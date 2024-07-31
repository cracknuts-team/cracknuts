import marimo

__generated_with = "0.7.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"# 软件实现AES算法的CPA分析")
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"## 基于汉明重量的AES CPA攻击简介")
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        ## 能量迹文件格式介绍
        能量迹文件格式为zarr, 参见https://zarr.readthedocs.io/en/stable/tutorial.html
        """
    )
    return


@app.cell
def __():
    # import zarr
    # import matplotlib.pyplot as plt
    # import numpy as np
    # from sys import stdout
    # from numcodecs import Blosc
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"采集到的AES能量迹存储在如下文件中：")
    return


@app.cell
def __():
    dataset_name = '../data/aes_cp_3.zarr'
    return dataset_name,


@app.cell
def __(dataset_name, zarr):
    dataset = zarr.open(dataset_name, "r")
    return dataset,


@app.cell
def __(dataset):
    dataset.info
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        文件格式如下：  
        其中traces是能量迹，plaintext是明文数据
        """
    )
    return


@app.cell(hide_code=True)
def __(dataset):
    dataset.tree()
    return


@app.cell
def __(dataset, plt):
    #画出其中一条能量迹
    fig2, ax2 = plt.subplots(figsize=(32, 4))
    ax2.plot(dataset['0/0/traces'][0], color='blue')

    ax2.set_xlabel('Samples')
    ax2.set_ylabel('Value')
    # plt.show()
    ax2
    return ax2, fig2


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


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"## 完整分析过程")
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        使用scarr库（https://github.com/decryptofy/scarr.git）来进行AES第一轮第0个字节的CPA分析展示。  
        python版本要求：python 3.10以上  
        依赖包安装过程：  
        git clone https://github.com/decryptofy/scarr.git  
        cd scarr  
        pip install .
        """
    )
    return


@app.cell
def __():
    from scarr.engines.cpa import CPA as cpa
    from scarr.file_handling.trace_handler import TraceHandler as th
    from scarr.model_values.sbox_weight import SboxWeight
    from scarr.container.container import Container, ContainerOptions
    return Container, ContainerOptions, SboxWeight, cpa, th


@app.cell
def __(Container, ContainerOptions, SboxWeight, cpa, dataset_name, th):
    handler2 = th(fileName=dataset_name)
    model = SboxWeight()
    engine2 = cpa(model)
    container2 = Container(options=ContainerOptions(engine=engine2, handler=handler2), model_positions = [x for x in range(1)])
    return container2, engine2, handler2, model


@app.cell
def __(container2):
    container2.run()
    return


@app.cell
def __(container2):
    results2 = container2.engine.get_result()
    return results2,


@app.cell
def __(results2):
    results2.shape
    return


@app.cell
def __(engine2):
    engine2.get_candidate()
    return


@app.cell
def __(plt, results2):
    fig, ax = plt.subplots(figsize=(32, 4))
    ax.plot(results2[0,0,0,:,:5000].T, color='gray')
    ax.plot(results2[0,0,0,0x11,:5000].T, color='red')

    ax.set_xlabel('Samples')
    ax.set_ylabel('CPA')
    # plt.show()

    ax
    return ax, fig


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        ## 分解讲解
        在这里面，为了便于清晰展示，程序运行速度将比较慢。
        """
    )
    return


@app.cell
def __(mo):
    mo.md(
        r"""
        - 第一步： 选择所分析算法的中间变量，作为CPA分析的对象。中间变量的选取原则为需要是变化的数据$d$和一小部分密钥$k$的函数，即$f(d,k)$. 这里我们选择AES的第一轮的S盒输出作为中间变量，此时$d$为明文，$k$为whitening key的一个字节。选择这样的中间变量的原因是需要已知且变化的数据，且涉及的密钥比特数不应太多，以使猜测密钥进行CPA的复杂度可以接受。
        - 第二步：能量迹采集。
        """
    )
    return


@app.cell
def __(mo):
    mo.md(r"- 第三步：计算中间变量猜测值的汉明重量。即计算$HW(S(p \oplus k))$，其中$HW$指的是汉明重量。汉明重量的计算，可以直接计算，也可以将0-255的汉明重量预计算出来存于WEIGHTS中，以空间换时间。对于某个明文$p$，我们将所有256种密钥猜测的$HW(S(p \oplus k))$都计算出来，也是空间换时间。")
    return


@app.cell
def __():
    from numba import njit, prange
    return njit, prange


