import marimo

__generated_with = "0.7.14"
app = marimo.App(width="medium")


@app.cell
def __(mo):
    mo.md("""# Reactive plots! ðŸš—""")
    return


@app.cell
def __(mo):
    width = mo.ui.slider(start=1, stop=100, label="width")
    height = mo.ui.slider(start=1, stop=250, step=1, label="height")

    [width, height]
    return height, width


@app.cell
def __(height, mo, width):
    area = mo.stat(
        label="Area",
        bordered=True,
        caption="1",
        direction="increase",
        value=f"${width.value * height.value:,.0f}",
    )
    circumference = mo.stat(
        label="Circumference",
        bordered=True,
        caption="2",
        direction="increase",
        value=f"${(width.value + height.value)*2:,.0f}",
    )
    mo.hstack(
        [area, circumference],
        widths="equal",
        gap=1,
    )
    return area, circumference


@app.cell
def __(mo):
    mo.md("""This plot is **interactive**! Click and drag to select points to get a filtered dataset.""")
    return


@app.cell
def __(alt, data, mo):
    stocks = data.stocks()
    stock_brush = alt.selection_interval(encodings=["x"])

    stock_base = (
        alt.Chart(stocks)
        .mark_line(opacity=0.3)
        .encode(x="date", y="price", color="symbol")
        .add_params(stock_brush)
    )

    stock_detail = stock_base.transform_filter(stock_brush).mark_line()

    stock_chart = mo.ui.altair_chart(
        stock_base + stock_detail, chart_selection=False, legend_selection=False
    )

    stock_chart
    return stock_base, stock_brush, stock_chart, stock_detail, stocks


@app.cell
def __(
    alt,
    date_max,
    date_min,
    get_max,
    get_min,
    mo,
    pd,
    stock_chart,
    stocks,
):
    mo.stop(stock_chart.value.empty)

    t_min = get_min()
    t_max = get_max()
    filtered_stocks = stocks.loc[
        (stocks["date"] >= pd.Timestamp(t_min))
        & (stocks["date"] <= pd.Timestamp(t_max))
    ]

    stock_filtered = mo.ui.altair_chart(
        alt.Chart(filtered_stocks)
        .mark_line()
        .encode(x="date:T", y="price:Q", color="symbol:N")
    )
    stock_filtered
    mo.hstack([[date_min, date_max], stock_filtered])
    return filtered_stocks, stock_filtered, t_max, t_min


@app.cell
def __(mo):
    get_min, set_min = mo.state(None)
    get_max, set_max = mo.state(None)
    return get_max, get_min, set_max, set_min


@app.cell
def __(get_max, get_min, mo, set_max, set_min):
    date_min = mo.ui.date(value=get_min(), on_change=set_min)
    date_max = mo.ui.date(value=get_max(), on_change=set_max)
    return date_max, date_min


@app.cell
def __(mo, set_max, set_min, stock_chart):
    mo.stop(stock_chart.value.empty)
    set_min(min(stock_chart.value["date"]).date())
    set_max(max(stock_chart.value["date"]).date())
    return


@app.cell
def __(data, mo):
    cars = data.cars()
    columns = cars.columns.tolist()
    x_axis = mo.ui.dropdown(
        options=columns,
        value="Horsepower",
        label="X Axis:",
        full_width=True,
    )
    y_axis = mo.ui.dropdown(
        options=columns,
        value="Miles_per_Gallon",
        label="Y Axis:",
        full_width=True,
    )
    color = mo.ui.dropdown(
        options=columns,
        value="Origin",
        label="Color:",
        full_width=True,
    )
    clear = mo.ui.button(
        label="Clear",
        full_width=True,
    )
    return cars, clear, color, columns, x_axis, y_axis


@app.cell
def __(alt, cars, color, mo, x_axis, y_axis):
    brush = alt.selection_interval(
        encodings=["x"],
        on="[mousedown[event.altKey], mouseup] > mousemove",
        translate="[mousedown[event.altKey], mouseup] > mousemove!",
        zoom="wheel![event.altKey]",
    )

    interaction = alt.selection_interval(
        bind="scales",
        encodings=["x"],
        on="[mousedown[!event.altKey], mouseup] > mousemove",
        translate="[mousedown[!event.altKey], mouseup] > mousemove!",
        zoom="wheel![!event.altKey]",
    )

    chart = mo.ui.altair_chart(
        alt.Chart(cars)
        .mark_line(point=True)
        .encode(x=x_axis.value, y=y_axis.value, color=color.value)
        .add_params(brush, interaction)
    )
    mo.hstack(
        [
            mo.vstack(
                [
                    mo.md("## Controls"),
                    x_axis,
                    y_axis,
                    color,
                ]
            ),
            chart,
        ]
    )
    return brush, chart, interaction


@app.cell
def __(mo):
    mo.md("""Select one or more cars from the table.""")
    return


@app.cell
def __(chart, mo):
    (filtered_data := mo.ui.table(chart.value))
    return filtered_data,


@app.cell
def __(alt, filtered_data, mo):
    mo.stop(not len(filtered_data.value))
    mpg_hist = mo.ui.altair_chart(
        alt.Chart(filtered_data.value)
        .mark_bar()
        .encode(alt.X("Miles_per_Gallon:Q", bin=True), y="count()")
    )
    horsepower_hist = mo.ui.altair_chart(
        alt.Chart(filtered_data.value)
        .mark_bar()
        .encode(alt.X("Horsepower:Q", bin=True), y="count()")
    )
    mo.hstack([mpg_hist, horsepower_hist], justify="space-around", widths="equal")
    return horsepower_hist, mpg_hist


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    import altair as alt
    from vega_datasets import data
    import pandas as pd
    return alt, data, pd


if __name__ == "__main__":
    app.run()
