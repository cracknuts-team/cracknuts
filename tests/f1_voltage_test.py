from cracknuts.cracker import CrackerF1
from pico_get_avg import PicoScopeAverager
from cracknuts.cracker.cracker_g1 import CrackerG1
import time
import matplotlib.pyplot as plt


pico = PicoScopeAverager(sample_count=10000, voltage_range_v=10)

f1 = CrackerF1('192.168.0.19')

f1.connect(force_update_bin=True, force_write_default_config=True)

print(f1.get_firmware_version())

code_voltage_dict = {}
# code_voltage_csv_path = "test_int.csv"
# code_voltage_csv_path = "test_ddr.csv"
# code_voltage_csv_path = "test_aux.csv"
code_voltage_csv_path = "test_io.csv"
# code_voltage_csv_path = "test_bak.csv"

code_voltage_csv = open(code_voltage_csv_path, 'w+', encoding='utf-8')
code_voltage_csv.write('code,voltage\n')

f1.register_write(base_address=0x43C1_0000, offset=0x1004, data=0)
f1.register_write(base_address=0x43C1_0000, offset=0x1008, data=0b111111)

for i in range(0x0000, 0x00ff+1):
    # f1.register_write(base_address=0x43C1_0000, offset=0x1010, data=(16 << 8) | (i & 0xFF))
    # f1.register_write(base_address=0x43C1_0000, offset=0x1014, data=(16 << 8) | (i & 0xFF))
    # f1.register_write(base_address=0x43C1_0000, offset=0x1018, data=(16 << 8) | (i & 0xFF))
    f1.register_write(base_address=0x43C1_0000, offset=0x101C, data=(16 << 8) | (i & 0xFF))
    # f1.register_write(base_address=0x43C1_0000, offset=0x1020, data=(16 << 8) | (i & 0xFF))
    time.sleep(0.5)
    voltage_mv = pico.read_avg_voltage_mv()
    print(f"0x{i:04x}:\t{voltage_mv/1000:.2f}")
    code_voltage_dict[i] = voltage_mv
    code_voltage_csv.write(f'{i:04x},{voltage_mv}\n')

code_voltage_csv.close()
pico.close()

# 准备数据
x = list(code_voltage_dict.keys())
y = list(code_voltage_dict.values())

# 绘图
plt.figure(figsize=(10, 5))
plt.plot(x, y, marker='o')
plt.title("Injection Voltage Curve")
plt.xlabel("Hex Address")
plt.ylabel("Voltage")
plt.grid(True)

# 设置 x 轴刻度为 4 位十六进制
plt.xticks(x, [f'0x{val:04X}' for val in x], rotation=45)

plt.tight_layout()
plt.show()