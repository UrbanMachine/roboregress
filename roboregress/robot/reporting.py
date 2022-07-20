from typing import List

from bokeh.io import show
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from pydantic import BaseModel, Field

from roboregress.robot.statistics import StatsTracker


class RobotTable(BaseModel):
    cell_id: List[int] = Field(default_factory=list)
    surface: List[str] = Field(default_factory=list)
    robot_type: List[str] = Field(default_factory=list)
    utilization_ratio: List[float] = Field(default_factory=list)
    n_picked_fasteners: List[int] = Field(default_factory=list)


class HighLevelTable(BaseModel):
    total_time: List[float] = Field(default_factory=list)
    throughput_feet_per_day: List[float] = Field(default_factory=list)
    board_feet_per_day_2x12: List[float] = Field(default_factory=list)
    total_fasteners: List[int] = Field(default_factory=list)
    missed_fasteners: List[int] = Field(default_factory=list)
    processed_feet: List[float] = Field(default_factory=list)


def render_stats(stats: StatsTracker) -> None:
    """Generate and open a report in browser"""

    # Gather the per-robot statistics
    robot_table = RobotTable()
    for cell_id, rob_stat in stats.robots_by_cell:
        robot_table.cell_id.append(cell_id)
        robot_table.robot_type.append(rob_stat.name)
        robot_table.utilization_ratio.append(round(rob_stat.utilization_ratio * 100, 1))
        robot_table.n_picked_fasteners.append(rob_stat.n_picked_fasteners)
        robot_table.surface.append(rob_stat.robot_params.pickable_surface.value)

    # Gather the overall robot assembly statistics
    assert (
        sum(r.n_picked_fasteners for r in stats.robot_stats) == stats.total_picked_fasteners
    ), "The pick count numbers should be consistent! There is a bug somewhere."
    overall_table = HighLevelTable()
    overall_table.total_time.append(round(stats.total_time))
    overall_table.total_fasteners.append(stats.total_picked_fasteners)
    overall_table.processed_feet.append(round(stats.total_feet_processed))
    overall_table.missed_fasteners.append(stats.missed_fasteners)

    daily_throughput_feet = stats.throughput_feet * 60 * 60 * 24
    overall_table.board_feet_per_day_2x12.append(round((daily_throughput_feet * ((2 * 12) / 12))))
    overall_table.throughput_feet_per_day.append(round(daily_throughput_feet))

    robot_table_plot = render_pydantic_table(robot_table)
    overall_table_plot = render_pydantic_table(overall_table)

    show(layout([robot_table_plot, overall_table_plot], sizing_mode="stretch_both"))


def render_pydantic_table(model: BaseModel) -> DataTable:
    columns = [
        TableColumn(field=attr_name, title=attr_name.replace("_", " ").title())
        for attr_name in model.__fields__.keys()
    ]
    column_data_source = ColumnDataSource(model.dict())
    table = DataTable(source=column_data_source, columns=columns)
    return table
