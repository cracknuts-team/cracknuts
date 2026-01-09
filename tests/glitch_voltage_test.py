from pico_get_avg import PicoScopeAverager
from cracknuts.cracker.cracker_g1 import CrackerG1
import time
import matplotlib.pyplot as plt


pico = PicoScopeAverager(sample_count=10000, voltage_range_v=10)

g1 = CrackerG1('192.168.0.10')

g1.connect(force_update_bin=True, force_write_default_config=True)

print(g1.get_firmware_version())

code_voltage_dict = {}
# code_voltage_csv_path = "test_g_vcc.csv"
# code_voltage_csv_path = "test_g_vcc2.csv"
# code_voltage_csv_path = "test_g_gnd.csv"
# code_voltage_csv_path = "test_g_gnd2.csv"
code_voltage_csv_path = "test_g_clock.csv"

code_voltage_csv = open(code_voltage_csv_path, 'w+', encoding='utf-8')
code_voltage_csv.write('code,voltage\n')

g1.nut_voltage_disable()
g1.register_write(base_address=0x43c10000, offset=0x1C4, data=1) # 禁止 clock
time.sleep(1)
g1.nut_voltage_enable()
g1.register_write(base_address=0x43c10000, offset=0x1D0, data=25) # 配置clock的长度
g1.register_write(base_address=0x43c10000, offset=0x1C4, data=0) # 使能 clock


for i in range(0x0000, 0x03ff+1):
    # g1.register_write(0x43c10000,0x150, i) # vcc vnormal
    # g1.register_write(0x43c10000,0x190, i) # gnd vnormal
    g1.register_write(base_address=0x43c10000, offset=0x1D4, data=i) # clock  配置时钟所有的值都是一样的便于测量电压
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