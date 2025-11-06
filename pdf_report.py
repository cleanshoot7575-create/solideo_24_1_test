"""
PDF Report Generator
수집된 시스템 모니터링 데이터를 PDF 리포트로 생성
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import matplotlib.pyplot as plt
from datetime import datetime
import io
from system_monitor import format_bytes


class PDFReportGenerator:
    """PDF 리포트 생성 클래스"""

    def __init__(self, monitor):
        self.monitor = monitor
        self.history = monitor.get_history()

    def generate_report(self, filename):
        """PDF 리포트 생성"""
        doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # 문서 요소 리스트
        story = []

        # 제목
        title = Paragraph("시스템 리소스 모니터링 리포트", title_style)
        story.append(title)

        # 생성 시간
        now = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
        date_text = Paragraph(f"<para align=center>리포트 생성 시간: {now}</para>", styles['Normal'])
        story.append(date_text)
        story.append(Spacer(1, 0.3 * inch))

        # 요약 정보
        story.append(Paragraph("1. 모니터링 요약", heading_style))
        summary_data = self._generate_summary()
        summary_table = self._create_summary_table(summary_data)
        story.append(summary_table)
        story.append(Spacer(1, 0.2 * inch))

        # 그래프 섹션
        story.append(Paragraph("2. 리소스 사용 그래프", heading_style))
        story.append(Spacer(1, 0.1 * inch))

        # CPU 및 메모리 그래프
        cpu_mem_img = self._create_cpu_memory_graph()
        if cpu_mem_img:
            story.append(cpu_mem_img)
            story.append(Spacer(1, 0.2 * inch))

        # 디스크 및 네트워크 그래프
        disk_net_img = self._create_disk_network_graph()
        if disk_net_img:
            story.append(disk_net_img)
            story.append(Spacer(1, 0.2 * inch))

        # 온도 및 GPU 그래프
        temp_gpu_img = self._create_temp_gpu_graph()
        if temp_gpu_img:
            story.append(temp_gpu_img)

        # 페이지 구분
        story.append(PageBreak())

        # 상세 통계
        story.append(Paragraph("3. 상세 통계", heading_style))
        stats_data = self._generate_statistics()
        stats_table = self._create_statistics_table(stats_data)
        story.append(stats_table)

        # PDF 생성
        doc.build(story)

    def _generate_summary(self):
        """요약 정보 생성"""
        if not self.history['timestamps']:
            return []

        duration = (self.history['timestamps'][-1] - self.history['timestamps'][0]).total_seconds()

        summary = [
            ["모니터링 기간", f"{duration:.1f}초"],
            ["데이터 포인트", f"{len(self.history['timestamps'])}개"],
            ["시작 시간", self.history['timestamps'][0].strftime("%Y-%m-%d %H:%M:%S")],
            ["종료 시간", self.history['timestamps'][-1].strftime("%Y-%m-%d %H:%M:%S")],
        ]

        return summary

    def _create_summary_table(self, data):
        """요약 테이블 생성"""
        table = Table(data, colWidths=[3 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        return table

    def _create_cpu_memory_graph(self):
        """CPU 및 메모리 그래프 생성"""
        if not self.history['timestamps']:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

        times = list(range(len(self.history['timestamps'])))

        # CPU 그래프
        ax1.plot(times, self.history['cpu_percent'], 'b-', linewidth=2)
        ax1.set_title('CPU 사용률', fontsize=12, fontweight='bold')
        ax1.set_xlabel('시간 (샘플)')
        ax1.set_ylabel('사용률 (%)')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)

        # 메모리 그래프
        ax2.plot(times, self.history['memory_percent'], 'g-', linewidth=2)
        ax2.set_title('메모리 사용률', fontsize=12, fontweight='bold')
        ax2.set_xlabel('시간 (샘플)')
        ax2.set_ylabel('사용률 (%)')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # 이미지로 변환
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        img = Image(img_buffer, width=9 * inch, height=2.7 * inch)
        return img

    def _create_disk_network_graph(self):
        """디스크 및 네트워크 그래프 생성"""
        if not self.history['timestamps']:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

        times = list(range(len(self.history['timestamps'])))

        # 디스크 I/O 그래프
        disk_read_mb = [x / (1024 * 1024) for x in self.history['disk_read']]
        disk_write_mb = [x / (1024 * 1024) for x in self.history['disk_write']]
        ax1.plot(times, disk_read_mb, 'r-', label='읽기', linewidth=2)
        ax1.plot(times, disk_write_mb, 'orange', label='쓰기', linewidth=2)
        ax1.set_title('디스크 I/O', fontsize=12, fontweight='bold')
        ax1.set_xlabel('시간 (샘플)')
        ax1.set_ylabel('속도 (MB/s)')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # 네트워크 그래프
        net_sent_mb = [x / (1024 * 1024) for x in self.history['net_sent']]
        net_recv_mb = [x / (1024 * 1024) for x in self.history['net_recv']]
        ax2.plot(times, net_sent_mb, 'm-', label='송신', linewidth=2)
        ax2.plot(times, net_recv_mb, 'c-', label='수신', linewidth=2)
        ax2.set_title('네트워크 트래픽', fontsize=12, fontweight='bold')
        ax2.set_xlabel('시간 (샘플)')
        ax2.set_ylabel('속도 (MB/s)')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        # 이미지로 변환
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        img = Image(img_buffer, width=9 * inch, height=2.7 * inch)
        return img

    def _create_temp_gpu_graph(self):
        """온도 및 GPU 그래프 생성"""
        if not self.history['timestamps']:
            return None

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3))

        times = list(range(len(self.history['timestamps'])))

        # 온도 그래프
        if any(t > 0 for t in self.history['temperatures']):
            ax1.plot(times, self.history['temperatures'], 'orange', linewidth=2)
            ax1.set_title('시스템 온도', fontsize=12, fontweight='bold')
            ax1.set_xlabel('시간 (샘플)')
            ax1.set_ylabel('온도 (°C)')
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, '온도 센서\n사용 불가',
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('시스템 온도', fontsize=12, fontweight='bold')

        # GPU 그래프
        if any(g > 0 for g in self.history['gpu_usage']):
            ax2.plot(times, self.history['gpu_usage'], 'purple', linewidth=2)
            ax2.set_title('GPU 사용률', fontsize=12, fontweight='bold')
            ax2.set_xlabel('시간 (샘플)')
            ax2.set_ylabel('사용률 (%)')
            ax2.set_ylim(0, 100)
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'GPU\n사용 불가',
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('GPU 사용률', fontsize=12, fontweight='bold')

        plt.tight_layout()

        # 이미지로 변환
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close(fig)

        img = Image(img_buffer, width=9 * inch, height=2.7 * inch)
        return img

    def _generate_statistics(self):
        """상세 통계 생성"""
        if not self.history['timestamps']:
            return []

        stats = [
            ["리소스", "평균", "최소", "최대", "표준편차"],
        ]

        # CPU
        cpu_data = self.history['cpu_percent']
        if cpu_data:
            import statistics
            stats.append([
                "CPU 사용률 (%)",
                f"{statistics.mean(cpu_data):.2f}",
                f"{min(cpu_data):.2f}",
                f"{max(cpu_data):.2f}",
                f"{statistics.stdev(cpu_data) if len(cpu_data) > 1 else 0:.2f}"
            ])

        # 메모리
        mem_data = self.history['memory_percent']
        if mem_data:
            import statistics
            stats.append([
                "메모리 사용률 (%)",
                f"{statistics.mean(mem_data):.2f}",
                f"{min(mem_data):.2f}",
                f"{max(mem_data):.2f}",
                f"{statistics.stdev(mem_data) if len(mem_data) > 1 else 0:.2f}"
            ])

        # 디스크 읽기
        disk_read = self.history['disk_read']
        if disk_read:
            import statistics
            disk_read_mb = [x / (1024 * 1024) for x in disk_read]
            stats.append([
                "디스크 읽기 (MB/s)",
                f"{statistics.mean(disk_read_mb):.2f}",
                f"{min(disk_read_mb):.2f}",
                f"{max(disk_read_mb):.2f}",
                f"{statistics.stdev(disk_read_mb) if len(disk_read_mb) > 1 else 0:.2f}"
            ])

        # 디스크 쓰기
        disk_write = self.history['disk_write']
        if disk_write:
            import statistics
            disk_write_mb = [x / (1024 * 1024) for x in disk_write]
            stats.append([
                "디스크 쓰기 (MB/s)",
                f"{statistics.mean(disk_write_mb):.2f}",
                f"{min(disk_write_mb):.2f}",
                f"{max(disk_write_mb):.2f}",
                f"{statistics.stdev(disk_write_mb) if len(disk_write_mb) > 1 else 0:.2f}"
            ])

        # 네트워크 송신
        net_sent = self.history['net_sent']
        if net_sent:
            import statistics
            net_sent_mb = [x / (1024 * 1024) for x in net_sent]
            stats.append([
                "네트워크 송신 (MB/s)",
                f"{statistics.mean(net_sent_mb):.2f}",
                f"{min(net_sent_mb):.2f}",
                f"{max(net_sent_mb):.2f}",
                f"{statistics.stdev(net_sent_mb) if len(net_sent_mb) > 1 else 0:.2f}"
            ])

        # 네트워크 수신
        net_recv = self.history['net_recv']
        if net_recv:
            import statistics
            net_recv_mb = [x / (1024 * 1024) for x in net_recv]
            stats.append([
                "네트워크 수신 (MB/s)",
                f"{statistics.mean(net_recv_mb):.2f}",
                f"{min(net_recv_mb):.2f}",
                f"{max(net_recv_mb):.2f}",
                f"{statistics.stdev(net_recv_mb) if len(net_recv_mb) > 1 else 0:.2f}"
            ])

        return stats

    def _create_statistics_table(self, data):
        """통계 테이블 생성"""
        table = Table(data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        return table
