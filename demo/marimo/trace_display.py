import marimo

__generated_with = "0.7.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    from crackernut.solver import trace
    import altair as alt
    from vega_datasets import data
    import numpy as np
    import pandas as pd
    import zarr
    return alt, data, mo, np, pd, trace, zarr


@app.cell
def __(trace):
    data_type, traces_source, trace_count, data_count = trace.load_traces('../data/traces.npy')
    return data_count, data_type, trace_count, traces_source


@app.cell
def __(data_count, mo, trace_count):
    trace_select_panel = mo.md('''
        **Select display trace index.**

        {traceStart} {traceStop} {indexStart} {indexStop}  {sampleCount}
    ''').batch(
            traceStart=mo.ui.number(label="Trace index start", start=0, stop=trace_count),
            traceStop=mo.ui.number(label="Trace index stop", start=0, stop=trace_count, value=10),
            indexStart=mo.ui.number(label="Data index start", start=0, stop=data_count),
            indexStop=mo.ui.number(label="Data index stop", start=0, stop=data_count, value=data_count),
            sampleCount=mo.ui.number(label="Sample count", start=0, stop=10000, value=500)
        ).form(show_clear_button=True, bordered=False)

    trace_select_panel
    return trace_select_panel,


@app.cell
def __(alt, trace, trace_select_panel, traces_source):
    # print(trace_select_panel.value)
    trace_panel = None
    if trace_select_panel.value:
        traces, indexs = trace.get_traces_df_from_ndarray(traces_source, trace_select_panel.value['traceStart'], trace_select_panel.value['traceStop'], trace_select_panel.value['indexStart'], trace_select_panel.value['indexStop'], trace_select_panel.value['sampleCount'])
        
        interval_selection = alt.selection_interval(encodings=['x'])
        base = alt.Chart(traces, width=800).mark_line(size=1).encode(
            x = 'index:Q',
            y = 'value:Q',
            color = 'traces:N'
        )
        
        legend_select = alt.selection_point(fields=['traces'], bind='legend')
        
        
        chart_detail = base.encode(alt.X('index:Q').scale(domain=interval_selection), opacity=alt.condition(legend_select, alt.value(1), alt.value(0.1))).add_params(legend_select)
        
        chart_overview = base.properties(height=80).add_params(interval_selection)
        
        pointerover = alt.selection_point(nearest=True, on="pointerover", clear='pointerout', fields=["index"], empty=False)
        
        rules = alt.Chart(traces).transform_pivot(
            "traces",
            value="value",
            groupby=["index"]
        ).mark_rule(color="red", size=2).encode(
            x=alt.X('index:Q').scale(domain=interval_selection),
            opacity=alt.condition(pointerover, alt.value(0.3), alt.value(0)),
            tooltip=[alt.Tooltip(str(t), type="quantitative") for t in indexs]
        ).add_params(pointerover)
        
        
        trace_panel = alt.vconcat(alt.layer(
            chart_detail, rules
        ).properties(
            width=800
        ), chart_overview)

    trace_panel
    return (
        base,
        chart_detail,
        chart_overview,
        indexs,
        interval_selection,
        legend_select,
        pointerover,
        rules,
        trace_panel,
        traces,
    )


if __name__ == "__main__":
    app.run()
