from cracknuts.cracker.basic_cracker import CrackerS1

basic_device = CrackerS1(server_address=('127.0.0.1', 65432))
basic_device.connect()
print('====', basic_device.echo('11223344'))
print('++++', basic_device.echo('556677'))
# basic_device.disconnect()
