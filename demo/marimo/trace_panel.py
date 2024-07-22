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

    mo.vstack([chart_overview])
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

    chart_detail_base
    return chart_detail_base, index_e, index_s, trace_data


@app.cell
def __(index_start, index_stop, mo, sample_count, trace_start, trace_stop):
    mo.vstack([trace_start, trace_stop, index_start, index_stop, sample_count])
    return


@app.cell
def __(alt, cars):
    slider = alt.binding_range(min=0, max=1, step=0.05, name='opacity:')
    op_var = alt.param(value=0.1, bind=slider)

    alt.Chart(cars).mark_circle(opacity=op_var).encode(
        x='Horsepower:Q',
        y='Miles_per_Gallon:Q',
        color='Origin:N'
    ).add_params(
        op_var
    )
    return op_var, slider


if __name__ == "__main__":
    app.run()
