import marimo

__generated_with = "0.7.8"
app = marimo.App(width="medium")


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
def __():
    # # trace
    # get_trace_count, set_trace_count = mo.state(0) 
    # get_data_count, set_data_count = mo.state(0) 
    # # trace control
    # get_trace_start, set_trace_start = mo.state(0)
    # get_trace_stop, set_trace_stop = mo.state(0)
    # get_index_start, set_index_start = mo.state(0)
    # get_index_stop, set_index_stop = mo.state(0)
    # get_sample_count, set_sample_count = mo.state(0)
    # # trace display
    # get_trace_data, set_trace_data = mo.state(None)
    return


@app.cell
def __():
    # trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_trace_count(), full_width=True, on_change=set_trace_start)
    # trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_trace_count(), value=min(get_trace_count(), 10), full_width=True, on_change=set_trace_stop)
    # index_start=mo.ui.number(label="Data index start", start=0, stop=get_data_count(), full_width=True, on_change=set_index_start)
    # index_stop=mo.ui.number(label="Data index stop", start=0, stop=get_data_count(), value=get_data_count(), full_width=True, on_change=set_index_stop)
    # sample_count=mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count)
    return


@app.cell
def __():
    # def load_traces(path: str, trace_count_setter: callable = None, data_count_setter: callable=None) -> typing.Tuple[str, pd.DataFrame, int, int]:
    #     if os.path.isdir(path):
    #         # load scarr data from zarr format file.
    #         traces_source = zarr.open(path, "r")['0/0/traces']
    #         trace_count = traces_source.shape[0]
    #         data_count = traces_source.shape[1]
    #         data_type = 'zarr'
    #     else:
    #         # load newae data from npy format file.
    #         traces_source = np.load(path)
    #         trace_count = traces_source.shape[0]
    #         data_count = traces_source.shape[1]
    #         data_type = 'npy'

    #     if trace_count_setter:
    #         trace_count_setter(trace_count)
    #     if data_count_setter:
    #         data_count_setter(data_count)
    #     return data_type, traces_source, trace_count, data_count
    return


@app.cell
def __():
    # data_type, traces_source, trace_count, data_count = load_traces('../data/traces.npy', set_trace_count, set_data_count)
    # data_type, traces_source, trace_count, data_count = load_traces('../data/aes_cp_3.zarr', set_trace_count, set_data_count)
    return


@app.cell
def __():
    # # trace_panel = None
    # # chart_overview = None
    # # chart_detail = None




    # # if trace_start.value is not None and trace_stop.value is not None and index_start.value is not None and index_stop.value and sample_count.value is not None:

    # traces, indexs = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_start.value, index_stop.value, sample_count.value)

    # # chart_detail_base =  mo.ui.altair_chart(alt.Chart(traces).mark_line(size=1, opacity=0.3).encode(
    # #     x = 'index:Q',
    # #     y = 'value:Q',
    # #     color = 'traces:N'
    # # ), chart_selection=False)

    # set_trace_data(traces)

    # # def update_detail(trace_df):
    # #     index_s = min(get_trace_data()['index'])
    # #     index_e = max(get_trace_data()['index'])
    # #     set_trace_data(trace_df)
    # #     trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)
    # #     chart_detail_base =  mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
    # #         x = alt.X('index:Q', bandPosition=0),
    # #         # x = 'index:Q',
    # #         y = 'value:Q',
    # #         color = 'traces:N'
    # #     ), chart_selection=False)
    # #     chart_detail_base.display()

    # interval_selection = alt.selection_interval(encodings=['x'])
    # base = alt.Chart(traces).mark_line(size=1).encode(
    #     x = 'index:Q',
    #     y = 'value:Q',
    #     color = alt.Color('traces:N').legend(None)
    # )

    # legend_select = alt.selection_point(fields=['traces'], bind='legend')

    # # print(type(get_trace_data()))
    # # chart_detail_base = alt.Chart(get_trace_data()).mark_line()

    # chart_overview_base = base.properties(height=80).add_params(interval_selection)

    # chart_overview_shadow = base.transform_filter(interval_selection).mark_line(size=1)

    # chart_overview = mo.ui.altair_chart(chart_overview_base + chart_overview_shadow, chart_selection=False, legend_selection=False, on_change=set_trace_data)

    # # pointerover = alt.selection_point(nearest=True, on="pointerover", clear='pointerout', fields=["index"], empty=False)

    # # chart_detail_rules = alt.Chart(traces).transform_pivot(
    # #     "traces",
    # #     value="value",
    # #     groupby=["index"]
    # # ).mark_rule(color="red", size=2).encode(
    # #     x=alt.X('index:Q').scale(domain=interval_selection),
    # #     opacity=alt.condition(pointerover, alt.value(0.3), alt.value(0)),
    # #     tooltip=[alt.Tooltip(str(t), type="quantitative") for t in indexs]
    # # ).add_params(pointerover)

    # # chart_detail = alt.layer(chart_detail_base, chart_detail_rules).properties(width=800)

    # # trace_panel = mo.vstack([chart_detail_base, chart_overview])

    # # detail_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)

    # # chart_detail_base = mo.ui.altair_chart(alt.Chart(traces).mark_line(size=1).encode(
    # #     x = alt.X('index:Q', bandPosition=0),
    # #     # x = 'index:Q',
    # #     y = 'value:Q',
    # #     color = 'traces:N'
    # # ), chart_selection=False)

    # # mo.vstack([chart_overview])
    return


