from typing import List

from bokeh.io import show
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from pydantic import BaseModel

from roboregress.robot.statistics import StatsTracker


class RobotTable(BaseModel):
    cell_id: List[int]
    surface: List[str]
    robot_type: List[str]
    utilization_ratio: List[float]


def render_stats(stats: StatsTracker) -> None:
    """Generate and open a report in browser"""
    robot_centers = list(dict.fromkeys(r.robot_params.start_pos for r in stats.robot_stats))
    robot_centers.sort()

    robot_table = RobotTable(cell_id=[], utilization_ratio=[], surface=[], robot_type=[])
    for robot in stats.robot_stats:
        robot_table.robot_type.append(robot.name)
        robot_table.cell_id.append(robot_centers.index(robot.robot_params.start_pos))
        robot_table.utilization_ratio.append(round(robot.utilization_ratio * 100, 1))
        robot_table.surface.append(robot.robot_params.pickable_surface.value)

    robot_table = render_pydantic_table(robot_table)
    show(robot_table)


def render_pydantic_table(model: BaseModel) -> DataTable:
    columns = [
        TableColumn(field=attr_name, title=attr_name.title())
        for attr_name in model.__fields__.keys()
    ]
    column_data_source = ColumnDataSource(model.dict())
    table = DataTable(source=column_data_source, columns=columns, autosize_mode="fit_columns")
    return table
