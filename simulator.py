import pandas as pd

from models import Warehouse_params
from math import floor
import config


class Warehouse:

    def run(self,
            params: Warehouse_params,
            conf=config):

        hours = conf.SIMULATION_DAYS * 24
        rush_hours = set()
        history = []
        queue = 0

        num_pickers = params.pickers
        picker_speed_per_hour = floor(params.order_picking_volume /
                                      (params.pickers *
                                       params.real_work_time_picker *
                                       params.shifts))
        picker_capacity = floor(picker_speed_per_hour * num_pickers)
        full_capacity = int(picker_capacity * params.productivity)
        demand_per_day = params.order_picking_volume

        rush_start, rush_end = params.rush_start_end
        if rush_start > rush_end:
            rush_hours.update(range(rush_start, 24))
            rush_hours.update(range(0, rush_end))
        else:
            rush_hours.update(range(rush_start, rush_end))

        for hour in range(hours):
            # Определение - пиковый час или обычный
            day_hour = hour % 24
            is_rush = (day_hour >= rush_start) or (day_hour < rush_end)

            # Развесовка
            peak_weight = conf.PEAK_RATIO if is_rush else 1.0
            total_weight = len(rush_hours) * conf.PEAK_RATIO + (24 - len(rush_hours))
            X = peak_weight / total_weight

            inbound = floor(demand_per_day * X)
            demand = inbound + queue
            completed = min(full_capacity, demand)
            queue = demand - completed

            history.append([inbound, demand, full_capacity, completed, queue])

        columns = ['inbound', 'demand', 'full_capacity', 'completed', 'queue']
        data = pd.DataFrame(data=history, columns=columns)

        return data
