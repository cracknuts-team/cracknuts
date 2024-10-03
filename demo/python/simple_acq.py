from cracknuts.acquisition import Acquisition
from cracknuts.acquisition.acquisition import AcqProgress
from cracknuts.cracker.basic_cracker import CrackerS1
from cracknuts.cracker.cracker import Cracker
from cracknuts.cracker.stateful_cracker import StatefulCracker


class SimpleTestAcq(Acquisition):

    def _do_run(self, test: bool = True, count: int = 1, sample_offset: int = None,
                trigger_judge_wait_time: float | None = None, trigger_judge_timeout: float | None = None,
                do_error_max_count: int | None = None, do_error_handler_strategy: int | None = None):
        trace_index = 0
        self._progress_changed(AcqProgress(trace_index, self.trace_count))
        while self._status != 0 and self.trace_count - trace_index != 0:
            cracker.osc_force()
            cracker.osc_is_triggered()
            self._last_wave = self._get_waves(
                self.sample_offset,
                self.cracker.get_current_config().scrat_sample_len,
            )
            trace_index += 1
            self._current_trace_count = trace_index
            self._progress_changed(AcqProgress(trace_index, self.trace_count))

    def pre_do(self):
        self.cracker.osc_force()

    def init(self):
        pass

    def do(self):
        pass


sample_len = 1000
trace_count = 1000

cracker_s1 = CrackerS1()
cracker = StatefulCracker(cracker_s1)

cracker.set_uri('cnp://192.168.0.10:8080')
cracker.connect()
cracker.osc_sample_len(sample_len)

acq = SimpleTestAcq(cracker)
acq.run(count=trace_count)
