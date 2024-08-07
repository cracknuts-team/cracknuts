import marimo

__generated_with = "0.7.12"
app = marimo.App(width="medium")


@app.cell
def __():
    import matplotlib.pyplot as plt
    import numpy as np
    return np, plt


@app.cell
def __(np):
    # 生成频率为1MHz的正弦信号数据
    time = np.linspace(0, 1e-6, 1000)  # 时间轴，从0到1us，共1000个点
    cycle = 4  # 图中的周期数
    signal = np.sin(cycle * 2 * np.pi * 1e6 * time)
    return cycle, signal, time


@app.cell
def __(plt, signal, time):
    # 创建第一个子图
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # 第一个子图：绘制频率为1MHz的正弦信号，每隔10个点为红色
    axs[0].plot(time, signal)
    for i in range(10, len(time), 25):  # 从索引10开始每隔10个点标记
        axs[0].scatter(time[i], signal[i], color='red')

    # 第二个子图与第一个相同，只是间隔13个点为红色
    axs[1].plot(time, signal)
    for i in range(10, len(time), 29):  # 从索引13开始每隔13个点标记
        axs[1].scatter(time[i], signal[i], color='red')

    plt.show()
    return axs, fig, i


@app.cell
def __(plt):
    plt.show()
    return


@app.cell
def __():
    return


@app.cell
def __():
    import marimo as mo
    return mo,


if __name__ == "__main__":
    app.run()
