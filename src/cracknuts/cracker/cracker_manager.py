# Copyright 2024 CrackNuts. All rights reserved.

"""
CRKR Device Manager

A high-level Python client for discovering and managing CRKR devices on the network.
Supports continuous background scanning, device state tracking, and real-time callbacks.
"""

import argparse
import logging
import queue
import socket
import struct
import threading
import time
import random
from enum import Enum
from collections.abc import Callable

logger = logging.getLogger(__name__)

MAGIC = b"CRKR"
VERSION = 1
CMD_DISCOVER = 1
CMD_SET_IP = 2
CMD_ACK = 3

HEADER_FMT = "!4sBBHIHH"
ACK_FMT = "!I96s16s18s64s"
SET_IP_FMT = "!16s16s16sI"

PORT = 9769


class DeviceStatus(Enum):
    """Device connection status."""

    ONLINE = "online"
    OFFLINE = "offline"


def _pack_header(cmd: int, txid: int, payload_len: int) -> bytes:
    """Pack a CRKR packet header."""
    return struct.pack(HEADER_FMT, MAGIC, VERSION, cmd, 0, txid, payload_len, 0)


def _parse_ack(payload: bytes) -> dict:
    """Parse a CMD_ACK payload into a dictionary."""
    status, msg, ip, mac, hostname = struct.unpack(ACK_FMT, payload)
    return {
        "status": status,
        "msg": msg.split(b"\x00", 1)[0].decode("utf-8", "ignore"),
        "ip": ip.split(b"\x00", 1)[0].decode("utf-8", "ignore"),
        "mac": mac.split(b"\x00", 1)[0].decode("utf-8", "ignore"),
        "hostname": hostname.split(b"\x00", 1)[0].decode("utf-8", "ignore"),
    }


def _get_local_ips() -> list[str]:
    """Return all non-loopback IPv4 addresses on the local machine."""
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
        ips = list({info[4][0] for info in infos})
        return [ip for ip in ips if not ip.startswith("127.")]
    except OSError:
        return []