@app.cell
def __(njit, np, prange):
    #定义AES的S盒
    AES_SBOX = np.array([99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118,
                        202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192,
                        183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21,
                        4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117,
                        9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132,
                        83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207,
                        208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168,
                        81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210,
                        205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115,
                        96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219,
                        224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121,
                        231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8,
                        186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138,
                        112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158,
                        225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223,
                        140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22])

    #计算汉量重量的函数
    @njit
    def hw(a, n):
        h = 0
        for i in prange(0, n):
            h += (a >> i) & 1
        return h

    #预计算：0-255的汉明重量
    WEIGHTS = np.array([0,1,1,2,1,2,2,3,1,2,2,3,2,3,3,4,
                        1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,
                        1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
                        1,2,2,3,2,3,3,4,2,3,3,4,3,4,4,5,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
                        2,3,3,4,3,4,4,5,3,4,4,5,4,5,5,6,
                        3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
                        3,4,4,5,4,5,5,6,4,5,5,6,5,6,6,7,
                        4,5,5,6,5,6,6,7,5,6,6,7,6,7,7,8],
                        np.float32)

    #密钥猜测值，为0到255之间的数
    KEYS = np.arange(256).reshape(-1, 1)
    return AES_SBOX, KEYS, WEIGHTS, hw


@app.cell
def __(dataset):
    dataset.tree()
    return


@app.cell
def __(dataset):
    #为了分析第0个字节，将plaintext中的相应字节取出
    data = dataset['0/0/plaintext'][:,0]
    #将曲线取出
    traces = dataset['0/0/traces']
    return data, traces


@app.cell
def __(data):
    data.shape
    return


@app.cell
def __(AES_SBOX, KEYS, WEIGHTS, data, np):
    #这个函数计算对于一个明文字节，对应所有256种密钥猜测的S盒输出的汉明重量
    def calculate_all_tables_helper(single_data):
            inputs = np.bitwise_xor(single_data, KEYS)

            outputs = AES_SBOX[inputs]

            return WEIGHTS[outputs]

    #计算对于所有明文的这个字节，对应所有256种密钥猜测的S盒输出的汉明重量
    intermedia_data = np.apply_along_axis(calculate_all_tables_helper, axis=0, arr=data).T
    return calculate_all_tables_helper, intermedia_data


