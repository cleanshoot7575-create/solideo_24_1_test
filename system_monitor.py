"""
System Resource Monitor Module
실시간 시스템 리소스 모니터링을 위한 모듈
"""

import psutil
import time
from datetime import datetime
from typing import Dict, List, Optional


class SystemMonitor:
    """시스템 리소스 모니터링 클래스"""

    def __init__(self):
        self.history = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_percent': [],
            'disk_read': [],
            'disk_write': [],
            'net_sent': [],
            'net_recv': [],
            'temperatures': [],
            'gpu_usage': []
        }
        self.start_time = time.time()
        self._prev_net_io = psutil.net_io_counters()
        self._prev_disk_io = psutil.disk_io_counters()
        self._prev_time = time.time()

    def get_cpu_info(self) -> Dict:
        """CPU 정보 수집"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)

        return {
            'percent': cpu_percent,
            'count': cpu_count,
            'frequency': cpu_freq.current if cpu_freq else 0,
            'per_cpu': per_cpu
        }

    def get_memory_info(self) -> Dict:
        """메모리 정보 수집"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'percent': memory.percent,
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'swap_percent': swap.percent,
            'swap_total': swap.total,
            'swap_used': swap.used
        }

    def get_disk_info(self) -> Dict:
        """디스크 정보 수집"""
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()

        current_time = time.time()
        time_delta = current_time - self._prev_time

        if time_delta > 0 and disk_io and self._prev_disk_io:
            read_speed = (disk_io.read_bytes - self._prev_disk_io.read_bytes) / time_delta
            write_speed = (disk_io.write_bytes - self._prev_disk_io.write_bytes) / time_delta
        else:
            read_speed = 0
            write_speed = 0

        if disk_io:
            self._prev_disk_io = disk_io

        return {
            'percent': disk_usage.percent,
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'read_speed': read_speed,
            'write_speed': write_speed
        }

    def get_network_info(self) -> Dict:
        """네트워크 정보 수집"""
        net_io = psutil.net_io_counters()

        current_time = time.time()
        time_delta = current_time - self._prev_time

        if time_delta > 0:
            sent_speed = (net_io.bytes_sent - self._prev_net_io.bytes_sent) / time_delta
            recv_speed = (net_io.bytes_recv - self._prev_net_io.bytes_recv) / time_delta
        else:
            sent_speed = 0
            recv_speed = 0

        self._prev_net_io = net_io
        self._prev_time = current_time

        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'sent_speed': sent_speed,
            'recv_speed': recv_speed,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }

    def get_temperature_info(self) -> Dict:
        """온도 정보 수집 (가능한 경우)"""
        temps = {}
        try:
            if hasattr(psutil, "sensors_temperatures"):
                sensors = psutil.sensors_temperatures()
                if sensors:
                    for name, entries in sensors.items():
                        if entries:
                            temps[name] = [entry.current for entry in entries]
        except Exception as e:
            # 온도 센서를 지원하지 않는 시스템
            temps['error'] = str(e)

        return temps

    def get_gpu_info(self) -> Dict:
        """GPU 정보 수집 (가능한 경우)"""
        gpu_info = {
            'available': False,
            'usage': 0,
            'memory': 0,
            'temperature': 0
        }

        try:
            # nvidia-smi를 통한 GPU 정보 수집 시도
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,temperature.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                values = result.stdout.strip().split(', ')
                if len(values) >= 3:
                    gpu_info['available'] = True
                    gpu_info['usage'] = float(values[0])
                    gpu_info['memory'] = float(values[1])
                    gpu_info['temperature'] = float(values[2])
        except Exception:
            # GPU 정보를 사용할 수 없음
            pass

        return gpu_info

    def collect_snapshot(self) -> Dict:
        """현재 시스템 스냅샷 수집"""
        snapshot = {
            'timestamp': datetime.now(),
            'elapsed_time': time.time() - self.start_time,
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'temperature': self.get_temperature_info(),
            'gpu': self.get_gpu_info()
        }

        # 히스토리에 추가
        self.history['timestamps'].append(snapshot['timestamp'])
        self.history['cpu_percent'].append(snapshot['cpu']['percent'])
        self.history['memory_percent'].append(snapshot['memory']['percent'])
        self.history['disk_read'].append(snapshot['disk']['read_speed'])
        self.history['disk_write'].append(snapshot['disk']['write_speed'])
        self.history['net_sent'].append(snapshot['network']['sent_speed'])
        self.history['net_recv'].append(snapshot['network']['recv_speed'])

        # 온도 정보 (평균값 저장)
        temps = snapshot['temperature']
        avg_temp = 0
        temp_count = 0
        if temps and 'error' not in temps:
            for name, values in temps.items():
                if isinstance(values, list):
                    avg_temp += sum(values)
                    temp_count += len(values)
        if temp_count > 0:
            avg_temp /= temp_count
        self.history['temperatures'].append(avg_temp)

        # GPU 사용률
        self.history['gpu_usage'].append(snapshot['gpu']['usage'])

        return snapshot

    def get_history(self) -> Dict:
        """수집된 히스토리 반환"""
        return self.history

    def clear_history(self):
        """히스토리 초기화"""
        for key in self.history:
            self.history[key] = []
        self.start_time = time.time()


def format_bytes(bytes_value: float) -> str:
    """바이트를 읽기 쉬운 형식으로 변환"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
