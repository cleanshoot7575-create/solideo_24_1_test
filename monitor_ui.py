"""
Real-time System Monitor UI
실시간 시스템 모니터링 UI 구현
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime
from system_monitor import SystemMonitor, format_bytes


class MonitorUI:
    """실시간 모니터링 UI 클래스"""

    def __init__(self, root):
        self.root = root
        self.root.title("시스템 리소스 모니터")
        self.root.geometry("1400x900")

        self.monitor = SystemMonitor()
        self.is_monitoring = False
        self.monitoring_thread = None
        self.recording_start_time = None
        self.recording_duration = 60  # 1분

        # UI 구성
        self.setup_ui()

        # 업데이트 시작
        self.update_display()

    def setup_ui(self):
        """UI 컴포넌트 설정"""
        # 상단 제어 패널
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # 시작/정지 버튼
        self.start_button = ttk.Button(
            control_frame,
            text="모니터링 시작 (60초)",
            command=self.start_monitoring
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            control_frame,
            text="정지",
            command=self.stop_monitoring,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # PDF 생성 버튼
        self.pdf_button = ttk.Button(
            control_frame,
            text="PDF 리포트 생성",
            command=self.generate_pdf,
            state=tk.DISABLED
        )
        self.pdf_button.pack(side=tk.LEFT, padx=5)

        # 상태 레이블
        self.status_label = ttk.Label(
            control_frame,
            text="준비",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=20)

        # 정보 표시 프레임 (좌측)
        info_frame = ttk.Frame(self.root)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        # CPU 정보
        cpu_frame = ttk.LabelFrame(info_frame, text="CPU 정보", padding="10")
        cpu_frame.pack(fill=tk.X, pady=5)
        self.cpu_label = ttk.Label(cpu_frame, text="CPU: --%", font=("Arial", 12))
        self.cpu_label.pack(anchor=tk.W)
        self.cpu_freq_label = ttk.Label(cpu_frame, text="주파수: -- MHz")
        self.cpu_freq_label.pack(anchor=tk.W)
        self.cpu_count_label = ttk.Label(cpu_frame, text="코어: --")
        self.cpu_count_label.pack(anchor=tk.W)

        # 메모리 정보
        mem_frame = ttk.LabelFrame(info_frame, text="메모리 정보", padding="10")
        mem_frame.pack(fill=tk.X, pady=5)
        self.mem_label = ttk.Label(mem_frame, text="메모리: --%", font=("Arial", 12))
        self.mem_label.pack(anchor=tk.W)
        self.mem_used_label = ttk.Label(mem_frame, text="사용: -- / --")
        self.mem_used_label.pack(anchor=tk.W)
        self.swap_label = ttk.Label(mem_frame, text="스왑: --%")
        self.swap_label.pack(anchor=tk.W)

        # 디스크 정보
        disk_frame = ttk.LabelFrame(info_frame, text="디스크 정보", padding="10")
        disk_frame.pack(fill=tk.X, pady=5)
        self.disk_label = ttk.Label(disk_frame, text="디스크: --%", font=("Arial", 12))
        self.disk_label.pack(anchor=tk.W)
        self.disk_used_label = ttk.Label(disk_frame, text="사용: -- / --")
        self.disk_used_label.pack(anchor=tk.W)
        self.disk_io_label = ttk.Label(disk_frame, text="읽기/쓰기: -- / --")
        self.disk_io_label.pack(anchor=tk.W)

        # 네트워크 정보
        net_frame = ttk.LabelFrame(info_frame, text="네트워크 정보", padding="10")
        net_frame.pack(fill=tk.X, pady=5)
        self.net_label = ttk.Label(net_frame, text="네트워크", font=("Arial", 12))
        self.net_label.pack(anchor=tk.W)
        self.net_speed_label = ttk.Label(net_frame, text="송신/수신: -- / --")
        self.net_speed_label.pack(anchor=tk.W)

        # 온도 정보
        temp_frame = ttk.LabelFrame(info_frame, text="온도 정보", padding="10")
        temp_frame.pack(fill=tk.X, pady=5)
        self.temp_label = ttk.Label(temp_frame, text="온도: -- °C")
        self.temp_label.pack(anchor=tk.W)

        # GPU 정보
        gpu_frame = ttk.LabelFrame(info_frame, text="GPU 정보", padding="10")
        gpu_frame.pack(fill=tk.X, pady=5)
        self.gpu_label = ttk.Label(gpu_frame, text="GPU: 사용 불가")
        self.gpu_label.pack(anchor=tk.W)

        # 그래프 프레임 (우측)
        graph_frame = ttk.Frame(self.root)
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Matplotlib Figure 생성
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3)

        # 서브플롯 생성
        self.ax_cpu = self.fig.add_subplot(3, 2, 1)
        self.ax_mem = self.fig.add_subplot(3, 2, 2)
        self.ax_disk = self.fig.add_subplot(3, 2, 3)
        self.ax_net = self.fig.add_subplot(3, 2, 4)
        self.ax_temp = self.fig.add_subplot(3, 2, 5)
        self.ax_gpu = self.fig.add_subplot(3, 2, 6)

        # Canvas 생성
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_display(self):
        """디스플레이 업데이트"""
        if not self.is_monitoring:
            # 모니터링 중이 아니어도 현재 상태는 표시
            snapshot = self.monitor.collect_snapshot()
            self.update_info_labels(snapshot)

        # 그래프 업데이트
        self.update_graphs()

        # 100ms마다 업데이트
        self.root.after(100, self.update_display)

    def update_info_labels(self, snapshot):
        """정보 레이블 업데이트"""
        # CPU
        cpu = snapshot['cpu']
        self.cpu_label.config(text=f"CPU: {cpu['percent']:.1f}%")
        self.cpu_freq_label.config(text=f"주파수: {cpu['frequency']:.0f} MHz")
        self.cpu_count_label.config(text=f"코어: {cpu['count']}")

        # 메모리
        mem = snapshot['memory']
        self.mem_label.config(text=f"메모리: {mem['percent']:.1f}%")
        self.mem_used_label.config(
            text=f"사용: {format_bytes(mem['used'])} / {format_bytes(mem['total'])}"
        )
        self.swap_label.config(text=f"스왑: {mem['swap_percent']:.1f}%")

        # 디스크
        disk = snapshot['disk']
        self.disk_label.config(text=f"디스크: {disk['percent']:.1f}%")
        self.disk_used_label.config(
            text=f"사용: {format_bytes(disk['used'])} / {format_bytes(disk['total'])}"
        )
        self.disk_io_label.config(
            text=f"읽기/쓰기: {format_bytes(disk['read_speed'])}/s / {format_bytes(disk['write_speed'])}/s"
        )

        # 네트워크
        net = snapshot['network']
        self.net_speed_label.config(
            text=f"송신/수신: {format_bytes(net['sent_speed'])}/s / {format_bytes(net['recv_speed'])}/s"
        )

        # 온도
        temps = snapshot['temperature']
        if temps and 'error' not in temps:
            temp_values = []
            for name, values in temps.items():
                if isinstance(values, list):
                    temp_values.extend(values)
            if temp_values:
                avg_temp = sum(temp_values) / len(temp_values)
                self.temp_label.config(text=f"온도: {avg_temp:.1f} °C")
            else:
                self.temp_label.config(text="온도: 사용 불가")
        else:
            self.temp_label.config(text="온도: 사용 불가")

        # GPU
        gpu = snapshot['gpu']
        if gpu['available']:
            self.gpu_label.config(
                text=f"GPU: {gpu['usage']:.1f}% | 온도: {gpu['temperature']:.1f}°C"
            )
        else:
            self.gpu_label.config(text="GPU: 사용 불가")

    def update_graphs(self):
        """그래프 업데이트"""
        history = self.monitor.get_history()

        if not history['timestamps']:
            return

        # 시간축 (상대 시간으로 변환)
        if self.recording_start_time:
            times = [(t - self.recording_start_time).total_seconds()
                    for t in history['timestamps']]
        else:
            times = list(range(len(history['timestamps'])))

        # CPU 그래프
        self.ax_cpu.clear()
        self.ax_cpu.plot(times, history['cpu_percent'], 'b-', linewidth=2)
        self.ax_cpu.set_title('CPU 사용률', fontsize=10, fontweight='bold')
        self.ax_cpu.set_ylabel('사용률 (%)')
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.grid(True, alpha=0.3)

        # 메모리 그래프
        self.ax_mem.clear()
        self.ax_mem.plot(times, history['memory_percent'], 'g-', linewidth=2)
        self.ax_mem.set_title('메모리 사용률', fontsize=10, fontweight='bold')
        self.ax_mem.set_ylabel('사용률 (%)')
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.grid(True, alpha=0.3)

        # 디스크 I/O 그래프
        self.ax_disk.clear()
        disk_read_mb = [x / (1024 * 1024) for x in history['disk_read']]
        disk_write_mb = [x / (1024 * 1024) for x in history['disk_write']]
        self.ax_disk.plot(times, disk_read_mb, 'r-', label='읽기', linewidth=2)
        self.ax_disk.plot(times, disk_write_mb, 'orange', label='쓰기', linewidth=2)
        self.ax_disk.set_title('디스크 I/O', fontsize=10, fontweight='bold')
        self.ax_disk.set_ylabel('속도 (MB/s)')
        self.ax_disk.legend(loc='upper right', fontsize=8)
        self.ax_disk.grid(True, alpha=0.3)

        # 네트워크 그래프
        self.ax_net.clear()
        net_sent_mb = [x / (1024 * 1024) for x in history['net_sent']]
        net_recv_mb = [x / (1024 * 1024) for x in history['net_recv']]
        self.ax_net.plot(times, net_sent_mb, 'm-', label='송신', linewidth=2)
        self.ax_net.plot(times, net_recv_mb, 'c-', label='수신', linewidth=2)
        self.ax_net.set_title('네트워크 트래픽', fontsize=10, fontweight='bold')
        self.ax_net.set_ylabel('속도 (MB/s)')
        self.ax_net.legend(loc='upper right', fontsize=8)
        self.ax_net.grid(True, alpha=0.3)

        # 온도 그래프
        self.ax_temp.clear()
        if any(t > 0 for t in history['temperatures']):
            self.ax_temp.plot(times, history['temperatures'], 'orange', linewidth=2)
            self.ax_temp.set_title('시스템 온도', fontsize=10, fontweight='bold')
            self.ax_temp.set_ylabel('온도 (°C)')
        else:
            self.ax_temp.text(0.5, 0.5, '온도 센서\n사용 불가',
                            ha='center', va='center', transform=self.ax_temp.transAxes)
            self.ax_temp.set_title('시스템 온도', fontsize=10, fontweight='bold')
        self.ax_temp.grid(True, alpha=0.3)

        # GPU 그래프
        self.ax_gpu.clear()
        if any(g > 0 for g in history['gpu_usage']):
            self.ax_gpu.plot(times, history['gpu_usage'], 'purple', linewidth=2)
            self.ax_gpu.set_title('GPU 사용률', fontsize=10, fontweight='bold')
            self.ax_gpu.set_ylabel('사용률 (%)')
            self.ax_gpu.set_ylim(0, 100)
        else:
            self.ax_gpu.text(0.5, 0.5, 'GPU\n사용 불가',
                           ha='center', va='center', transform=self.ax_gpu.transAxes)
            self.ax_gpu.set_title('GPU 사용률', fontsize=10, fontweight='bold')
        self.ax_gpu.grid(True, alpha=0.3)

        # X축 레이블 (하단 그래프만)
        self.ax_temp.set_xlabel('시간 (초)')
        self.ax_gpu.set_xlabel('시간 (초)')

        self.canvas.draw()

    def monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            snapshot = self.monitor.collect_snapshot()
            self.update_info_labels(snapshot)

            # 60초 경과 확인
            elapsed = (datetime.now() - self.recording_start_time).total_seconds()
            remaining = self.recording_duration - elapsed

            if remaining <= 0:
                self.is_monitoring = False
                self.root.after(0, self.on_monitoring_complete)
                break

            self.status_label.config(
                text=f"모니터링 중... 남은 시간: {int(remaining)}초"
            )

            time.sleep(0.5)

    def start_monitoring(self):
        """모니터링 시작"""
        self.is_monitoring = True
        self.monitor.clear_history()
        self.recording_start_time = datetime.now()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pdf_button.config(state=tk.DISABLED)

        self.status_label.config(text="모니터링 시작...")

        self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """모니터링 정지"""
        self.is_monitoring = False
        self.on_monitoring_complete()

    def on_monitoring_complete(self):
        """모니터링 완료 처리"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pdf_button.config(state=tk.NORMAL)

        self.status_label.config(text="모니터링 완료")
        messagebox.showinfo("완료", "모니터링이 완료되었습니다.\nPDF 리포트를 생성할 수 있습니다.")

    def generate_pdf(self):
        """PDF 리포트 생성"""
        from pdf_report import PDFReportGenerator

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_monitor_report_{timestamp}.pdf"

            generator = PDFReportGenerator(self.monitor)
            generator.generate_report(filename)

            self.status_label.config(text=f"PDF 생성 완료: {filename}")
            messagebox.showinfo("완료", f"PDF 리포트가 생성되었습니다:\n{filename}")

        except Exception as e:
            messagebox.showerror("오류", f"PDF 생성 중 오류 발생:\n{str(e)}")


def main():
    """메인 함수"""
    root = tk.Tk()
    app = MonitorUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
