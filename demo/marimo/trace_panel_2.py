import marimo

__generated_with = "0.7.0"
app = marimo.App(width="normal")


@app.cell
def __(
    button_open_trace,
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
    mo.vstack([mo.vstack([trace_select, select_trace_attr]), mo.vstack([mo.hstack([trace_start, trace_stop, index_start, index_stop, sample_count, button_open_trace]), chart_detail_base]), chart_overview])
    return


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
    import nutcracker.solver.trace
    return alt, data, mo, np, nutcracker, os, pd, trace, zarr


@app.cell
def __(
    np,
    os,
    pd,
    set_data_count,
    set_downsample_data,
    set_index_start,
    set_index_stop,
    set_selected_data,
    set_selected_sample_count,
    set_selected_trace_count,
    set_selected_trace_data,
    set_trace_count,
    set_trace_start,
    set_trace_stop,
    trace,
    typing,
    zarr,
):
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

    def get_select_file_trace_attr(file_path):
        file_path = file_path[0].path
        if file_path.endswith('.npy'):
            data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
            set_selected_trace_count(trace_count)
            set_selected_sample_count(sample_count)
            set_selected_data(data)
            set_trace_count(trace_count)
            set_data_count(sample_count)
            set_selected_trace_data(traces_source)
            set_trace_start(0)
            set_trace_stop(1)
            set_index_start(0)
            set_index_stop(sample_count)
            set_downsample_data(pd.DataFrame({'index': [], 'traces': [], 'value': []}))
        elif file_path.endswith('.zgroup'):
            file_path = get_zarr_dir(file_path)
            if file_path:
                data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
                set_selected_trace_count(trace_count)
                set_selected_sample_count(sample_count)
                set_selected_data(data)
                set_trace_count(trace_count)
                set_data_count(sample_count)
                set_selected_trace_data(traces_source)
                set_trace_start(0)
                set_trace_stop(1)
                set_index_start(0)
                set_index_stop(sample_count)
                set_downsample_data(pd.DataFrame({'index': [], 'traces': [], 'value': []}))
        else:
            set_selected_trace_count(0)
            set_selected_sample_count(0)
            set_selected_data(None)
            set_trace_count(trace_count)
            set_data_count(sample_count)
            set_selected_trace_data(traces_source)
            set_trace_start(0)
            set_trace_stop(1)
            set_index_start(0)
            set_index_stop(sample_count)
            set_downsample_data(pd.DataFrame({'index': [], 'traces': [], 'value': []}))

    def get_zarr_dir(zgroup_file_path, depth=0):
        if depth > 3:
            return None
        depth += 1
        parent_path = os.path.dirname(zgroup_file_path)
        if parent_path.endswith('.zarr'):
            return parent_path
        else:
            return get_zarr_dir(parent_path, depth)
    return get_select_file_trace_attr, get_zarr_dir, load_traces


@app.cell
def __(mo, np, pd):
    # trace
    get_trace_count, set_trace_count = mo.state(0) 
    get_data_count, set_data_count = mo.state(0) 
    # trace control
    get_trace_start, set_trace_start = mo.state(0)
    get_trace_stop, set_trace_stop = mo.state(1)
    get_index_start, set_index_start = mo.state(0)
    get_index_stop, set_index_stop = mo.state(0)
    get_sample_count, set_sample_count = mo.state(1000)
    # trace display
    # get_trace_data, set_trace_data = mo.state(None)

    get_selected_trace_count, set_selected_trace_count = mo.state(0)
    get_selected_sample_count, set_selected_sample_count = mo.state(0)
    get_selected_data, set_selected_data = mo.state(0)
    get_selected_trace_data, set_selected_trace_data = mo.state(np.empty(0))

    get_downsample_data, set_downsample_data = mo.state(pd.DataFrame({'index': [], 'traces': [], 'value': []}))
    return (
        get_data_count,
        get_downsample_data,
        get_index_start,
        get_index_stop,
        get_sample_count,
        get_selected_data,
        get_selected_sample_count,
        get_selected_trace_count,
        get_selected_trace_data,
        get_trace_count,
        get_trace_start,
        get_trace_stop,
        set_data_count,
        set_downsample_data,
        set_index_start,
        set_index_stop,
        set_sample_count,
        set_selected_data,
        set_selected_sample_count,
        set_selected_trace_count,
        set_selected_trace_data,
        set_trace_count,
        set_trace_start,
        set_trace_stop,
    )


@app.cell
def __(
    get_data_count,
    get_selected_trace_data,
    get_trace_count,
    mo,
    pd,
    set_downsample_data,
    set_index_start,
    set_index_stop,
    set_sample_count,
    set_trace_start,
    set_trace_stop,
    trace,
):
    def open_trace_file(v):
        ts = get_selected_trace_data()
        if len(ts) == 0:
            trace_data = pd.DataFrame({'index': [], 'traces': [], 'value': []})
        else:
            trace_data, _ = trace.get_traces_df_from_ndarray(get_selected_trace_data(), trace_start.value, trace_stop.value, index_start.value, index_stop.value, sample_count.value)
        set_downsample_data(trace_data)

    trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_trace_count(), full_width=True, on_change=set_trace_start, debounce=True)
    trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_trace_count(), value=min(get_trace_count(), 1), full_width=True, on_change=set_trace_stop, debounce=True)
    index_start=mo.ui.number(label="Sample start", start=0, stop=get_data_count(), full_width=True, on_change=set_index_start, debounce=True)
    index_stop=mo.ui.number(label="Sample index stop", start=0, stop=get_data_count(), value=get_data_count(), full_width=True, on_change=set_index_stop, debounce=True)
    sample_count=mo.ui.number(label="Downsample count", start=0, stop=1000, value=1000, full_width=True, on_change=set_sample_count, debounce=True)
    button_open_trace = mo.ui.button(label='Open', on_click=open_trace_file)
    return (
        button_open_trace,
        index_start,
        index_stop,
        open_trace_file,
        sample_count,
        trace_start,
        trace_stop,
    )