@app.cell
def __(intermedia_data, mo):
    mo.md(f'intermedia_data.shape: {intermedia_data.shape}')
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        - 第四步：计算相关性。

        相关系数是衡量两个变量之间线性关系强度和方向的统计量。在CPA（Correlation Power Analysis）攻击中，通常使用皮尔逊相关系数（Pearson Correlation Coefficient）来衡量实际测量的能量迹与根据猜测密钥计算的预期功耗之间的相关性。

        皮尔逊相关系数的计算公式如下：

        \[
        r_{i,j} = \frac{\sum_{d=1}^{D} (h_{d,i} - \bar{h}_i)(t_{d,j} - \bar{t}_j)}{\sqrt{\sum_{d=1}^{D} (h_{d,i} - \bar{h}_i)^2 \sum_{d=1}^{D} (t_{d,j} - \bar{t}_j)^2}}
        \]

        其中：  
            *  \( r_{i,j} \) 是相关系数。<br>
            *  \( h_{d,i} \) 是第 \( d \) 个样本在第 \( i \) 个猜测密钥下的汉明重量。<br>
            *  \( \bar{h}_i \) 是第 \( i \) 个猜测密钥下所有样本的汉明重量的平均值。<br>
            *  \( t_{d,j} \) 是第 \( d \) 个能量迹在第 \( j \) 个时间点的功耗值。<br>
            *  \( \bar{t}_j \) 是所有能量迹在第 \( j \) 个时间点的功耗值的平均值。<br>
            *  \( D \) 是样本数量或时间点的数量。

        相关系数的值范围在 -1 到 1 之间，其中：  <br>
            *  1 表示完全正相关，即随着一个变量的增加，另一个变量也增加。 <br> 
            *  -1 表示完全负相关，即随着一个变量的增加，另一个变量减少。  <br>
            *  0 表示没有线性相关。

        在CPA攻击中，攻击者会计算每个猜测密钥的相关系数，并寻找最高值，这个最高值对应的猜测密钥很可能是正确的密钥。
        """
    )
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(
        r"""
        下面是计算相关系数的过程:  

         sample_sum: $\sum_{d=1}^{D} t_{d,j}$

         sample_sq_sum: $\sum_{d=1}^{D} t^2_{d,j}$

         model_sum: $\sum_{d=1}^{D} h_{d,i}$

         model_sq_sum: $\sum_{d=1}^{D} h^2_{d,i}$

         prod_sum: $\sum_{d=1}^{D} h_{d,i} \cdot t_{d,j}$
        """
    )
    return


@app.cell
def __(intermedia_data, np, traces):
    sample_sum = np.sum(traces, axis=0)
    sample_sq_sum = np.sum(np.square(traces), axis=0)
    model_sum = np.sum(intermedia_data, axis=0)
    model_sq_sum = np.sum(np.square(intermedia_data), axis=0)
    prod_sum = np.matmul(intermedia_data.T, traces)
    return model_sq_sum, model_sum, prod_sum, sample_sq_sum, sample_sum


@app.cell
def __(traces):
    #曲线数
    trace_count = traces.shape[0]
    return trace_count,


@app.cell
def __(traces):
    traces.shape
    return


@app.cell
def __(
    model_sq_sum,
    model_sum,
    np,
    prod_sum,
    sample_sq_sum,
    sample_sum,
    trace_count,
):
    # 计算均值
    sample_mean = np.divide(sample_sum, trace_count)
    model_mean = np.divide(model_sum, trace_count)
    prod_mean = np.divide(prod_sum, trace_count)
    # 计算相关系数的分子部分
    numerator = np.subtract(prod_mean, model_mean[:, None]*sample_mean)
    # 计算相关系数分母与能量迹值相关部分
    to_sqrt = np.subtract(np.divide(sample_sq_sum, trace_count), np.square(sample_mean))
    to_sqrt[to_sqrt < 0] = 0
    denom_sample = np.sqrt(to_sqrt)
    # 计算相关系数分母与汉明重量值相关部分
    to_sqrt = np.subtract(np.divide(model_sq_sum, trace_count), np.square(model_mean))
    to_sqrt[to_sqrt < 0] = 0
    denom_model = np.sqrt(to_sqrt)

    denominator = denom_model[:, None]*denom_sample

    denominator[denominator == 0] = 1

    # result里存的是相关系数
    result = np.divide(numerator, denominator)
    return (
        denom_model,
        denom_sample,
        denominator,
        model_mean,
        numerator,
        prod_mean,
        result,
        sample_mean,
        to_sqrt,
    )


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"result里存的是相关系数矩阵$r_{i,j}$，即第$i$个密钥猜测，第$j$个时间点的相关系数值。")
    return


@app.cell
def __(result):
    result.shape
    return


@app.cell(hide_code=True)
def __(mo):
    mo.md(r"下面找出最大的$r_{i,j}$，并定位其对应的密钥猜测ck，这也是对这个密钥字节的CPA分析结果。在本例子中，所设置的AES-128的密钥为0x1122334455667788。因此，对于第一轮的CPA分析，我们所关注的第0字节的密钥为17(0x11). 可见CPA的分析结果是正确的。")
    return


@app.cell
def __(np, result):
    candidate = [None for _ in range(result.shape[0])]

    for i in range(result.shape[0]):
        candidate[i] = np.unravel_index(np.abs(result[i, :]).argmax(), result[i, :].shape[0:])[0]
    return candidate, i


@app.cell
def __(candidate, np, result):
    candidates = np.empty(256, dtype=np.float64)
    for k in range(256):
        candidates[k] = result[k,candidate[k]]
    ck = np.abs(candidates).argmax()
    print(ck)
    return candidates, ck, k


@app.cell
def __(plt, result):
    fig1, ax1 = plt.subplots(figsize=(32, 4))
    for j in range(0, 256):
        ax1.plot(result[j,:], color='gray')
    ax1.plot(result[0x11,:], color='red')

    ax1.set_xlabel('Samples')
    ax1.set_ylabel('CPA')
    # plt.show()
    ax1
    return ax1, fig1, j


@app.cell
def __(mo):
    mo.md(r"## 对齐代码实验")
    return


@app.cell
def __():
    import scipy as sp
    return sp,


@app.cell
def __(traces):
    # 参照曲线是哪条
    ref_num = 0
    # 参照曲线开始点和结束点
    sStart = 500
    sEnd = 1500

    ref_trace = traces[0, sStart:sEnd]
    ref_trace = ref_trace[::-1]
    return ref_num, ref_trace, sEnd, sStart


@app.cell(hide_code=True)
def __():
    # mo.vstack([mo.vstack([trace_select, select_trace_attr]), mo.vstack([mo.hstack([trace_start, trace_stop, index_start, index_stop, sample_count, button_open_trace]), chart_detail_base]), chart_overview])
    return


@app.cell(hide_code=True)
def __():
    import marimo as mo
    from cracknuts.solver import trace
    import altair as alt
    # from vega_datasets import data
    import numpy as np
    import pandas as pd
    import zarr
    import os
    import cracknuts.solver.trace

    import matplotlib.pyplot as plt
    import numpy as np
    from sys import stdout
    from numcodecs import Blosc
    return Blosc, alt, mo, np, cracknuts, os, pd, plt, stdout, trace, zarr


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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def __(alt, get_downsample_data, mo, set_downsample_data):
    # chart overview
    interval_selection = alt.selection_interval(encodings=['x'])
    base = alt.Chart(get_downsample_data()).mark_line(size=1).encode(
        x = 'index:Q',
        y = 'value:Q',
        color = alt.Color('traces:N').legend(None)
    )
    # print('overview run...')
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


@app.cell(hide_code=True)
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
    # print('detail run...')
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


@app.cell(hide_code=True)
def __(get_selected_sample_count, get_selected_trace_count, mo):
    select_trace_attr = mo.md(f'''
    Trace count: {get_selected_trace_count()}   Sample count: {get_selected_sample_count()}
    ''')
    return select_trace_attr,


if __name__ == "__main__":
    app.run()
