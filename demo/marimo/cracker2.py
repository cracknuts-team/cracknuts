import marimo

__generated_with = "0.7.11"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import cracknuts.solver.trace as nt
    import numpy as np
    import altair as alt
    from cracknuts.acquisition.acquisitiontemplate import AcquisitionTemplate
    import cracknuts.logger as logger
    import logging
    return AcquisitionTemplate, alt, logger, logging, mo, np, nt


@app.cell
def __(Acquisition, logger, logging):
    acq = Acquisition(None)
    # acq.on_wave_loaded(lambda w: print(w.shape))
    logger.set_level(logging.DEBUG, acq)
    acq.test()
    return acq,


@app.cell
def __(np):
    # refresh_button
    wave = np.array([np.random.random(1000)])
    return wave,


@app.cell
def __(acq, refresh_button, set_wave):
    refresh_button
    # set_wave(np.array([np.random.random(1000)]))
    set_wave(acq.get_last_wave())
    return


@app.cell
def __(mo, np):
    get_wave, set_wave = mo.state(np.array([np.random.random(1000)]))
    return get_wave, set_wave


@app.cell
def __(get_wave, nt):
    trace_data, _ = nt.get_traces_df_from_ndarray(get_wave(), 0, 1, 0, 1000, 1000)
    return trace_data,


@app.cell
def __(alt, mo, trace_data):
    chart_wave = mo.ui.altair_chart(alt.Chart(trace_data).mark_line(size=1).encode(
        x = 'index:Q',
        y = 'value:Q',
        color = 'traces:N'
    ), chart_selection=False)
    return chart_wave,


@app.cell
def __(mo):
    refresh_button = mo.ui.refresh(
        options=["1s", "3s", "5s"],
        default_interval="1s",
    )
    return refresh_button,


@app.cell
def __(chart_wave, mo, refresh_button):
    mo.vstack([refresh_button, chart_wave])
    return


@app.cell
def __():
    # import time

    # for i in range(10):
    #     print(i)
    #     set_wave(np.array([np.random.random(1000)]))
    #     time.sleep(1)
    return


if __name__ == "__main__":
    app.run()
