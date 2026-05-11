from math import ceil
from statistics import mean
import pandas as pd
from models import Warehouse_params
import config
from apis import get_credit_rate

class Calculator:

    def calculate(self,
                  params: Warehouse_params,
                  data: pd.DataFrame,
                  conf=config) -> dict:

        metrics = {}

        opex = (
                (params.average_staff_salary * params.inbound_outbound_staff) +
                (params.average_drivers_salary * params.drivers) +
                (params.average_pickers_salary * params.pickers)) / 30 * conf.SIMULATION_DAYS
        metrics['opex'] = opex

        capex = params.amr_cost * params.amr_num
        metrics['capex'] = capex

        peaks_per_order = ceil(params.order_picking_volume / params.shipping_stores)
        avg_delayed_orders = ceil(mean(data['queue'] / peaks_per_order))
        metrics['avg_delayed_orders'] = avg_delayed_orders

        max_delayed_orders = ceil(data['queue'].max() / peaks_per_order)
        metrics['max_delayed_orders'] = max_delayed_orders

        avg_picks_per_hour = mean(data['full_capacity'] / params.pickers)
        metrics['avg_picks_per_hour'] = avg_picks_per_hour

        time_per_pick = 3600 / avg_picks_per_hour
        metrics['time_per_pick'] = time_per_pick


        throughout = data['full_capacity'].mean() * 24
        metrics['throughout'] = throughout

        return metrics

    def compute_min_monthly_profit(self,
                                   data: pd.DataFrame,
                                   conf=config):
        rate = get_credit_rate()
        effect = data.loc['capex']['effect'] + data.loc['opex']['effect']
        years = conf.SIMULATION_DAYS / 365
        bank_growth = (1 + rate) ** years
        total_bank_profit = effect * (bank_growth - 1)
        min_monthly_profit = total_bank_profit / years / 12

        return min_monthly_profit