"""
test_arm_examples.py - 机械臂硬件实测脚本

用法：
    python test_arm_examples.py           # 运行演示序列
    python test_arm_examples.py --probe   # 只读取当前坐标，不运动
    python test_arm_examples.py --kin     # 只做运动学数学验证，不连接硬件
"""

import sys
import math
import time
from cracknuts.arm.arm_a1 import ArmA1, RobotArmKinematics

ARM_IP = "192.168.0.25"


# ─────────────────────────────────────────────────────────────────
# 运动学自验证（无需硬件）
# ─────────────────────────────────────────────────────────────────

def verify_kinematics():
    kin = RobotArmKinematics()
    print("=" * 55)
    print("运动学自验证（正逆运动学一致性）")
    print("=" * 55)

    samples = [
        ([0,     0,     0],    "原点"),
        ([10500, 7700,  1200], "工作位 A"),
        ([10500, 7700,  6400], "工作位 A 下探"),
        ([10500, 1200,  1200], "大臂收缩"),
        ([6400,  7700,  1200], "底座旋转"),
        ([29000, 8850,  7960], "中间区域"),
    ]

    print(f"\n{'脉冲':>30}  {'X':>7} {'Y':>7} {'Z':>7}  {'误差':>6}")
    print("-" * 65)
    all_ok = True
    for pulses, label in samples:
        xyz    = kin.forward(pulses)
        p_back = kin.inverse(xyz)
        xyz2   = kin.forward(p_back)
        err    = math.sqrt(sum((xyz[i] - xyz2[i]) ** 2 for i in range(3)))
        ok_str = "✓" if err < 1.0 else "✗"
        print(f"  {label:<14} {str(pulses):>20}  "
              f"{xyz[0]:7.1f} {xyz[1]:7.1f} {xyz[2]:7.1f}  {err:5.2f}mm {ok_str}")
        if err >= 1.0:
            all_ok = False

    print()
    if all_ok:
        print("✓ 所有样本点正逆运动学一致性 < 1mm")
    else:
        print("✗ 存在误差超标的样本点，请检查运动学参数")
    print()


# ─────────────────────────────────────────────────────────────────
# 只读探测（连接硬件，不移动）
# ─────────────────────────────────────────────────────────────────

def probe(ip=ARM_IP):
    print(f"连接 {ip}...")
    mc = ArmA1(ip)
    ts0, ts1, ts2 = mc._arm.get_status_3axis()
    print("\n当前状态：")
    print(f"  归零完成  : {mc._arm.get_have_origin()}")
    print(f"  当前坐标  : {mc.get_coords()}")
    print(f"  各轴脉冲  : 轴0={ts0[1] if ts0 else None}  轴1={ts1[1] if ts1 else None}  轴2={ts2[1] if ts2 else None}")
    mc.close()


# ─────────────────────────────────────────────────────────────────
# 完整演示序列
# ─────────────────────────────────────────────────────────────────

def demo(ip=ARM_IP):
    print("=" * 55)
    print("机械臂硬件演示")
    print("=" * 55)

    mc = ArmA1(ip)

    print("\n[1] 初始化归零...")
    assert mc.init(), "归零失败，请检查硬件连接"

    origin = mc.get_coords()
    print(f"\n[2] 原点坐标: {origin}")

    kin   = RobotArmKinematics()
    pos_a = kin.forward([10500, 7700, 1200])
    print(f"\n[3] 移动到工作位 A: {pos_a}")
    assert mc.send_coords(pos_a, speed=80), "移动失败"
    print(f"    到达: {mc.get_coords()}")

    safe_pos = kin.forward([10500, 4000, 2000])
    print(f"\n[4] 移动到安全退出位: {safe_pos}")
    mc.send_coords(safe_pos, speed=50)

    mc.close()
    print("\n演示完成")


# ─────────────────────────────────────────────────────────────────
# 矩形绘制演示
# ─────────────────────────────────────────────────────────────────

def draw_rectangle(ip=ARM_IP,
                   cx=200.0, cy=200.0, z=200.0,
                   width=100.0, height=60.0,
                   speed=40.0):
    """用末端在笛卡尔空间绘制一个矩形（mode=0 和 mode=1 各跑一次）。"""
    mc = ArmA1(ip)

    print("\n[矩形] 初始化归零...")
    assert mc.init(), "归零失败，请检查硬件连接"
    time.sleep(2)

    corners = [
        [300, 0,  200],
        [300, 10, 200],
        [290, 10, 200],
        [290, 0,  200],
        [300, 0,  200],
    ]

    print("[矩形] mode=0 关节空间直接移动")
    for pt in corners:
        mc.send_coords(pt, speed=80, mode=0)
        time.sleep(2)

    time.sleep(3)
    print("\n[矩形] 再次归零...")
    assert mc.init(), "归零失败，请检查硬件连接"
    time.sleep(2)

    print("[矩形] mode=1 笛卡尔线性插补")
    for pt in corners:
        mc.send_coords(pt, speed=80, mode=1)
        time.sleep(2)

    mc.close()
    print("\n矩形绘制完成")


# ─────────────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--kin" in sys.argv:
        verify_kinematics()
    elif "--probe" in sys.argv:
        verify_kinematics()
        probe()
    elif "--rect" in sys.argv:
        verify_kinematics()
        draw_rectangle()
    else:
        verify_kinematics()
        demo()