def _do_discover_on(
    bip: str,
    targets: list[str],
    timeout: float,
    retries: int,
    interval: float,
    verbose: bool,
    seen: set[tuple[str, str]],
    out: queue.Queue,
) -> None:
    """Perform discovery broadcasts from a specific bind IP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        sock.bind((bip, 0))
    except OSError as exc:
        logger.warning("bind %s failed (%s), skipping", bip, exc)
        sock.close()
        return

    for i in range(max(1, retries)):
        txid = random.getrandbits(32)
        pkt = _pack_header(CMD_DISCOVER, txid, 0)
        for bcast in targets:
            if verbose:
                logger.debug(
                    "send broadcast %s:%d via %s (try %d/%d)",
                    bcast,
                    PORT,
                    bip,
                    i + 1,
                    retries,
                )
            else:
                logger.info(
                    "Sending discovery to %s via %s (try %d/%d)...",
                    bcast,
                    bip,
                    i + 1,
                    retries,
                )
            sock.sendto(pkt, (bcast, PORT))

        start = time.time()
        while True:
            try:
                data, addr = sock.recvfrom(1024)
            except TimeoutError:
                break
            if time.time() - start > timeout:
                break
            if len(data) < struct.calcsize(HEADER_FMT):
                continue
            unpacked = struct.unpack_from(HEADER_FMT, data)
            magic, ver, cmd, r_txid = unpacked[0], unpacked[1], unpacked[2], unpacked[4]
            if magic != MAGIC or ver != VERSION or cmd != CMD_ACK or r_txid != txid:
                continue
            payload = data[struct.calcsize(HEADER_FMT) :]
            if len(payload) < struct.calcsize(ACK_FMT):
                continue
            ack = _parse_ack(payload[: struct.calcsize(ACK_FMT)])
            key = (ack.get("mac", ""), addr[0])
            if key in seen:
                continue
            seen.add(key)
            ack["from"] = addr[0]
            out.put(ack)

        if i < retries - 1 and interval > 0:
            time.sleep(interval)

    sock.close()


def _discover_once(
    bind_ip: str,
    broadcasts: list[str],
    timeout: float,
    retries: int,
    interval: float,
    verbose: bool,
) -> list[dict]:
    """
    Perform a single discovery scan and return all discovered devices.

    Args:
        bind_ip: Local IP to bind, or "auto"/""/"0.0.0.0" for auto-detection.
        broadcasts: List of broadcast addresses to send to.
        timeout: Socket timeout per retry (seconds).
        retries: Number of broadcast retries.
        interval: Interval between retries (seconds).
        verbose: Enable verbose logging.

    Returns:
        List of device dicts with keys: status, msg, ip, mac, hostname, from.
    """
    if bind_ip in ("0.0.0.0", "", "auto"):
        bind_ips = _get_local_ips() or ["0.0.0.0"]
    else:
        bind_ips = [bind_ip]

    out: queue.Queue = queue.Queue()
    seen: set[tuple[str, str]] = set()

    def worker() -> None:
        for bip in bind_ips:
            _do_discover_on(bip, broadcasts, timeout, retries, interval, verbose, seen, out)
        out.put(None)

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    results = []
    while True:
        item = out.get()
        if item is None:
            break
        results.append(item)

    return results


def discover_devices(
    broadcast: str = "255.255.255.255",
    scan_interval: float = 3.0,
    offline_grace: float = 15.0,
    device_timeout: float = 60.0,
) -> list[dict]:
    """
    Discover devices on the local network once.

    Args:
        broadcast: Broadcast address for discovery.
        scan_interval: Cached scan interval for manager-style callers.
        offline_grace: Cached offline grace period for manager-style callers.
        device_timeout: Cached device timeout for manager-style callers.

    Returns:
        List of discovered device dictionaries.
    """
    manager = CrackerManager(
        broadcast=broadcast,
        scan_interval=scan_interval,
        offline_grace=offline_grace,
        device_timeout=device_timeout,
        continuous=False,
    )
    return manager.discover_once()


def _set_ip(
    target_ip: str,
    new_ip: str,
    mask: str = "",
    gateway: str | None = None,
    delay_ms: int = 200,
) -> dict | None:
    """
    Send a CMD_SET_IP command to a target device.

    Args:
        target_ip: Current IP of the target device.
        new_ip: New IP address, or "dhcp" to enable DHCP mode.
        mask: Subnet mask or prefix length (ignored for DHCP).
        gateway: Default gateway (ignored for DHCP).
        delay_ms: Delay before applying changes (milliseconds).

    Returns:
        ACK dict with keys: status, msg, ip, mac, hostname, or None on timeout.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)

    txid = random.getrandbits(32)
    if new_ip == "dhcp":
        ip_bytes = b"dhcp\x00" + b"\x00" * 11
    else:
        ip_bytes = new_ip.encode("utf-8")[:15].ljust(16, b"\x00")
    payload = struct.pack(
        SET_IP_FMT,
        ip_bytes,
        (mask or "").encode("utf-8")[:15].ljust(16, b"\x00"),
        (gateway or "").encode("utf-8")[:15].ljust(16, b"\x00"),
        delay_ms,
    )
    pkt = _pack_header(CMD_SET_IP, txid, len(payload)) + payload
    sock.sendto(pkt, (target_ip, PORT))

    try:
        while True:
            data, _ = sock.recvfrom(1024)
            if len(data) < struct.calcsize(HEADER_FMT):
                continue
            unpacked = struct.unpack_from(HEADER_FMT, data)
            magic, ver, cmd, r_txid = unpacked[0], unpacked[1], unpacked[2], unpacked[4]
            if magic != MAGIC or ver != VERSION or cmd != CMD_ACK or r_txid != txid:
                continue
            payload = data[struct.calcsize(HEADER_FMT) :]
            ack = _parse_ack(payload[: struct.calcsize(ACK_FMT)])
            sock.close()
            return ack
    except TimeoutError:
        sock.close()
        logger.warning("set_ip: no response from %s (timeout)", target_ip)
        return None


