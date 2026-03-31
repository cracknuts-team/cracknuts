# Copyright 2024 CrackNuts. All rights reserved.

"""
arm_a1.py - 三轴串联机械臂驱动与运动规划

物理结构：
  轴0：底座旋转盘      (0~58000 pulses → 0~328.09°)
  轴1：大臂俯仰关节    (0~17700 pulses → 9.14°~106.14°，相对立柱竖直方向)
  轴2：小臂俯仰关节    (0~15920 pulses → 126.33°~29.0°，大臂与小臂夹角)

机械参数：
  L1 = 200mm  大臂长度
  L2 = 200mm  小臂长度
  H  = 138mm  立柱高度（底座到轴1旋转中心）
"""

import math
import time
import threading
from enum import Enum

from pymodbus.client import ModbusTcpClient


# ─────────────────────────────────────────────────────────────────
# ArmA1Driver — Modbus TCP 硬件驱动层
# ─────────────────────────────────────────────────────────────────


class ArmA1Driver:
    """三轴机械臂 Modbus TCP 低级驱动。

    轴范围：
      轴0: 0~58000 pulses
      轴1: 0~17700 pulses
      轴2: 0~15920 pulses
    """

    _AXIS_MAX = [58000, 17700, 15920]

    def __init__(self, ip: str, port: int = 502, slave: int = 255):
        self.haveOrigin = False
        self.slave = slave
        self.client = ModbusTcpClient(host=ip, port=port)
        self.connect()
        self.axis_value = [0, 0, 0]

    def connect(self):
        self.client.connect()
        if not self.client.connected:
            print("连接失败")

    def close(self):
        self.client.close()

    def get_status(self, axis: int = 0):
        result = self.client.read_holding_registers(address=12000 + axis * 6, count=6, slave=self.slave)
        if result.isError():
            print(f"读取寄存器12000失败:{result}")
            return None
        result.registers = [
            result.registers[i] << 16 | result.registers[i + 1] for i in range(0, len(result.registers), 2)
        ]
        if result.registers[1] & 0x80000000:
            result.registers[1] -= 0x100000000
        if result.registers[2] & 0x80000000:
            result.registers[2] -= 0x100000000
        return result.registers

    def set_speed(
        self, axis: int = 0, begin: int = 1000, accel: int = 200, run: int = 6400, end: int = 1000, decel: int = 200
    ):
        temp = [
            (run >> 16) & 0xFFFF,
            run & 0xFFFF,
            (begin >> 16) & 0xFFFF,
            begin & 0xFFFF,
            accel & 0xFFFF,
            decel & 0xFFFF,
            (end >> 16) & 0xFFFF,
            end & 0xFFFF,
        ]
        result = self.client.write_registers(address=10100 + axis * 100 + 20, values=temp, slave=self.slave)
        if result.isError():
            print(f"写寄存器10100失败:{result}")
            return False
        return True

    def go_origin(self, axis: int = 0, speed: int = 0):
        temp = [(speed >> 16) & 0xFFFF, speed & 0xFFFF]
        result = self.client.write_registers(address=12680 + axis * 2, values=temp, slave=self.slave)
        if result.isError():
            print(f"写寄存器12680失败:{result}")
            return False
        return True

    def move(self, axis: int = 0, pulses: int = 6400):
        temp = [(pulses >> 16) & 0xFFFF, pulses & 0xFFFF]
        result = self.client.write_registers(address=12160 + axis * 2, values=temp, slave=self.slave)
        if result.isError():
            print(f"写寄存器12160失败:{result}, axis={axis}")
            return False
        return True

    def stop(self, axis: int = 0, pulses: int = 0):
        """停止运行。pulses=0 急停，pulses=-1 按减速时间停止。"""
        temp = [(pulses >> 16) & 0xFFFF, pulses & 0xFFFF]
        result = self.client.write_registers(address=12096 + axis * 2, values=temp, slave=self.slave)
        if result.isError():
            print(f"写寄存器12096失败:{result}")
            return False
        return True

    # ── 三轴批量操作 ──────────────────────────────────────────────

    def set_speed_3axis(self):
        for i in range(3):
            self.set_speed(axis=i)

    def go_origin_3axis(self):
        for i in range(3):
            self.go_origin(axis=i)
        self.__wait_origin_3axis()
        self.wait_pulses_3axis()
        self.haveOrigin = True

    def get_have_origin(self) -> bool:
        return self.haveOrigin

    def get_status_3axis(self):
        return self.get_status(0), self.get_status(1), self.get_status(2)

    def move_3axis(self, value: list[int]):
        for i in range(3):
            value[i] = max(0, min(self._AXIS_MAX[i], value[i]))
        self.axis_value = list(value)
        for i in range(3):
            self.move(axis=i, pulses=value[i])

    def stop_3axis(self):
        for i in range(3):
            self.stop(axis=i)

    def wait_pulses_3axis(self, time_out: float = 5):
        duration = 0.0
        while True:
            time.sleep(0.01)
            duration += 0.01
            if duration > time_out:
                break
            ts0, ts1, ts2 = self.get_status_3axis()
            if None in (ts0, ts1, ts2):
                continue
            print(
                f"轴0 坐标:{ts0[1]} 脉冲:{int(ts0[0]) >> 3 & 1} | "
                f"轴1 坐标:{ts1[1]} 脉冲:{int(ts1[0]) >> 3 & 1} | "
                f"轴2 坐标:{ts2[1]} 脉冲:{int(ts2[0]) >> 3 & 1}"
            )
            if (
                ts0[1] == self.axis_value[0]
                and ts1[1] == self.axis_value[1]
                and ts2[1] == self.axis_value[2]
                and int(ts0[0]) >> 3 & 1 == 0
                and int(ts1[0]) >> 3 & 1 == 0
                and int(ts2[0]) >> 3 & 1 == 0
            ):
                break

    def __wait_origin_3axis(self, time_out: float = 5):
        duration = 0.0
        while True:
            time.sleep(0.01)
            duration += 0.01
            if duration > time_out:
                break
            ts0, ts1, ts2 = self.get_status_3axis()
            if None in (ts0, ts1, ts2):
                continue
            print(f"归零 轴0:{int(ts0[0]) >> 6 & 1} 轴1:{int(ts1[0]) >> 6 & 1} 轴2:{int(ts2[0]) >> 6 & 1}")
            if int(ts0[0]) >> 6 & 1 == 1 and int(ts1[0]) >> 6 & 1 == 1 and int(ts2[0]) >> 6 & 1 == 1:
                break


