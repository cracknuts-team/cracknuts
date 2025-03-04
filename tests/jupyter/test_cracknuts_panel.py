import logging
import os.path
import socket
import struct
import threading
import time
import subprocess
import sys
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
import cracknuts.mock as mock
from cracknuts import CrackerS1
from cracknuts.cracker.protocol import Command


@pytest.fixture(scope='module')
def mock_cracker():
    def start_mock_cracker():
        # mock.start(logging_level=logging.WARNING)
        mock.start(logging_level=logging.INFO)

    mock_thread = threading.Thread(target=start_mock_cracker)
    mock_thread.daemon = True
    mock_thread.start()
    time.sleep(1)
    yield


def wait_for_jupyter(port=8888, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                return True
        time.sleep(0.5)
    return False


@pytest.fixture(scope="module", autouse=True)
def start_jupyter_lab(request):
    jupyter_process = subprocess.Popen(
        [str(Path(sys.executable)), "-m", "jupyter", "lab", "--no-browser", "--ServerApp.token=''",
         f"{os.path.dirname(request.fspath)}/test_cracknuts_panel.ipynb"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if not wait_for_jupyter():
        raise RuntimeError("Jupyter Lab 启动失败")

    yield

    jupyter_process.terminate()
    jupyter_process.wait()


@pytest.fixture(scope="module")
def browser(start_jupyter_lab):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def jupyter_page(browser):
    context = browser.new_context()
    page = context.new_page()
    # page.set_viewport_size(viewport_size={"width": 1920, "height": 1080})
    yield page
    page.close()


@pytest.fixture(scope="module")
def assert_cracker(mock_cracker):
    cracker = CrackerS1("localhost")
    cracker.connect(update_bin=False)
    yield cracker


def get_result_by_command(device, command):
    _, r = device.send_with_command(0xFFFF, payload=struct.pack('>I', command))
    return r


@pytest.fixture(scope="module")
def run_cell(mock_cracker, jupyter_page):
    jupyter_page.goto('http://localhost:8888/lab/workspaces/auto-0/tree/test_cracknuts_panel.ipynb')

    jupyter_page.click("div.jp-Cell:first-of-type", timeout=15000)

    jupyter_page.click(
        'jp-button[title="Run this cell and advance (Shift+Enter)"][data-command="notebook:run-cell-and-select-next"]', timeout=15000)

    jupyter_page.wait_for_selector("#cracknuts_widget", timeout=15000, state="attached")


def test_uart_enable_disable(run_cell, assert_cracker, jupyter_page):
    jupyter_page.click("#cracker_config_uart_enable", timeout=5000)
    assert struct.unpack('?', get_result_by_command(assert_cracker, Command.CRACKER_UART_ENABLE))[0]

    # jupyter_page.click("#cracker_config_uart_enable", timeout=5000)
    # assert not struct.unpack('?', get_result_by_command(assert_cracker, Command.CRACKER_UART_ENABLE))[0]

    jupyter_page.query_selector('.ant-select:has(#cracker_config_uart_baudrate)').click()
    jupyter_page.click('.ant-select-item.ant-select-item-option[title="57600"]', timeout=5000)
    assert struct.unpack('>BBBI', get_result_by_command(assert_cracker, Command.CRACKER_UART_CONFIG))[3] == 57600

    jupyter_page.query_selector('.ant-select:has(#cracker_config_uart_baudrate)').click()
    jupyter_page.click('.ant-select-item.ant-select-item-option[title="9600"]', timeout=5000)
    assert struct.unpack('>BBBI', get_result_by_command(assert_cracker, Command.CRACKER_UART_CONFIG))[3] == 9600