@app.cell
def __():
    # # chart_detail_base = alt.Chart(traces, width=800).mark_line(size=1, opacity=0.3).encode(
    # #     x = 'index:Q',
    # #     y = 'value:Q',
    # #     color = 'traces:N'
    # # )

    # index_s = min(get_trace_data()['index'])
    # index_e = max(get_trace_data()['index'])

    # trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)

    # chart_detail_base = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
    #     x = alt.X('index:Q', bandPosition=0),
    #     # x = 'index:Q',
    #     y = 'value:Q',
    #     color = 'traces:N'
    # ), chart_selection=False)

    # # print(min(get_trace_data()['index']), max(get_trace_data()['index']))

    # # chart_detail_base
    return


@app.cell
def __():
    # mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count])
    return


@app.cell
def __():
    # select_trace_attr = mo.md(f'''
    # Trace count: {get_selected_trace_count()}   Sample count: {get_selected_sample_count()}
    # Data: 
    # {button_open_trace}
    # ''')
    return


@app.cell
def __(mo, np, pd):
    # trace control
    get_trace_start, set_trace_start = mo.state(0)
    get_trace_stop, set_trace_stop = mo.state(0)
    get_index_start, set_index_start = mo.state(0)
    get_index_stop, set_index_stop = mo.state(0)
    get_sample_count, set_sample_count = mo.state(0)
    # trace filter
    get_trace_data, set_trace_data = mo.state(None)

    # trace file info
    get_selected_trace_count, set_selected_trace_count = mo.state(0)
    get_selected_sample_count, set_selected_sample_count = mo.state(0)
    get_selected_data, set_selected_data = mo.state(None)
    get_selected_trace_data, set_selected_trace_data = mo.state(np.empty(0))

    # trace downsample data
    get_downsample_data, set_downsample_data = mo.state((pd.DataFrame({'index': [], 'traces': [], 'value': []}), []))
    return (
        get_downsample_data,
        get_index_start,
        get_index_stop,
        get_sample_count,
        get_selected_data,
        get_selected_sample_count,
        get_selected_trace_count,
        get_selected_trace_data,
        get_trace_data,
        get_trace_start,
        get_trace_stop,
        set_downsample_data,
        set_index_start,
        set_index_stop,
        set_sample_count,
        set_selected_data,
        set_selected_sample_count,
        set_selected_trace_count,
        set_selected_trace_data,
        set_trace_data,
        set_trace_start,
        set_trace_stop,
    )


