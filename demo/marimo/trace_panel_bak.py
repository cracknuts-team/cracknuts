import marimo

__generated_with = "0.7.8"
app = marimo.App(width="normal")


@app.cell
def __():
    import marimo as mo
    from nutcracker.solver import trace
    import altair as alt
    from vega_datasets import data
    import numpy as np
    import pandas as pd
    import zarr
    import os
    return alt, data, mo, np, os, pd, trace, zarr


@app.cell
def __(mo):
    # trace
    get_trace_count, set_trace_count = mo.state(0) 
    get_data_count, set_data_count = mo.state(0) 
    # trace control
    get_trace_start, set_trace_start = mo.state(0)
    get_trace_stop, set_trace_stop = mo.state(0)
    get_index_start, set_index_start = mo.state(0)
    get_index_stop, set_index_stop = mo.state(0)
    get_sample_count, set_sample_count = mo.state(0)
    # trace display
    get_trace_data, set_trace_data = mo.state(None)
    return (
        get_data_count,
        get_index_start,
        get_index_stop,
        get_sample_count,
        get_trace_count,
        get_trace_data,
        get_trace_start,
        get_trace_stop,
        set_data_count,
        set_index_start,
        set_index_stop,
        set_sample_count,
        set_trace_count,
        set_trace_data,
        set_trace_start,
        set_trace_stop,
    )


@app.cell
def __(
    get_data_count,
    get_trace_count,
    mo,
    set_index_start,
    set_index_stop,
    set_sample_count,
    set_trace_start,
    set_trace_stop,
):
    trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_trace_count(), full_width=True, on_change=set_trace_start)
    trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_trace_count(), value=min(get_trace_count(), 10), full_width=True, on_change=set_trace_stop)
    index_start=mo.ui.number(label="Data index start", start=0, stop=get_data_count(), full_width=True, on_change=set_index_start)
    index_stop=mo.ui.number(label="Data index stop", start=0, stop=get_data_count(), value=get_data_count(), full_width=True, on_change=set_index_stop)
    sample_count=mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count)
    return index_start, index_stop, sample_count, trace_start, trace_stop


@app.cell
def __(np, os, pd, typing, zarr):
    def load_traces(path: str, trace_count_setter: callable = None, data_count_setter: callable=None) -> typing.Tuple[str, pd.DataFrame, int, int]:
        if os.path.isdir(path):
            # load scarr data from zarr format file.
            traces_source = zarr.open(path, "r")['0/0/traces']
            trace_count = traces_source.shape[0]
            data_count = traces_source.shape[1]
            data_type = 'zarr'
        else:
            # load newae data from npy format file.
            traces_source = np.load(path)
            trace_count = traces_source.shape[0]
            data_count = traces_source.shape[1]
            data_type = 'npy'

        if trace_count_setter:
            trace_count_setter(trace_count)
        if data_count_setter:
            data_count_setter(data_count)
        return data_type, traces_source, trace_count, data_count
    return load_traces,


@app.cell
def __(load_traces, set_data_count, set_trace_count):
    # data_type, traces_source, trace_count, data_count = load_traces('../data/traces.npy', set_trace_count, set_data_count)
    data_type, traces_source, trace_count, data_count = load_traces('../data/aes_cp_3.zarr', set_trace_count, set_data_count)
    return data_count, data_type, trace_count, traces_source