@app.cell
def __(alt, get_downsample_data, mo, set_downsample_data):
    # chart overview
    interval_selection = alt.selection_interval(encodings=['x'])
    base = alt.Chart(get_downsample_data()).mark_line(size=1).encode(
        x = 'index:Q',
        y = 'value:Q',
        color = alt.Color('traces:N').legend(None)
    )
    print('overview run...')
    legend_select = alt.selection_point(fields=['traces'], bind='legend')

    chart_overview_base = base.properties(height=80).add_params(interval_selection)

    chart_overview_shadow = base.transform_filter(interval_selection).mark_line(size=1)

    chart_overview = mo.ui.altair_chart(chart_overview_base + chart_overview_shadow, chart_selection=False, legend_selection=False, on_change=set_downsample_data)
    return (
        base,
        chart_overview,
        chart_overview_base,
        chart_overview_shadow,
        interval_selection,
        legend_select,
    )


@app.cell
def __(
    alt,
    get_downsample_data,
    get_sample_count,
    get_selected_trace_data,
    get_trace_start,
    get_trace_stop,
    mo,
    pd,
    trace,
):
    # detail chart
    print('detail run...')
    indexes = get_downsample_data()['index']
    index_s = 0 if len(indexes) == 0 else indexes.iloc[0]
    index_e = 0 if len(indexes) == 0 else indexes.iloc[-1]
    traces_source = get_selected_trace_data()
    if len(traces_source) == 0:
        trace_data = pd.DataFrame({'index': [], 'traces': [], 'value': []})
    elif get_trace_stop() - get_trace_start() < 1:
        trace_data = pd.DataFrame({'index': [], 'traces': [], 'value': []})
    else:
        trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, get_trace_start(), get_trace_stop(), index_s, index_e, get_sample_count())

    chart_detail_base = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
        x = alt.X('index:Q', bandPosition=0),
        # x = 'index:Q',
        y = 'value:Q',
        color = 'traces:N'
    ), chart_selection=False)
    return (
        chart_detail_base,
        index_e,
        index_s,
        indexes,
        trace_data,
        traces_source,
    )


@app.cell
def __(get_select_file_trace_attr, mo):
    trace_select = mo.ui.file_browser(multiple=False, on_change=get_select_file_trace_attr)
    return trace_select,


@app.cell
def __(get_selected_sample_count, get_selected_trace_count, mo):
    select_trace_attr = mo.md(f'''
    Trace count: {get_selected_trace_count()}   Sample count: {get_selected_sample_count()}
    ''')
    return select_trace_attr,


@app.cell
def __():
    # mo.vstack([mo.vstack([trace_select, select_trace_attr]), mo.vstack([mo.hstack([trace_start, trace_stop, index_start, index_stop, sample_count, button_open_trace]), chart_detail_base]), chart_overview])
    return


@app.cell
def __():
    # chart_selected()
    return


if __name__ == "__main__":
    app.run()
