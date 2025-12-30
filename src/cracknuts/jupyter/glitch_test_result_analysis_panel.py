# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import sqlite3

import traitlets
from anywidget import AnyWidget

from cracknuts import logger


class GlitchTestResultAnalysisPanel(AnyWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "GlitchTestResultAnalysisWidget.js"
    _css = ""

    selected_status = traitlets.List([0, 1, 2, 3]).tag(sync=True)
    glitch_test_result = traitlets.List([]).tag(sync=True)

    def __init__(self, glitch_test_result_path: str):
        super().__init__()
        self._logger = logger.get_logger(self)
        self.glitch_test_result_path = glitch_test_result_path
        self._conn = sqlite3.connect(self.glitch_test_result_path)
        self.cursor = self._conn.cursor()
        self.load_data()

    def load_data(self):
        query = f"SELECT * FROM glitch_result where status in ({", ".join(map(str, self.selected_status))})"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        # print([dict(zip([column[0] for column in self.cursor.description], row)) for row in rows][0])
        self.glitch_test_result = [dict(zip([column[0] for column in self.cursor.description], row)) for row in rows]

    @traitlets.observe("selected_status")
    def on_selected_status_change(self, change):
        self.load_data()
