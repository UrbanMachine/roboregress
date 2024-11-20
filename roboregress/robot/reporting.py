from collections.abc import Mapping
from pathlib import Path

from bokeh.io import curdoc, output_file, show
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource, Div
from bokeh.models.widgets import DataTable, TableColumn
from pydantic import BaseModel, Field

from roboregress.robot.statistics import StatsTracker

_CODE_BLOCK_STYLE = {
    "font-family": "Monaco, monospace",
    "display": "block",
    "background-color": "#eee",
    "white-space": "pre",
    "-webkit-overflow-scrolling": "touch",
    "overflow-x": "scroll",
    "max-width": "100%",
    "min-width": "100%",
    "padding": "0.2em",
}


class RobotTable(BaseModel):
    cell_id: list[int] = Field(default_factory=list)
    surface: list[str] = Field(default_factory=list)
    robot_type: list[str] = Field(default_factory=list)
    work_time_ratio: list[float] = Field(default_factory=list)
    wood_wait_ratio: list[float] = Field(default_factory=list)
    n_picked_fasteners: list[int] = Field(default_factory=list)


class HighLevelTable(BaseModel):
    total_time: list[float] = Field(default_factory=list)
    throughput_feet_per_8_hrs: list[float] = Field(default_factory=list)
    board_feet_per_8_hrs_2x12: list[float] = Field(default_factory=list)
    total_fasteners: list[int] = Field(default_factory=list)
    processed_feet: list[float] = Field(default_factory=list)


def render_stats(stats: StatsTracker, save_to: Path, config_file: Path) -> None:
    """Generate and open a report in browser"""

    # Gather the per-robot statistics
    robot_table = RobotTable()
    for cell_id, rob_stat in stats.robots_by_cell:
        robot_table.cell_id.append(cell_id)
        robot_table.robot_type.append(rob_stat.name)
        robot_table.work_time_ratio.append(
            round(rob_stat.work_timer.utilization_ratio * 100, 1)
        )
        robot_table.wood_wait_ratio.append(
            round(rob_stat.waiting_for_wood_timer.utilization_ratio * 100, 1)
        )
        robot_table.n_picked_fasteners.append(rob_stat.n_picked_fasteners)
        robot_table.surface.append(rob_stat.robot_params.pickable_surface.value)

    # Gather the overall robot assembly statistics
    assert (
        sum(r.n_picked_fasteners for r in stats.robot_stats)
        == stats.wood.total_picked_fasteners
    ), "The pick count numbers should be consistent! There is a bug somewhere."
    overall_table = HighLevelTable()
    overall_table.total_time.append(round(stats.total_time))
    overall_table.total_fasteners.append(stats.wood.total_picked_fasteners)
    overall_table.processed_feet.append(round(stats.wood.total_feet_processed))

    daily_throughput_feet = stats.wood.throughput_feet * 60 * 60 * 8
    overall_table.board_feet_per_8_hrs_2x12.append(
        round(daily_throughput_feet * ((2 * 12) / 12))
    )
    overall_table.throughput_feet_per_8_hrs.append(round(daily_throughput_feet))

    # Create the output plots
    output_file(save_to, title=save_to.stem.title().replace("_", " "))
    robot_table_plot = render_pydantic_table(robot_table)
    overall_table_plot = render_pydantic_table(overall_table)
    missed_fasteners_plot = render_dict_table(stats.missed_fasteners)
    input_yaml = Div(
        text=config_file.read_text(), render_as_text=False, style=_CODE_BLOCK_STYLE
    )

    final = layout(
        [[robot_table_plot, [overall_table_plot, missed_fasteners_plot]], [input_yaml]],
        sizing_mode="stretch_both",
    )
    curdoc().theme = "dark_minimal"
    show(final)


def render_dict_table(data: Mapping[str, int | list[int]]) -> DataTable:
    # Accept single values as well as lists of values
    data = {
        title: val if isinstance(val, list) else [val] for title, val in data.items()
    }

    columns = [
        TableColumn(field=attr_name, title=attr_name.replace("_", " ").title())
        for attr_name in data
    ]
    column_data_source = ColumnDataSource(data)
    table = DataTable(source=column_data_source, columns=columns)
    return table


def render_pydantic_table(model: BaseModel) -> DataTable:
    data = {attr_name: getattr(model, attr_name) for attr_name in model.__fields__}
    return render_dict_table(data)
