import time
import subprocess
import sys
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

# 获取当前虚拟环境中的 Python 解释器路径
python_path = Path(sys.executable)

# 启动 Jupyter Lab
@pytest.fixture(scope="module", autouse=True)
def start_jupyter_lab():
    # 启动 Jupyter Lab 进程，使用虚拟环境中的 Python 解释器
    jupyter_process = subprocess.Popen(
        [str(python_path), "-m", "jupyter", "lab"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # 等待 Jupyter Lab 完全启动
    time.sleep(5)  # 给 Jupyter Lab 启动一些时间

    yield

    # 关闭 Jupyter Lab 进程
    jupyter_process.terminate()
    jupyter_process.wait()


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False 以便调试
        yield browser
        browser.close()

@pytest.fixture(scope="module")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()

def test_open_jupyter_lab_and_run_notebook(page):
    # 打开 Jupyter Lab
    page.goto('http://localhost:8888')  # 默认情况下，Jupyter Lab 在本地 8888 端口运行
    page.wait_for_selector('text=JupyterLab')

    # 打开指定的 notebook
    notebook_path = "example_notebook.ipynb"  # 修改为你的 notebook 路径
    page.click(f"text={notebook_path}")
    page.wait_for_selector(f"div[title='{notebook_path}']")  # 确保 notebook 加载完成

    # 执行 notebook 中的第一个单元格
    page.click('button[title="Run the selected cells"]')
    time.sleep(2)  # 等待几秒钟确保单元格代码被执行

    # 获取输出内容并断言
    output = page.text_content('div.output_area')  # 获取输出区域内容
    assert "Expected Output" in output  # 这里 "Expected Output" 是你期望的输出内容

    # 你还可以在测试中进行其他断言，验证输出的正确性
    print("Notebook Output:", output)