# ─────────────────────────────────────────────────────────────────
# RobotArmKinematics — 正逆运动学求解器
# ─────────────────────────────────────────────────────────────────


class RobotArmKinematics:
    """三轴串联机械臂运动学（轴0旋转 + 轴1/2平面2R机构）。

    正运动学：
      θ2_DH = 180° − α2
      ψ = θ1 + θ2_DH
      R = L1·sin(θ1) + L2·sin(ψ)
      Z = H + L1·cos(θ1) + L2·cos(ψ)
      X = R·cos(θ0),  Y = R·sin(θ0)

    逆运动学（2R平面臂余弦定理闭合解，elbow-forward）：
      θ0 = atan2(Y, X)
      d² = R² + Z'²,  Z' = Z − H
      cos(θ2_DH) = (d² − L1² − L2²) / (2·L1·L2)
      β = atan2(R, Z'),  γ = atan2(L2·sin(θ2_DH), L1 + L2·cos(θ2_DH))
      θ1 = β − γ,  α2 = 180° − θ2_DH
    """

    L1 = 200.0
    L2 = 200.0
    H = 138.0

    PULSE0_MAX = 58000
    THETA0_MAX = 328.09
    PULSE1_MAX = 17700
    THETA1_AT_0 = 9.14
    THETA1_AT_MAX = 106.14
    PULSE2_MAX = 15920
    ALPHA2_AT_0 = 126.33
    ALPHA2_AT_MAX = 29.0

    def pulses_to_angles(self, pulses: list[int]) -> tuple[float, float, float]:
        """脉冲值 → (θ0°, θ1°, α2°)"""
        p0, p1, p2 = pulses
        theta0 = p0 * self.THETA0_MAX / self.PULSE0_MAX
        theta1 = self.THETA1_AT_0 + p1 * (self.THETA1_AT_MAX - self.THETA1_AT_0) / self.PULSE1_MAX
        alpha2 = self.ALPHA2_AT_0 + p2 * (self.ALPHA2_AT_MAX - self.ALPHA2_AT_0) / self.PULSE2_MAX
        return theta0, theta1, alpha2

    def angles_to_pulses(self, theta0: float, theta1: float, alpha2: float) -> list[int]:
        """(θ0°, θ1°, α2°) → 脉冲值（含限位钳制）"""
        p0 = theta0 * self.PULSE0_MAX / self.THETA0_MAX
        p1 = (theta1 - self.THETA1_AT_0) * self.PULSE1_MAX / (self.THETA1_AT_MAX - self.THETA1_AT_0)
        p2 = (alpha2 - self.ALPHA2_AT_0) * self.PULSE2_MAX / (self.ALPHA2_AT_MAX - self.ALPHA2_AT_0)
        return [
            int(max(0, min(self.PULSE0_MAX, p0))),
            int(max(0, min(self.PULSE1_MAX, p1))),
            int(max(0, min(self.PULSE2_MAX, p2))),
        ]

    def forward(self, pulses: list[int]) -> list[float]:
        """脉冲值 → [X, Y, Z] mm"""
        theta0, theta1, alpha2 = self.pulses_to_angles(pulses)
        theta2_dh = 180.0 - alpha2
        psi = theta1 + theta2_dh

        t0 = math.radians(theta0)
        t1 = math.radians(theta1)
        ps = math.radians(psi)

        R = self.L1 * math.sin(t1) + self.L2 * math.sin(ps)
        Z = self.H + self.L1 * math.cos(t1) + self.L2 * math.cos(ps)
        return [round(R * math.cos(t0), 2), round(R * math.sin(t0), 2), round(Z, 2)]

    def inverse(self, coords: list[float]) -> list[int]:
        """[X, Y, Z] mm → 脉冲值"""
        X, Y, Z = coords

        theta0_deg = math.degrees(math.atan2(Y, X))
        if theta0_deg < 0:
            theta0_deg += 360.0

        R = math.sqrt(X * X + Y * Y)
        Z_prime = Z - self.H

        d_sq = R * R + Z_prime * Z_prime
        cos_t2 = (d_sq - self.L1**2 - self.L2**2) / (2.0 * self.L1 * self.L2)
        cos_t2 = max(-1.0, min(1.0, cos_t2))
        t2 = math.acos(cos_t2)

        beta = math.atan2(R, Z_prime)
        gamma = math.atan2(self.L2 * math.sin(t2), self.L1 + self.L2 * math.cos(t2))
        theta1_deg = math.degrees(beta - gamma)
        alpha2_deg = 180.0 - math.degrees(t2)

        return self.angles_to_pulses(theta0_deg, theta1_deg, alpha2_deg)

    def in_workspace(self, coords: list[float]) -> tuple[bool, str]:
        """检查坐标是否可达，返回 (可达?, 原因说明)"""
        X, Y, Z = coords

        if Z < 0:
            return False, f"Z={Z:.1f}mm 低于底座（Z≥0）"

        theta0 = math.degrees(math.atan2(Y, X))
        if theta0 < 0:
            theta0 += 360.0
        if not (0.0 <= theta0 <= self.THETA0_MAX):
            return False, f"底座旋转角 {theta0:.1f}° 超出范围 [0°, {self.THETA0_MAX}°]"

        R = math.sqrt(X * X + Y * Y)
        Z_prime = Z - self.H
        d_sq = R * R + Z_prime * Z_prime

        if d_sq > (self.L1 + self.L2) ** 2:
            return False, f"目标距离 {math.sqrt(d_sq):.1f}mm 超出最大臂展 {self.L1 + self.L2:.0f}mm"

        cos_t2 = (d_sq - self.L1**2 - self.L2**2) / (2.0 * self.L1 * self.L2)
        if not (-1.0 <= cos_t2 <= 1.0):
            return False, "几何上不可达"

        t2 = math.acos(cos_t2)
        beta = math.atan2(R, Z_prime)
        gamma = math.atan2(self.L2 * math.sin(t2), self.L1 + self.L2 * math.cos(t2))
        theta1 = math.degrees(beta - gamma)
        alpha2 = 180.0 - math.degrees(t2)

        if not (self.THETA1_AT_0 <= theta1 <= self.THETA1_AT_MAX):
            return False, f"大臂角 {theta1:.1f}° 超出范围 [{self.THETA1_AT_0}°, {self.THETA1_AT_MAX}°]"
        if not (self.ALPHA2_AT_MAX <= alpha2 <= self.ALPHA2_AT_0):
            return False, f"小臂夹角 {alpha2:.1f}° 超出范围 [{self.ALPHA2_AT_MAX}°, {self.ALPHA2_AT_0}°]"

        return True, "ok"

    def dist(self, pulses_a: list[int], pulses_b: list[int]) -> float:
        """两个脉冲位置之间的笛卡尔距离（mm）"""
        a = self.forward(pulses_a)
        b = self.forward(pulses_b)
        return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