@app.cell
def __(
    alt,
    get_downsample_data,
    get_selected_sample_count,
    get_selected_trace_count,
    get_selected_trace_data,
    mo,
    np,
    os,
    pd,
    set_index_start,
    set_index_stop,
    set_sample_count,
    set_selected_data,
    set_selected_sample_count,
    set_selected_trace_count,
    set_selected_trace_data,
    set_trace_data,
    set_trace_start,
    set_trace_stop,
    trace,
    typing,
    zarr,
):
    import nutcracker.solver.trace

    # trace
    # get_trace_count, set_trace_count = mo.state(0) 
    # get_data_count, set_data_count = mo.state(0) 
    # # trace control
    # get_trace_start, set_trace_start = mo.state(0)
    # get_trace_stop, set_trace_stop = mo.state(0)
    # get_index_start, set_index_start = mo.state(0)
    # get_index_stop, set_index_stop = mo.state(0)
    # get_sample_count, set_sample_count = mo.state(0)
    # # trace filter
    # get_trace_data, set_trace_data = mo.state(None)

    # # trace file info
    # get_selected_trace_count, set_selected_trace_count = mo.state(0)
    # get_selected_sample_count, set_selected_sample_count = mo.state(0)
    # get_selected_data, set_selected_data = mo.state(None)
    # get_selected_trace_data, set_selected_trace_data = mo.state(np.empty(0))

    # # trace downsample data
    # get_downsample_data, set_downsample_data = mo.state((pd.DataFrame({'index': [], 'traces': [], 'value': []}), []))

    def get_select_file_trace_attr(file_path):
        file_path = file_path[0].path
        print(file_path)
        if file_path.endswith('.npy'):
            data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
            set_selected_trace_count(trace_count)
            set_selected_sample_count(sample_count)
            set_selected_data(data)
            set_selected_trace_data(traces_source)
            print(trace_count)
        elif file_path.endswith('.zgroup'):
            file_path = get_zarr_dir(file_path)
            if file_path:
                data_type, traces_source, trace_count, sample_count, data = trace.load_traces(file_path)
                set_selected_trace_count(trace_count)
                set_selected_sample_count(sample_count)
                set_selected_data(data)
                set_selected_trace_data(traces_source)
        else:
            set_selected_trace_count(0)
            set_selected_sample_count(0)
            set_selected_data(None)
            set_selected_trace_data(np.empty(0))

    def get_zarr_dir(zgroup_file_path, depth=0):
        if depth > 3:
            return None
        depth += 1
        parent_path = os.path.dirname(zgroup_file_path)
        if parent_path.endswith('.zarr'):
            return parent_path
        else:
            return get_zarr_dir(parent_path, depth)


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


    def open_trace_file(v):
        print('open file: ', v)
        print('open file: ', get_selected_trace_data())
        # traces, indexs = trace.get_traces_df_from_ndarray(get_selected_trace_data(), trace_start.value, trace_stop.value, index_start.value, index_stop.value, sample_count.value)
        # set_downsample_data((traces, indexs))


    # ui

    trace_selector = mo.ui.file_browser(multiple=False, on_change=get_select_file_trace_attr)

    # trace file attr
    def get_selected_trace_attribute_panel():
        return mo.md(f'''
        Trace count: {get_selected_trace_count()}   Sample count: {get_selected_sample_count()}
        Data: 
        ''')     
    selected_trace_attribute_panel = get_selected_trace_attribute_panel()

    ####
    # data_type, trace_source, trace_count, data_count = load_traces('../data/traces.npy', set_trace_count, set_data_count)
    # traces, indexs = trace.get_traces_df_from_ndarray(trace_source, 0, 10, 0, 100, 500)
    ####

    # chart overview
    def get_chart_overview():
        interval_selection = alt.selection_interval(encodings=['x'])
        print('----', get_downsample_data()[0])
        base = alt.Chart(get_downsample_data()[0]).mark_line(size=1).encode(
            x = 'index:Q',
            y = 'value:Q',
            color = alt.Color('traces:N').legend(None)
        )
        chart_overview_base = base.properties(height=80).add_params(interval_selection)

        chart_overview_shadow = base.transform_filter(interval_selection).mark_line(size=1)

        return mo.ui.altair_chart(alt.layer(chart_overview_base, chart_overview_shadow), chart_selection=False, legend_selection=False, on_change=set_trace_data)

    # trace display config
    def get_trace_display_control_panel(*args, **kwargs):
        trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_selected_trace_count(), full_width=True, on_change=set_trace_start)
        trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_selected_trace_count(), value=min(get_selected_trace_count(), 10), full_width=True, on_change=set_trace_stop)
        index_start=mo.ui.number(label="Data index start", start=0, stop=get_selected_sample_count(), full_width=True, on_change=set_index_start)
        index_stop=mo.ui.number(label="Data index stop", start=0, stop=get_selected_sample_count(), value=get_selected_sample_count(), full_width=True, on_change=set_index_stop)
        sample_count=mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count)
        button_open_trace = mo.ui.button(label='Open', on_click=open_trace_file)
        return mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count,button_open_trace])

    # trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_selected_trace_count(), full_width=True, on_change=set_trace_start)
    # trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_selected_trace_count(), value=min(get_selected_trace_count(), 10), full_width=True, on_change=set_trace_stop)
    # index_start=mo.ui.number(label="Data index start", start=0, stop=get_selected_sample_count(), full_width=True, on_change=set_index_start)
    # index_stop=mo.ui.number(label="Data index stop", start=0, stop=get_selected_sample_count(), value=get_selected_sample_count(), full_width=True, on_change=set_index_stop)
    # sample_count=mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count)
    # button_open_trace = mo.ui.button(label='Open', on_change=open_trace_file, on_click=open_trace_file)
    # trace_display_control_panel = mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count,button_open_trace])
    # trace_display_control_panel = get_trace_display_control_panel()

    # chart detail
    # index_s = min(get_trace_data()['index'])
    # index_e = max(get_trace_data()['index'])

    # trace_data, _ = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_s, index_e, sample_count.value)

    # chart_detail = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
    #     x = alt.X('index:Q', bandPosition=0),
    #     # x = 'index:Q',
    #     y = 'value:Q',
    #     color = 'traces:N'
    # ), chart_selection=False)

    # ###

    # traces, indexs = trace.get_traces_df_from_ndarray(traces_source, trace_start.value, trace_stop.value, index_start.value, index_stop.value, sample_count.value)
    selected_trace_attribute_panel2 = get_selected_trace_attribute_panel()
    trace_display_control_panel2 = get_trace_display_control_panel()
    chart_overview2 = get_chart_overview()
    trace_selector, selected_trace_attribute_panel2
    return (
        chart_overview2,
        get_chart_overview,
        get_select_file_trace_attr,
        get_selected_trace_attribute_panel,
        get_trace_display_control_panel,
        get_zarr_dir,
        load_traces,
        nutcracker,
        open_trace_file,
        selected_trace_attribute_panel,
        selected_trace_attribute_panel2,
        trace_display_control_panel2,
        trace_selector,
    )


