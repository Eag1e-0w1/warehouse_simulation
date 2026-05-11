from datetime import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, model_validator, computed_field
import pandas as pd
import openpyxl

class Warehouse_params(BaseModel):
    model_config = ConfigDict(extra='ignore')

    schedule_str: str = Field(
        default='24/7', # Строка не валидируется! Допущение, что нет дробных чисел
        validation_alias='Время работы',
        description='Значение в виде строки из excel'
    )

    @computed_field
    @property
    def operation_hours_weekly(self) -> int:
        hours, days = map(int, self.schedule_str.split('/'))
        return hours * days

    rush_period: str = Field(
        default='20:00-05:00', # Строка не валидируется! Допущение, что шаг - час.
        validation_alias='Пик отгрузки',
        description='Значение в виде строки из excel (часы)'
    )

    @computed_field
    @property
    def rush_start_end(self) -> tuple:
        start, end = self.rush_period.split('-')
        start = dt.strptime(start, '%H:%M').hour
        end = dt.strptime(end, '%H:%M').hour
        return start, end

    shifts: int = Field(
        default=2,
        gt=0, le=4,
        validation_alias='Все зоны-Количество смен',
        description='Количество смен в сутки'
    )
    shift_duration: float = Field(
        default=12,
        gt=0, le=24,
        validation_alias='Все зоны-Продолжительность смены',
        description='Продолжительность смены'
    )
    square: int = Field(
        default=24_000,
        gt=0, le=100_000,
        validation_alias='Все зоны-Площадь склада',
        description='Площадь склада'
    )
    trucks_inbound: int = Field(
        default=50,
        gt=0, le=100,
        validation_alias='Зона приемки-Количество машин в приемке',
        description='Количество машин в приемке'
    )
    pallets_in_inbound_truck: int = Field(
        default=15,
        gt=0, le=50,
        validation_alias='Зона приемки-Количество паллет в машине',
        description='Количество паллет в машине'
    )
    pallets_inbound: int = Field(
        default=1_000,
        gt=0, le=10_000,
        validation_alias='Зона приемки-Количество паллет на приемке в сутки',
        description='Количество паллет на приемке в сутки'
    )
    order_picking_volume: int = Field(
        default=50_000,
        gt=0, le=500_000,
        validation_alias='Основная зона-Объем комплектации заказов',
        description='Объем комплектации заказов'
    )
    storage_volume: int = Field(
        default=15_000,
        gt=0, le=150_000,
        validation_alias='Основная зона-Объем хранения',
        description='Объем хранения'
    )
    trucks_outbound: int = Field(
        default=50,
        gt=0, le=500,
        validation_alias='Зона отгрузки-Количество машин к отгрузке',
        description='Количество машин к отгрузке'
    )
    pallets_in_outbound_truck: int = Field(
        default=12,
        gt=0, le=50,
        validation_alias='Зона отгрузки-Количество паллет в машине',
        description='Количество паллет в машине'
    )
    shipping_stores: int = Field(
        default=150,
        gt=0, le=1_500,
        validation_alias='Зона отгрузки-Количество магазинов отгрузки',
        description='Количество магазинов отгрузки'
    )
    real_work_time_staff: float = Field(
        default=11,
        gt=0, le=22, # Допущение - 1 час отдыха в 12 часов (грубо)
        validation_alias='Все зоны-Реальное рабочее время работника зоны приемки и отгрузки товаров в смене',
        description='рабочее время работника зоны приемки и отгрузки товаров в смене'
    )
    real_work_time_picker: float = Field(
        default=11,
        gt=0, le=22, # Допущение - 1 час отдыха в 12 часов (грубо)
        validation_alias='Все зоны-Реальное рабочее время комплектовщика в смене',
        description='рабочее время комплектовщика в смене'
    )
    real_work_time_driver: float = Field(
        default=11,
        gt=0, le=22, # Допущение - 1 час отдыха в 12 часов (грубо)
        validation_alias='Все зоны-Реальное рабочее время водителя ричтрака в смене',
        description='рабочее время водителя ричтрака в смене'
    )
    inbound_outbound_staff: int = Field(
        default=8,
        gt=0, le=80,
        validation_alias='Все зоны-Количество работников зон приемки и отгрузки товаров',
        description='Количество работников зон приемки и отгрузки товаров'
    )
    pickers: int = Field(
        default=40,
        gt=0, le=400,
        validation_alias='Все зоны-Количество комплектовщиков по всем зонам',
        description='Количество комплектовщиков по всем зонам'
    )
    drivers: int = Field(
        default=8,
        gt=0, le=80,
        validation_alias='Все зоны-Количество водителей ричтрака',
        description='Количество водителей ричтрака'
    )
    average_staff_salary: int = Field(
        default=100_000,
        gt=27_000, le=500_000, # Допущение - минимум приближен к МРОТ
        validation_alias='Все зоны-Средняя заработная плата работников зон приемки и отгрузки товаров',
        description='ФОТ работников зон приемки и отгрузки товаров'
    )
    average_pickers_salary: int = Field(
        default=100_000,
        gt=27_000, le=500_000, # Допущение - минимум приближен к МРОТ
        validation_alias='Все зоны-Средняя заработная плата отборщика',
        description = 'ФОТ отборщиков'
    )
    average_drivers_salary: int = Field(
        default=120_000,
        gt=27_000, le=600_000, # Допущение - минимум приближен к МРОТ
        validation_alias='Все зоны-Средняя заработная плата водителей ричтрака',
        description = 'ФОТ водителей ричтрака'
    )
    amr_num: int = Field(
        default=0,
        gt=0, le=1_000, # Не учитывает габариты и размеры склада
        validation_alias='Все зоны-Необходимое количество роботов для обслуживания заданного объема комплектации',
        description='Необходимое количество роботов для обслуживания заданного объема комплектации'
    )
    amr_payload: int = Field(
        default=1_500,
        gt=0, le=6_000,
        validation_alias='Все зоны-Грузоподъемность',
        description='Грузоподъемность робота'
    )
    amr_speed: float = Field(
        default=1.5,
        gt=0, le=5,
        validation_alias='Все зоны-Скорость перемещения',
        description='корость перемещения робота'
    )
    amr_battery_charge: float = Field(
        default=22,
        gt=0, le=72,
        validation_alias='Все зоны-Время работы',
        description='Время работы робота'
    )
    amr_cost: int = Field(
        default=1_500_000,
        gt=0, le=15_000_000,
        validation_alias='Все зоны-Стоимость',
        description='Стоимость робота'
    )
    productivity: float = Field(
        default=1.0,
        gt=0, le=2.0,
        validation_alias='Все зоны-Продуктивность',
        description='Продуктивность'
    )

    @model_validator(mode='after')
    def validate_24h_cycle(self):
        total_hours = self.shifts * self.shift_duration
        if total_hours != 24:
            raise ValueError(
                f'Некорректное количество часов в сутках: {self.shifts} * {self.shift_duration} = {total_hours} ч.'
                f'\nОжидается 24 часа'
            )
        return self

    @model_validator(mode='after')
    def validate_working_hours_staff(self):
        if self.shift_duration < self.real_work_time_staff: # здесь можно развить логику с отдыхом 1/12
            raise ValueError(
                f'Длительность смены = {self.shift_duration}, рабочее время сотрудника = {self.real_work_time_staff}'
                f'\nРеальное рабочее время сотрудника не может превышать длительность смены'
            )
        return self

    @model_validator(mode='after')
    def validate_working_hours_drivers(self):
        if self.shift_duration < self.real_work_time_driver: # здесь можно развить логику с отдыхом 1/12
            raise ValueError(
                f'Длительность смены = {self.shift_duration}, рабочее время сотрудника = {self.real_work_time_driver}'
                f'\nРеальное рабочее время сотрудника не может превышать длительность смены'
            )
        return self

def load_warehouse_params(path: str) -> Warehouse_params:
    """
     Загружает, нормализует и валидирует параметры склада из Excel-файла.

     Args:
         path: Путь к файлу Excel.

     Returns:
         Warehouse_params: Валидированная Pydantic-модель с параметрами конфигурации.
    """

    data = pd.read_excel(path)

    data.dropna(subset=['Зона склада',
                        'Параметр',
                        'Среднее значение по году'], inplace=True)
    data['Параметр'] = data['Зона склада'] + '-' + data['Параметр']
    data_dict = data.set_index('Параметр')['Среднее значение по году'].to_dict()
    return Warehouse_params(**data_dict)

