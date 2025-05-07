# Copyright 2024 CrackNuts. All rights reserved.

import os
import pathlib
import typing
from dataclasses import dataclass
from typing import Any
import platform
from cracknuts import logger
from cracknuts.acquisition.acquisition import Acquisition, AcquisitionConfig
from traitlets import traitlets

from cracknuts.jupyter.panel import MsgHandlerPanelWidget


class AcquisitionPanelWidget(MsgHandlerPanelWidget):
    _esm = pathlib.Path(__file__).parent / "static" / "AcquisitionPanelWidget.js"
    _css = ""

    acq_status = traitlets.Int(0).tag(sync=True)
    acq_run_progress = traitlets.Dict({"finished": 0, "total": -1}).tag(sync=True)

    trace_count = traitlets.Int(1000).tag(sync=True)
    sample_offset = traitlets.Int(0).tag(sync=True)
    sample_length = traitlets.Int(1024).tag(sync=True)
    trigger_judge_wait_time = traitlets.Float(0.05).tag(sync=True)
    trigger_judge_timeout = traitlets.Float(0.005).tag(sync=True)
    do_error_max_count = traitlets.Int(1).tag(sync=True)
    file_format = traitlets.Unicode("scarr").tag(sync=True)
    file_path = traitlets.Unicode("").tag(sync=True)
    trace_fetch_interval = traitlets.Float(2.0).tag(sync=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._logger = logger.get_logger(self)
        if not hasattr(self, "acquisition"):
            self.acquisition: Acquisition | None = None
            if "acquisition" in kwargs and isinstance(kwargs["acquisition"], Acquisition):
                self.acquisition: Acquisition = kwargs["acquisition"]
            if self.acquisition is None:
                raise ValueError("acquisition is required")

        self.reg_msg_handler("acqStatusButton", "onChange", self.msg_acq_status_changed)
        self.reg_msg_handler("fileSelector", "getDefaultDirectoryInfo", self.msg_get_default_directory_info)
        self.reg_msg_handler("fileSelector", "getDirectoryList", self.msg_get_directory_list)
        self.acquisition.on_status_changed(self.update_acq_status)
        self.acquisition.on_run_progress_changed(self.update_acq_run_progress)
        self.acq_status = self.acquisition.get_status()

    def sync_config_from_acquisition(self) -> None:
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

    def before_test(self): ...

    def before_run(self): ...

    def listen_acquisition_config(self) -> None:
        ...
        # todo complete ui -> python sync

    def get_acquisition_panel_config(self) -> AcquisitionConfig:
        return AcquisitionConfig(
            self.trace_count,
            self.sample_length,
            self.sample_offset,
            self.trigger_judge_timeout,
            self.trigger_judge_wait_time,
            self.do_error_max_count,
            self.file_path,
            self.file_format,
        )

    def update_acq_status(self, status) -> None:
        self.acq_status = status

    def update_acq_run_progress(self, progress: dict[str, int]):
        self.acq_run_progress = progress

    def msg_acq_status_changed(self, changed: dict[str, typing.Any]):
        status = changed.get("status")
        if status == "pause":
            self.acquisition.pause()
        elif status == "test":
            self.before_test()
            self.acquisition.test(
                sample_offset=self.sample_offset,
                trigger_judge_wait_time=self.trigger_judge_wait_time,
                trigger_judge_timeout=self.trigger_judge_timeout,
                do_error_max_count=self.do_error_max_count,
                trace_fetch_interval=self.trace_fetch_interval,
            )
        elif status == "run":
            self.before_run()
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

    def msg_get_default_directory_info(self, args: dict[str, typing.Any]) -> None:
        init_directory = args.get("initDirectory")
        if init_directory is None:
            init_directory = os.path.abspath(os.path.expanduser("~"))
        init_directory = init_directory.replace("\\", "/")
        default_directory_info = _DefaultDirectoryInfo(
            self._get_partitions(), init_directory, self._get_directory_list(init_directory)
        )

        self.send({"defaultDirectoryInfo": default_directory_info.to_dict()})

    def msg_get_directory_list(self, args: dict[str, typing.Any]) -> None:
        path: str = args.get("path")
        self._logger.info(f"get directory list: {path}")
        if path is None:
            return
        path = path.replace("\\", "/")
        directory_list = self._get_directory_list(path)
        self._logger.info(f"directory list: {directory_list}")
        self.send({"directoryList": [d.to_dict() for d in directory_list]})

    @traitlets.observe("trace_fetch_interval")
    def trace_fetch_interval_changed(self, change) -> None:
        if change.get("new"):
            self.acquisition.trace_fetch_interval = change["new"]

    def _get_partitions(self) -> list[str]:
        partitions = []
        system = platform.system()

        if system == "Windows":
            import string
            from ctypes import windll

            try:
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        partitions.append(f"{letter}:/")
                    bitmask >>= 1
            except Exception as e:
                self._logger.error(f"Error getting partitions on Windows: {e}")
        elif system == "Linux":
            try:
                with open("/proc/mounts") as f:
                    for line in f:
                        if line.startswith("/dev/"):
                            parts = line.split()
                            partitions.append(parts[1])
            except Exception as e:
                self._logger.error(f"Error getting partitions on Linux: {e}")

        return partitions

    def _get_directory_list(self, directory: str) -> list["_DirectoryListNode"]:
        directory_list = []
        try:
            path = pathlib.Path(directory)
            if path.is_dir():
                for item in path.iterdir():
                    directory_list.append(_DirectoryListNode(name=item.name, type="folder"))
        except Exception as e:
            self._logger.error(f"Error accessing directory {directory}: {e}")

        return directory_list


@dataclass
class _DirectoryListNode:
    name: str
    type: str

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
        }


@dataclass
class _DefaultDirectoryInfo:
    partitions: list[str]
    path: str
    directory_list: list[_DirectoryListNode]

    def to_dict(self):
        return {
            "partitions": self.partitions,
            "path": self.path,
            "directoryList": [item.to_dict() for item in self.directory_list],
        }