@app.cell
def __():
    # trace_select = mo.ui.file_browser(multiple=False, on_change=get_select_file_trace_attr)

    # trace_start=mo.ui.number(label="Trace index start", start=0, stop=get_trace_count(), full_width=True, on_change=set_trace_start)
    # trace_stop=mo.ui.number(label="Trace index stop", start=0, stop=get_trace_count(), value=min(get_trace_count(), 10), full_width=True, on_change=set_trace_stop)
    # index_start=mo.ui.number(label="Data index start", start=0, stop=get_data_count(), full_width=True, on_change=set_index_start)
    # index_stop=mo.ui.number(label="Data index stop", start=0, stop=get_data_count(), value=get_data_count(), full_width=True, on_change=set_index_stop)
    # sample_count=mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count)
    return


@app.cell
def __():
    # mo.vstack([trace_select, select_trace_attr])
    return


@app.cell
def __():
    # mo.vstack([mo.vstack([trace_select, select_trace_attr]), mo.hstack([mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count]), chart_detail_base], justify='space-around'), chart_overview])
    return


@app.cell
def __(
    get_chart_overview,
    get_selected_trace_attribute_panel,
    get_trace_display_control_panel,
    mo,
    trace_selector,
):
    selected_trace_attribute_panel1 = get_selected_trace_attribute_panel()
    trace_display_control_panel1 = get_trace_display_control_panel()
    chart_overview1 = get_chart_overview()

    mo.vstack([trace_selector, selected_trace_attribute_panel1, trace_display_control_panel1,chart_overview1])
    return (
        chart_overview1,
        selected_trace_attribute_panel1,
        trace_display_control_panel1,
    )


@app.cell
def __():
    # get_selected_trace_attribute_panel()
    return


@app.cell
def __(get_chart_overview):
    get_chart_overview()
    return


@app.cell
def __(get_trace_display_control_panel, mo, open_trace_file):
    # def yy():
    #     return [mo.ui.number(label="Trace index start", start=0, stop=get_selected_trace_count(), full_width=True, on_change=set_trace_start),
    #     mo.ui.number(label="Trace index stop", start=0, stop=get_selected_trace_count(), value=min(get_selected_trace_count(), 10), full_width=True, on_change=set_trace_stop),
    #     mo.ui.number(label="Data index start", start=0, stop=get_selected_sample_count(), full_width=True, on_change=set_index_start),
    #     mo.ui.number(label="Data index stop", start=0, stop=get_selected_sample_count(), value=get_selected_sample_count(), full_width=True, on_change=set_index_stop),
    #     mo.ui.number(label="Sample count", start=0, stop=1000, value=500, full_width=True, on_change=set_sample_count),
    #     mo.ui.button(label='Open', on_click=open_trace_file)]
    open_trace_file
    yy2 = get_trace_display_control_panel
    yy1 = yy2(open_trace_file)
    mo.vstack([yy1])
    return yy1, yy2


@app.cell
def __(mo, open_trace_file):
    # def xx2(v):
    #     print('open file: ', v)
    #     print('open file: ', get_selected_trace_data())

    def xx1():
        return mo.ui.button(label='Open', on_click=open_trace_file)
        
    # xx = mo.ui.button(label='Open', on_click=open_trace_file)
    xx = xx1()

    mo.vstack([xx])
    return xx, xx1


@app.cell
def __(get_trace_display_control_panel):
    get_trace_display_control_panel()
    return


@app.cell
def __(get_selected_sample_count):
    get_selected_sample_count()
    return


if __name__ == "__main__":
    app.run()
