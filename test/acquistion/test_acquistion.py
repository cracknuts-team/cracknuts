import time

from nutcracker.acquisition.acquisition import Acquisition


def test_acquisition_test_mode():
    acq = Acquisition(None)
    acq.on_wave_loaded(lambda waves: print(waves.shape))
    acq.test()
    time.sleep(10)


if __name__ == '__main__':
    test_acquisition_test_mode()
