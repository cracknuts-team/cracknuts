from cracknuts.acquisition import Acquisition
from cracknuts.mock.mock_cracker import MockCracker
from cracknuts.cracker.stateful_cracker import StatefulCracker

cracker = MockCracker()
stateful_cracker = StatefulCracker(cracker)
acq = Acquisition.builder().cracker(stateful_cracker).init(lambda _: None).do(lambda _: None)

stateful_cracker.sync_config_to_cracker()
