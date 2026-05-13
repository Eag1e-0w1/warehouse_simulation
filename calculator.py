from math import ceil
from statistics import mean
import pandas as pd
from models import Warehouse_params
import config
from apis import get_credit_rate


class Calculator:
    """
    Модуль расчета метрик и финансовой оценки складского процесса.
    Принимает результаты почасовой симуляции и входные параметры,
    возвращает операционные (OPEX), инвестиционные (CAPEX) показатели,
    метрики производительности и минимальную требуемую доходность проекта.
    """
    def calculate(self,
                  params: Warehouse_params,
                  data: pd.DataFrame,
                  conf=config) -> dict:
        """
        Вычисляет базовые метрики и финансовые показатели для одного сценария.

        Args:
            params: Конфигурация склада.
            data: DataFrame с результатами симуляции.
            conf: Глобальные настройки (SIMULATION_DAYS).

        Returns:
            dict: Словарь метрик:
                - 'opex': Затраты на персонал за период симуляции (руб.)
                - 'capex': Стоимость закупки парка роботов (руб.)
                - 'avg_delayed_orders': Среднее кол-во  заказов (шт.)
                - 'max_delayed_orders': Максимальное кол-во задержанных заказов (шт.)
                - 'avg_picks_per_hour': Ср. скорость одного комплектовщика (пиков/час)
                - 'time_per_pick': Ср. время отбора одного пика (сек.)
                - 'throughout': Ср. суточная пропускная способность (пиков/день)
        """
        metrics = {}

        # OPEX
        opex = (
                (params.average_staff_salary * params.inbound_outbound_staff) +
                (params.average_drivers_salary * params.drivers) +
                (params.average_pickers_salary * params.pickers)) / 30 * conf.SIMULATION_DAYS
        metrics['opex'] = opex

        # CAPEX
        capex = params.amr_cost * params.amr_num
        metrics['capex'] = capex

        # Среднее количество задержанных заказов
        peaks_per_order = ceil(params.order_picking_volume / params.shipping_stores)
        avg_delayed_orders = ceil(mean(data['queue'] / peaks_per_order))
        metrics['avg_delayed_orders'] = avg_delayed_orders

        # Максимальное количество задержанных заказов
        max_delayed_orders = ceil(data['queue'].max() / peaks_per_order)
        metrics['max_delayed_orders'] = max_delayed_orders

        # Среднее количество пиков в час
        avg_picks_per_hour = mean(data['full_capacity'] / params.pickers)
        metrics['avg_picks_per_hour'] = avg_picks_per_hour

        # Скорость одного пика
        time_per_pick = 3600 / avg_picks_per_hour
        metrics['time_per_pick'] = time_per_pick

        # Пропускная способность
        throughout = data['full_capacity'].mean() * 24
        metrics['throughout'] = throughout

        return metrics

    def compute_min_monthly_profit(self,
                                   data: pd.DataFrame,
                                   conf=config) -> float:
        """
        Рассчитывает минимальную месячную прибыль, необходимую для
        окупаемости проекта.

        Args:
            data: DataFrame с рассчитанными эффектами.
            conf: Конфигурация проекта (используется для перевода дней в годы).

        Returns:
            float: Минимальная требуемая месячная прибыль (руб.) с учётом
                   текущей кредитной ставки и сложного процента.
        """
        rate = get_credit_rate()
        effect = data.loc['capex']['effect'] + data.loc['opex']['effect']
        years = conf.SIMULATION_DAYS / 365
        bank_growth = (1 + rate) ** years
        total_bank_profit = effect * (bank_growth - 1)
        min_monthly_profit = total_bank_profit / years / 12

        return min_monthly_profit