from cracknuts import CrackerS1

param_baudrate = (115200, 38400, 57600, 38400, 9600)
param_stopbits = (1, 2)
param_parity = ('N', 'E', 'O')

s1 = CrackerS1('192.168.0.10')
s1.connect(force_update_bin=True, force_write_default_config=True)
s1.uart_io_enable()
s1.osc_trigger_source('P')

tx_data = bytes.fromhex('11 22')

param_list = []

for baudrate in param_baudrate:
    for stopbits in param_stopbits:
        for parity in param_parity:
            param_list.append({
                "baudrate": baudrate,
                "stopbits": stopbits,
                "parity": parity
            })
            # print(f"Testing with baudrate={baudrate}, stopbits={stopbits}, parity={parity}")
            # dynamic_serial_server = DynamicSerialServer(baudrate=baudrate, stopbits=stopbits, parity=parity)
            # dynamic_serial_server.start()
            # s, r = s1.uart_transmit_receive(tx_data=tx_data, is_trigger=True, timeout=10000, rx_count=len(tx_data))
            #
            # assert r == tx_data
            # dynamic_serial_server.stop()

print(param_list)