class CrackerManager:
    """
    CrackerManager for continuous discovery and device management.

    CrackerManager automatically discovers CRKR devices on the network and maintains
    a real-time device list with online/offline status tracking. It supports
    callbacks for device discovery, updates, and loss events.

    Args:
        broadcast: Broadcast address for discovery (default: "255.255.255.255").
        scan_interval: Seconds between discovery scans (default: 3.0).
        offline_grace: Seconds without response before marking offline (default: 15.0).
        device_timeout: Seconds without response before removing device (default: 60.0).
        continuous: Start scanning immediately on creation (default: True).

    Example:
        >>> with CrackerManager() as manager:
        ...     time.sleep(5)
        ...     for device in manager.devices:
        ...         print(device)
        ['mac': 'AA:BB:CC:DD:EE:FF', 'ip': '192.168.0.100', ...]
    """

    def __init__(
        self,
        broadcast: str = "255.255.255.255",
        scan_interval: float = 3.0,
        offline_grace: float = 15.0,
        device_timeout: float = 60.0,
        continuous: bool = True,
    ):
        self._broadcast = broadcast
        self._scan_interval = scan_interval
        self._offline_grace = offline_grace
        self._device_timeout = device_timeout
        self._continuous = continuous

        self._devices: dict[str, dict] = {}
        self._running = False
        self._lock = threading.Lock()

        self._callbacks: dict[str, list[Callable]] = {
            "discovered": [],
            "updated": [],
            "lost": [],
        }

        self._thread: threading.Thread | None = None

        if self._continuous:
            self.start_discovery()

    @property
    def devices(self) -> list[dict]:
        """
        Return a snapshot of all discovered devices.

        Returns:
            List of device dicts (online and offline).
            Each dict contains: ip, mac, hostname, status, last_seen, last_ip_change.
        """
        with self._lock:
            self._update_device_statuses()
            return [dict(d) for d in self._devices.values()]

    @property
    def online_devices(self) -> list[dict]:
        """
        Return a snapshot of only online devices.

        Returns:
            List of device dicts with status "online".
        """
        with self._lock:
            self._update_device_statuses()
            return [dict(d) for d in self._devices.values() if d.get("status") == DeviceStatus.ONLINE.value]

    def start_discovery(self):
        """Start background discovery scanning (no-op if already running)."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()

    def stop_discovery(self):
        """Stop background discovery scanning and wait for thread to finish."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def discover_once(self) -> list[dict]:
        """
        Perform a single discovery scan without affecting the managed device list.

        Returns:
            List of device dicts discovered in this scan.
        """
        return _discover_once(
            bind_ip="auto",
            broadcasts=[self._broadcast],
            timeout=1.5,
            retries=2,
            interval=0.1,
            verbose=False,
        )

    def set_ip(
        self,
        target_ip: str,
        new_ip: str,
        mask: str = "",
        gateway: str | None = None,
        delay_ms: int = 200,
    ) -> dict | None:
        """
        Set the IP address or DHCP mode of a target device.

        When new_ip is "dhcp", the device's IP will be marked as "DHCP" in the
        manager's device list until it responds to the next discovery scan.

        Args:
            target_ip: Current IP of the target device.
            new_ip: New IP address, or "dhcp" to enable DHCP mode.
            mask: Subnet mask or prefix length (ignored for DHCP).
            gateway: Default gateway (ignored for DHCP).
            delay_ms: Delay before applying changes (milliseconds).

        Returns:
            ACK dict on success, None on timeout.
        """
        ack = _set_ip(
            target_ip=target_ip,
            new_ip=new_ip,
            mask=mask,
            gateway=gateway,
            delay_ms=delay_ms,
        )

        if ack is None:
            return None

        if new_ip == "dhcp":
            with self._lock:
                for device in self._devices.values():
                    if device.get("ip") == target_ip:
                        device["ip"] = "DHCP"
                        device["status"] = DeviceStatus.ONLINE.value
                        device["last_seen"] = time.time()
                        self._emit_callback("updated", device)
                        break
        else:
            if ack.get("status") == 0 and ack.get("mac"):
                self._update_or_add_device(ack)

        return ack

    def get_device(self, mac: str = None, ip: str = None) -> dict | None:
        """
        Find a device by MAC address or IP address.

        Args:
            mac: MAC address to search for.
            ip: IP address to search for.

        Returns:
            Device dict if found, None otherwise.
        """
        with self._lock:
            if mac:
                return dict(self._devices.get(mac))
            if ip:
                for d in self._devices.values():
                    if d.get("ip") == ip:
                        return dict(d)
        return None

    def on_discovered(self, callback: Callable[[dict], None]):
        """
        Register a callback for new device discovery events.

        Args:
            callback: Function accepting a device dict.
        """
        self._callbacks["discovered"].append(callback)

    def on_updated(self, callback: Callable[[dict], None]):
        """
        Register a callback for device update events.

        Called when a device's IP changes or status transitions (online/offline).

        Args:
            callback: Function accepting a device dict.
        """
        self._callbacks["updated"].append(callback)

    def on_lost(self, callback: Callable[[dict], None]):
        """
        Register a callback for device loss events.

        Called when a device is removed from the list due to timeout.

        Args:
            callback: Function accepting a device dict.
        """
        self._callbacks["lost"].append(callback)

    def _scan_loop(self):
        """Internal background scan loop."""
        while self._running:
            self._do_scan()
            time.sleep(self._scan_interval)

    def _do_scan(self):
        """Internal: perform one scan cycle and update device states."""
        results = _discover_once(
            bind_ip="auto",
            broadcasts=[self._broadcast],
            timeout=1.5,
            retries=2,
            interval=0.1,
            verbose=False,
        )

        seen_macs = set()
        for ack in results:
            mac = ack.get("mac", "")
            if not mac:
                continue
            seen_macs.add(mac)

            is_new = mac not in self._devices
            self._update_or_add_device(ack, is_new=is_new)

        with self._lock:
            self._update_device_statuses()
            to_remove = []
            now = time.time()
            for mac, device in self._devices.items():
                if mac not in seen_macs:
                    if device.get("status") == DeviceStatus.ONLINE.value:
                        if now - device.get("last_seen", 0) > self._offline_grace:
                            device["status"] = DeviceStatus.OFFLINE.value
                            self._emit_callback("updated", device)
                    else:
                        if now - device.get("last_seen", 0) > self._device_timeout:
                            to_remove.append(mac)

            for mac in to_remove:
                device = self._devices.pop(mac)
                self._emit_callback("lost", device)

    def _update_or_add_device(self, ack: dict, is_new: bool = False):
        """Internal: update or add a device from ACK data."""
        mac = ack.get("mac", "")
        if not mac:
            return

        with self._lock:
            if mac in self._devices:
                old_ip = self._devices[mac].get("ip")
                self._devices[mac].update(
                    {
                        "ip": ack.get("ip", ""),
                        "mac": mac,
                        "hostname": ack.get("hostname", ""),
                        "status": DeviceStatus.ONLINE.value,
                        "last_seen": time.time(),
                        "last_ip_change": (
                            self._devices[mac]["last_ip_change"]
                            if old_ip != ack.get("ip") and old_ip != "DHCP"
                            else self._devices[mac].get("last_ip_change", time.time())
                        ),
                    }
                )
                self._emit_callback("updated", self._devices[mac])
            else:
                self._devices[mac] = {
                    "ip": ack.get("ip", ""),
                    "mac": mac,
                    "hostname": ack.get("hostname", ""),
                    "status": DeviceStatus.ONLINE.value,
                    "last_seen": time.time(),
                    "last_ip_change": time.time(),
                }
                self._emit_callback("discovered", self._devices[mac])

    def _update_device_statuses(self):
        """Internal: mark devices as offline based on last_seen."""
        now = time.time()
        for device in self._devices.values():
            last_seen = device.get("last_seen", 0)
            if device.get("status") == DeviceStatus.ONLINE.value:
                if now - last_seen > self._offline_grace:
                    device["status"] = DeviceStatus.OFFLINE.value

    def _emit_callback(self, event: str, device: dict):
        """Internal: emit a callback event."""
        for cb in self._callbacks.get(event, []):
            try:
                cb(device)
            except Exception as e:
                logger.error("callback error for %s: %s", event, e)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stops discovery."""
        self.stop_discovery()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    parser = argparse.ArgumentParser(description="CRKR Device Manager")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    p_list = subparsers.add_parser("list", help="List all discovered devices")
    p_list.add_argument("--broadcast", default="255.255.255.255", help="Broadcast address")
    p_list.add_argument("--scan-interval", type=float, default=3.0, help="Scan interval (seconds)")
    p_list.add_argument(
        "--offline-grace",
        type=float,
        default=15.0,
        help="Offline grace period (seconds)",
    )
    p_list.add_argument("--timeout", type=float, default=60.0, help="Device timeout (seconds)")
    p_list.add_argument("--once", action="store_true", help="Scan once and exit")

    p_set = subparsers.add_parser("set-ip", help="Set IP of a device")
    p_set.add_argument("target", help="Current IP of the target device")
    p_set.add_argument("ip", help="New IP address, or 'dhcp' to switch to DHCP")
    p_set.add_argument("--mask", default="", help="Subnet mask or prefix length")
    p_set.add_argument("--gateway", default=None, help="Default gateway")
    p_set.add_argument("--delay", type=int, default=200, help="Delay in ms (default 200)")
    p_set.add_argument("--broadcast", default="255.255.255.255", help="Broadcast address")

    args = parser.parse_args()

    if args.cmd == "list":
        manager = CrackerManager(
            broadcast=args.broadcast,
            scan_interval=args.scan_interval,
            offline_grace=args.offline_grace,
            device_timeout=args.timeout,
            continuous=not args.once,
        )

        def print_device(device):
            print(f"[{device['status'].upper():>7}] {device['mac']:17} {device['ip']:15}  {device['hostname']}")

        print(f"{'STATUS':>7}  {'MAC':17}  {'IP':15}  HOSTNAME")
        print("-" * 70)

        manager.on_discovered(print_device)
        manager.on_updated(print_device)
        manager.on_lost(lambda d: print(f"[REMOVED] {d['mac']}"))

        if args.once:
            for d in manager.discover_once():
                print_device(d)
        else:
            print("(Press Ctrl+C to stop)")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                manager.stop_discovery()

    elif args.cmd == "set-ip":
        manager = CrackerManager(
            broadcast=args.broadcast,
            continuous=False,
        )
        ack = manager.set_ip(
            target_ip=args.target,
            new_ip=args.ip,
            mask=args.mask,
            gateway=args.gateway,
            delay_ms=args.delay,
        )
        print(ack)