# ─────────────────────────────────────────────────────────────────
# ArmA1 — 工具坐标系 API
# ─────────────────────────────────────────────────────────────────


class MotionState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    STOPPING = "stopping"


class ArmA1:
    """三轴串联机械臂工具坐标系 API。

    快速上手：
        mc = ArmA1("192.168.0.25")
        mc.init()                                # 归零（必须）
        print(mc.get_coords())                   # 读取当前位姿 [X,Y,Z,rx,ry,rz]
        mc.send_coords([300, 0, 200], speed=80)  # 移动到目标坐标
        mc.stop()                                # 急停

    运动模式（send_coords mode参数）：
        mode=0  关节空间直接移动（默认，最快）
        mode=1  笛卡尔线性插补（路径为空间直线）
    """

    _ESTIMATED_SPEED_MM_S = 80.0
    _LINEAR_STEP_MM = 20.0

    def __init__(self, ip: str, port: int = 502, slave: int = 255):
        self._lock = threading.Lock()
        self._state = MotionState.IDLE
        self._arm = ArmA1Driver(ip=ip, port=port, slave=slave)
        self._kin = RobotArmKinematics()
        self._pose = [0.0] * 6

    def init(self) -> bool:
        """初始化：设置速度参数 → 三轴归零。必须在运动操作前调用。"""
        print("[ArmA1] 设置三轴速度参数...")
        self._arm.set_speed_3axis()
        print("[ArmA1] 执行三轴归零，请等待...")
        self._arm.go_origin_3axis()
        ok = self._arm.get_have_origin()
        if ok:
            self._pose[:3] = self._kin.forward([0, 0, 0])
            print(f"[ArmA1] 归零完成，原点位姿: {self._pose[:3]}")
        else:
            print("[ArmA1] 归零失败！")
        return ok

    def get_coords(self) -> list[float]:
        """获取当前末端工具坐标 [X, Y, Z, rx, ry, rz]，单位 mm。"""
        ts0, ts1, ts2 = self._arm.get_status_3axis()
        if None in (ts0, ts1, ts2):
            return self._pose[:]
        self._pose[:3] = self._kin.forward([ts0[1], ts1[1], ts2[1]])
        return self._pose[:]

    def send_coords(self, coords: list[float], speed: float = 50.0, mode: int = 0) -> bool:
        """移动末端到目标工具坐标。

        :param coords: 目标坐标 [X, Y, Z] 或 [X, Y, Z, rx, ry, rz]，单位 mm
        :param speed:  运动速度 (mm/s)，用于超时估算
        :param mode:   0=关节空间直接移动；1=笛卡尔线性插补
        """
        if not self._arm.get_have_origin():
            print("[ArmA1] 错误：未归零，请先调用 init()")
            return False

        target_xyz = list(coords[:3])
        ok, reason = self._kin.in_workspace(target_xyz)
        if not ok:
            print(f"[ArmA1] 目标超出工作空间：{reason}")
            return False

        with self._lock:
            if self._state != MotionState.IDLE:
                print(f"[ArmA1] 当前状态 {self._state.value}，拒绝新指令")
                return False
            self._state = MotionState.MOVING

        try:
            ts0, ts1, ts2 = self._arm.get_status_3axis()
            if None in (ts0, ts1, ts2):
                raise RuntimeError("读取当前位置失败")

            current_pulses = [ts0[1], ts1[1], ts2[1]]
            target_pulses = self._kin.inverse(target_xyz)

            if mode == 1:
                success = self._move_linear(current_pulses, target_pulses, speed)
            else:
                success = self._move_direct(current_pulses, target_pulses, speed)

            if success and len(coords) >= 6:
                self._pose[3:] = list(coords[3:6])
            return success

        except Exception as e:
            print(f"[ArmA1] send_coords 异常: {e}")
            return False
        finally:
            with self._lock:
                if self._state != MotionState.STOPPING:
                    self._state = MotionState.IDLE

    # ── 方向点动 ──────────────────────────────────────────────────

    def move_up(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """Z 轴向上移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0], cur[1], cur[2] + step], speed)

    def move_down(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """Z 轴向下移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0], cur[1], cur[2] - step], speed)

    def move_left(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """Y 轴负方向移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0], cur[1] - step, cur[2]], speed)

    def move_right(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """Y 轴正方向移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0], cur[1] + step, cur[2]], speed)

    def move_forward(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """X 轴正方向移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0] + step, cur[1], cur[2]], speed)

    def move_back(self, step: float = 10.0, speed: float = 30.0) -> bool:
        """X 轴负方向移动 step mm"""
        cur = self.get_coords()
        return self.send_coords([cur[0] - step, cur[1], cur[2]], speed)

    def stop(self) -> bool:
        """紧急停止（所有轴立即停止）"""
        with self._lock:
            self._state = MotionState.STOPPING
        self._arm.stop_3axis()
        with self._lock:
            self._state = MotionState.IDLE
        print("[ArmA1] 已急停")
        return True

    def close(self):
        """关闭 Modbus TCP 连接"""
        self._arm.close()
        print("[ArmA1] 连接已关闭")

    def _move_direct(self, current_pulses: list[int], target_pulses: list[int], speed_mm_s: float) -> bool:
        with self._lock:
            if self._state == MotionState.STOPPING:
                return False
        dist = self._kin.dist(current_pulses, target_pulses)
        timeout = self._calc_timeout(dist, speed_mm_s)
        self._arm.move_3axis(list(target_pulses))
        self._arm.wait_pulses_3axis(time_out=timeout)
        return True

    def _move_linear(self, current_pulses: list[int], target_pulses: list[int], speed_mm_s: float) -> bool:
        start = self._kin.forward(current_pulses)
        target = self._kin.forward(target_pulses)
        delta = [target[i] - start[i] for i in range(3)]
        dist = math.sqrt(sum(d * d for d in delta))

        if dist < 0.1:
            return True

        steps = max(1, int(math.ceil(dist / self._LINEAR_STEP_MM)))
        for k in range(1, steps + 1):
            with self._lock:
                if self._state == MotionState.STOPPING:
                    print(f"[ArmA1] 线性插补被中断（第{k}/{steps}段）")
                    return False
            t = k / steps
            pt = [start[i] + delta[i] * t for i in range(3)]
            seg_pulses = self._kin.inverse(pt)
            timeout = self._calc_timeout(dist / steps, speed_mm_s)
            self._arm.move_3axis(list(seg_pulses))
            self._arm.wait_pulses_3axis(time_out=timeout)

        return True

    @staticmethod
    def _calc_timeout(dist_mm: float, speed_mm_s: float) -> float:
        if speed_mm_s <= 0:
            speed_mm_s = 10.0
        return max(5.0, dist_mm / speed_mm_s * 2.0)
