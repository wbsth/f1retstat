from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, PanTool, BoxZoomTool, WheelZoomTool, ResetTool, SaveTool
from bokeh.io import export_png
from scipy.signal import savgol_filter
from misc import build_dataframe, fill_dataframe, import_race_statuses, build_season_list
import pandas as pd

statuses = import_race_statuses('finish_status.csv')
season_years = build_season_list('seasons.json')

df = build_dataframe()

final_df = fill_dataframe(df, season_years, statuses)
final_df['date'] = pd.to_datetime(final_df['date'], yearfirst=True)
final_df['ret_ov_perc'] = (final_df['retired_overall'] / final_df['started']) * 100
final_df['ret_mech_perc'] = (final_df['retired_mech'] / final_df['started']) * 100
final_df['ret_acc_perc'] = (final_df['retired_accident'] / final_df['started']) * 100
final_df['ma_ov'] = savgol_filter(final_df['ret_ov_perc'], 71, 3)
final_df['ma_mech'] = savgol_filter(final_df['ret_mech_perc'], 71, 3)
final_df['ma_acc'] = savgol_filter(final_df['ret_acc_perc'], 71, 3)

source = ColumnDataSource(final_df)

# plotting
for i in ['ov', 'mech', 'acc']:
    full_names = {
        'ov': 'Overall',
        'mech': 'Mechanical',
        'acc': 'Accidents'
    }

    # plot tools
    hover = HoverTool(tooltips=[
        ("GP", "@year @country"),
        ("Started", "@started"),
        ("Retired overall", '@retired_overall'),
        ("Mechanical", '@retired_mech'),
        ("Accident", '@retired_accident'),
        ("Misc", '@retired_misc'),
    ])

    tools = [PanTool(),
             BoxZoomTool(),
             WheelZoomTool(),
             ResetTool(),
             SaveTool(),
             hover]

    p = figure(title=f"Retirement percentage, {full_names[i]}", x_axis_label='Date',
               y_axis_label='Retirement percentage[%]',
               plot_width=1280, plot_height=720, x_axis_type='datetime', tools=tools)
    p.circle('date', f'ret_{i}_perc', size=5, source=source, fill_color='#b5d3ff', line_color='#569afc')
    p.line('date', f'ma_{i}', source=source, line_width=3)
    p.sizing_mode = 'scale_both'
    export_png(p, filename=f"{i}.png")
