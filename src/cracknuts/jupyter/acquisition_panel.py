# Copyright 2024 CrackNuts. All rights reserved.

import pathlib
import typing
from typing import Any

from cracknuts.acquisition.acquisition import Acquisition
from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class AcquisitionPanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "AcquisitionPanelWidget.js"
    _css = ""

    acq_status = traitlets.Int(0).tag(sync=True)
    acq_run_progress = traitlets.Dict({"finished": 0, "total": 1}).tag(sync=True)

    trace_count = traitlets.Int(1000).tag(sync=True)
    sample_offset = traitlets.Int(0).tag(sync=True)
    sample_length = traitlets.Int(1024).tag(sync=True)
    trigger_judge_wait_time = traitlets.Float(0.05).tag(sync=True)
    trigger_judge_timeout = traitlets.Float(0.005).tag(sync=True)
    do_error_max_count = traitlets.Int(1).tag(sync=True)
    file_format = traitlets.Unicode("scarr").tag(sync=True)
    file_path = traitlets.Unicode("").tag(sync=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if not hasattr(self, "acquisition"):
            self.acquisition: Acquisition | None = None
            if "acquisition" in kwargs and isinstance(kwargs["acquisition"], Acquisition):
                self.acquisition: Acquisition = kwargs["acquisition"]
            if self.acquisition is None:
                raise ValueError("acquisition is required")

        self.reg_msg_handler("acqStatusButton", "onChange", self.msg_acq_status_changed)
        self.acquisition.on_status_changed(self.update_acq_status)
        self.acquisition.on_run_progress_changed(self.update_acq_run_progress)
        self.acq_status = self.acquisition.get_status()

    def sync_config(self) -> None:
        if self.acquisition.trace_count != -1:
            # When acquisition.trace_count = -1, it indicates that the ACQUISITION is in test mode,
            # and in this mode, synchronization of the acquisition trace_count to the GUI is not required.
            self.trace_count = self.acquisition.trace_count
        self.sample_offset = self.acquisition.sample_offset
        self.sample_length = self.acquisition.sample_length
        self.trigger_judge_wait_time = self.acquisition.trigger_judge_wait_time
        self.trigger_judge_timeout = self.acquisition.trigger_judge_timeout
        self.do_error_max_count = self.acquisition.do_error_max_count
        self.file_format = self.acquisition.file_format
        self.file_path = (
            ""
            if self.acquisition.file_path is None or self.acquisition.file_path == "auto"
            else self.acquisition.file_path
        )

    def bind(self) -> None:
        ...
        # todo complete ui -> python sync

    def update_acq_status(self, status) -> None:
        self.acq_status = status

    def update_acq_run_progress(self, progress: dict[str, int]):
        self.acq_run_progress = progress

    def msg_acq_status_changed(self, changed: dict[str, typing.Any]):
        status = changed.get("status")
        if status == "pause":
            self.acquisition.pause()
        elif status == "test":
            self.acquisition.test(
                sample_offset=self.sample_offset,
                trigger_judge_wait_time=self.trigger_judge_wait_time,
                trigger_judge_timeout=self.trigger_judge_timeout,
                do_error_max_count=self.do_error_max_count,
            )
        elif status == "run":
            self.acquisition.run(
                count=self.trace_count,
                sample_offset=self.sample_offset,
                sample_length=self.sample_length,
                trigger_judge_wait_time=self.trigger_judge_wait_time,
                trigger_judge_timeout=self.trigger_judge_timeout,
                do_error_max_count=self.do_error_max_count,
                file_format=self.file_format,
                file_path="auto" if self.file_path == "" or self.file_path is None else self.file_path,
            )
        else:
            self.acquisition.stop()