@app.cell
def __(
    alt,
    index_start,
    index_stop,
    mo,
    sample_count,
    set_trace_data,
    trace,
    trace_start,
    trace_stop,
    traces_source,
):
    # trace_panel = None
    # chart_overview = None
    # chart_detail = None




    # if trace_start.value is not None and trace_stop.value is not None and index_start.value is not None and index_stop.value and sample_count.value is not None:

    traces, indexs = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_start.value, index_stop.value, sample_count.value)

    # chart_detail_base =  mo.ui.altair_chart(alt.Chart(traces).mark_line(size=1, opacity=0.3).encode(
    #     x = 'index:Q',
    #     y = 'value:Q',
    #     color = 'traces:N'
    # ), chart_selection=False)

    set_trace_data(traces)

    # def update_detail(trace_df):
    #     index_s = min(get_trace_data()['index'])
    #     index_e = max(get_trace_data()['index'])
    #     set_trace_data(trace_df)
    #     trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)
    #     chart_detail_base =  mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
    #         x = alt.X('index:Q', bandPosition=0),
    #         # x = 'index:Q',
    #         y = 'value:Q',
    #         color = 'traces:N'
    #     ), chart_selection=False)
    #     chart_detail_base.display()

    interval_selection = alt.selection_interval(encodings=['x'])
    base = alt.Chart(traces).mark_line(size=1).encode(
        x = 'index:Q',
        y = 'value:Q',
        color = alt.Color('traces:N').legend(None)
    )

    legend_select = alt.selection_point(fields=['traces'], bind='legend')

    # print(type(get_trace_data()))
    # chart_detail_base = alt.Chart(get_trace_data()).mark_line()

    chart_overview_base = base.properties(height=80).add_params(interval_selection)

    chart_overview_shadow = base.transform_filter(interval_selection).mark_line(size=1)

    chart_overview = mo.ui.altair_chart(chart_overview_base + chart_overview_shadow, chart_selection=False, legend_selection=False, on_change=set_trace_data)

    # pointerover = alt.selection_point(nearest=True, on="pointerover", clear='pointerout', fields=["index"], empty=False)

    # chart_detail_rules = alt.Chart(traces).transform_pivot(
    #     "traces",
    #     value="value",
    #     groupby=["index"]
    # ).mark_rule(color="red", size=2).encode(
    #     x=alt.X('index:Q').scale(domain=interval_selection),
    #     opacity=alt.condition(pointerover, alt.value(0.3), alt.value(0)),
    #     tooltip=[alt.Tooltip(str(t), type="quantitative") for t in indexs]
    # ).add_params(pointerover)

    # chart_detail = alt.layer(chart_detail_base, chart_detail_rules).properties(width=800)

    # trace_panel = mo.vstack([chart_detail_base, chart_overview])

    # detail_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)

    # chart_detail_base = mo.ui.altair_chart(alt.Chart(traces).mark_line(size=1).encode(
    #     x = alt.X('index:Q', bandPosition=0),
    #     # x = 'index:Q',
    #     y = 'value:Q',
    #     color = 'traces:N'
    # ), chart_selection=False)

    # mo.vstack([chart_overview])
    return (
        base,
        chart_overview,
        chart_overview_base,
        chart_overview_shadow,
        indexs,
        interval_selection,
        legend_select,
        traces,
    )


@app.cell
def __(
    alt,
    get_trace_data,
    mo,
    sample_count,
    trace,
    trace_start,
    trace_stop,
    traces_source,
):
    # chart_detail_base = alt.Chart(traces, width=800).mark_line(size=1, opacity=0.3).encode(
    #     x = 'index:Q',
    #     y = 'value:Q',
    #     color = 'traces:N'
    # )

    index_s = min(get_trace_data()['index'])
    index_e = max(get_trace_data()['index'])

    trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)

    chart_detail_base = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
        x = alt.X('index:Q', bandPosition=0),
        # x = 'index:Q',
        y = 'value:Q',
        color = 'traces:N'
    ), chart_selection=False)

    # print(min(get_trace_data()['index']), max(get_trace_data()['index']))

    # chart_detail_base
    return chart_detail_base, index_e, index_s, trace_data


@app.cell
def __():
    # mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count])
    return


@app.cell
def __(get_selected_sample_count, get_selected_trace_count, mo):
    select_trace_attr = mo.md(f'''
    Trace count: {get_selected_trace_count()}   Sample count: {get_selected_sample_count()}
    ''')
    return select_trace_attr,


@app.cell
def __(mo, os, trace):
    import nutcracker.solver.trace

    get_selected_trace_count, set_selected_trace_count = mo.state(0)
    get_selected_sample_count, set_selected_sample_count = mo.state(0)
    get_selected_data, set_selected_data = mo.state(0)

    def get_select_file_trace_attr(file_path):
        file_path = file_path[0].path
        if file_path.endswith('.npy'):
            data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
            set_selected_trace_count(trace_count)
            set_selected_sample_count(sample_count)
            set_selected_data(data)
        elif file_path.endswith('.zgroup'):
            file_path = get_zarr_dir(file_path)
            if file_path:
                data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
                set_selected_trace_count(trace_count)
                set_selected_sample_count(sample_count)
                set_selected_data(data)
        else:
            set_selected_trace_count(0)
            set_selected_sample_count(0)
            set_selected_data(None)

    def get_zarr_dir(zgroup_file_path, depth=0):
        if depth > 3:
            return None
        depth += 1
        parent_path = os.path.dirname(zgroup_file_path)
        if parent_path.endswith('.zarr'):
            return parent_path
        else:
            return get_zarr_dir(parent_path, depth)


    trace_select = mo.ui.file_browser(multiple=False, on_change=get_select_file_trace_attr)
    return (
        get_select_file_trace_attr,
        get_selected_data,
        get_selected_sample_count,
        get_selected_trace_count,
        get_zarr_dir,
        nutcracker,
        set_selected_data,
        set_selected_sample_count,
        set_selected_trace_count,
        trace_select,
    )


@app.cell
def __():
    # mo.vstack([trace_select, select_trace_attr])
    return


@app.cell
def __(
    chart_detail_base,
    chart_overview,
    index_start,
    index_stop,
    mo,
    sample_count,
    select_trace_attr,
    trace_select,
    trace_start,
    trace_stop,
):
    mo.vstack([mo.vstack([trace_select, select_trace_attr]), chart_overview, mo.hstack([mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count]), chart_detail_base], justify='space-around')])
    return


if __name__ == "__main__":
    app.run()
