# Copyright 2024 CrackNuts. All rights reserved.

from cracknuts.acquisition import Acquisition
from cracknuts.cracker.stateful_cracker import StatefulCracker

from cracknuts.jupyter.acquisition_panel import AcquisitionPanelWidget
from cracknuts.jupyter.cracker_panel import CrackerPanelWidget
from cracknuts.jupyter.cracknuts_panel import CracknutsPanelWidget
from cracknuts.jupyter.trace_analysis_panel import TraceAnalysisPanelWidget
from cracknuts.jupyter.trace_panel import TraceMonitorPanelWidget


def display_cracknuts_panel(acq: Acquisition):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    cnpw = CracknutsPanelWidget(acquisition=acq)
    cnpw.sync_config()
    cnpw.bind()
    return cnpw


def display_trace_analysis_panel():
    return TraceAnalysisPanelWidget()


def display_trace_monitor_panel(acq: Acquisition):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    return TraceMonitorPanelWidget(acquisition=acq)


def display_acquisition_panel(acq: Acquisition):
    acq.sample_length = -1  # ignore the sample_length of acquisition when use ui.
    acqw = AcquisitionPanelWidget(acquisition=acq)
    acqw.sync_config()
    return acqw


def display_cracker_panel(cracker: StatefulCracker):
    cpw = CrackerPanelWidget(cracker=cracker)
    cpw.sync_config()
    cpw.bind()
    return cpw


__all__ = [
    "display_cracknuts_panel",
    "display_trace_analysis_panel",
    "display_acquisition_panel",
    "display_cracker_panel",
]
