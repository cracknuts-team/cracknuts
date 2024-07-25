from nutcracker.cracker.basic_cracker import BasicCracker

basic_device = BasicCracker(server_address=('127.0.0.1', 65432))
basic_device.connect()
print('====', basic_device.echo('11223344'))
print('++++', basic_device.echo('556677'))
# basic_device.disconnect()
