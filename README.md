# 시스템 리소스 실시간 모니터링 프로그램

실시간으로 시스템 리소스를 모니터링하고 시각화하여 PDF 리포트로 저장할 수 있는 Python 애플리케이션입니다.

## 주요 기능

### 📊 실시간 모니터링
- **CPU 사용률**: 전체 및 코어별 사용률, 주파수 정보
- **메모리 사용률**: RAM 및 스왑 메모리 사용 현황
- **디스크 I/O**: 읽기/쓰기 속도 실시간 추적
- **네트워크 트래픽**: 송신/수신 데이터 속도
- **시스템 온도**: CPU 온도 센서 지원 (가능한 경우)
- **GPU 사용률**: NVIDIA GPU 사용률 및 온도 (nvidia-smi 사용 가능 시)

### 📈 실시간 그래프 시각화
- 6개의 실시간 업데이트 그래프
- 직관적인 색상 구분
- 부드러운 애니메이션

### 📄 PDF 리포트 생성
- 60초 모니터링 후 자동으로 데이터 수집
- 상세한 통계 정보 (평균, 최소, 최대, 표준편차)
- 고품질 그래프 포함
- A4 가로 형식의 전문적인 리포트

## 시스템 요구사항

- Python 3.7 이상
- Linux, Windows, macOS 지원
- 선택사항:
  - nvidia-smi (NVIDIA GPU 모니터링용)
  - lm-sensors (Linux 온도 센서용)

## 설치 방법

### 1. 저장소 클론 또는 다운로드

```bash
git clone <repository-url>
cd solideo_24_1_test
```

### 2. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install psutil matplotlib reportlab numpy Pillow
```

### 3. 실행

```bash
python main.py
```

또는 실행 권한 부여 후:

```bash
chmod +x main.py
./main.py
```

## 사용 방법

### 기본 사용

1. **프로그램 실행**: `python main.py` 명령어로 프로그램 시작
2. **모니터링 시작**: "모니터링 시작 (60초)" 버튼 클릭
3. **실시간 확인**: 좌측 패널에서 현재 리소스 상태 확인, 우측 그래프에서 시각화된 데이터 확인
4. **자동 완료**: 60초 후 자동으로 모니터링 종료
5. **PDF 생성**: "PDF 리포트 생성" 버튼을 클릭하여 리포트 저장

### 버튼 설명

- **모니터링 시작 (60초)**: 60초간 시스템 리소스 모니터링 시작
- **정지**: 모니터링을 수동으로 중지
- **PDF 리포트 생성**: 수집된 데이터를 PDF 파일로 저장

### PDF 리포트

생성된 PDF 리포트에는 다음이 포함됩니다:

1. **모니터링 요약**
   - 모니터링 기간
   - 데이터 포인트 수
   - 시작/종료 시간

2. **리소스 사용 그래프**
   - CPU 및 메모리 사용률
   - 디스크 I/O 속도
   - 네트워크 트래픽
   - 시스템 온도
   - GPU 사용률

3. **상세 통계**
   - 각 리소스별 평균, 최소, 최대, 표준편차

PDF 파일은 `system_monitor_report_YYYYMMDD_HHMMSS.pdf` 형식으로 저장됩니다.

## 프로젝트 구조

```
solideo_24_1_test/
├── main.py                 # 메인 실행 파일
├── system_monitor.py       # 시스템 리소스 모니터링 모듈
├── monitor_ui.py           # UI 및 실시간 그래프 구현
├── pdf_report.py           # PDF 리포트 생성 모듈
├── requirements.txt        # 필수 패키지 목록
└── README.md              # 프로젝트 문서
```

## 모듈 설명

### system_monitor.py
- `SystemMonitor` 클래스: 시스템 리소스 데이터 수집
- 각종 센서 정보 읽기 및 히스토리 관리
- CPU, 메모리, 디스크, 네트워크, 온도, GPU 모니터링

### monitor_ui.py
- `MonitorUI` 클래스: Tkinter 기반 GUI
- 실시간 그래프 업데이트 (matplotlib)
- 모니터링 제어 및 상태 표시

### pdf_report.py
- `PDFReportGenerator` 클래스: PDF 리포트 생성
- 그래프 및 통계 테이블 생성
- reportlab을 사용한 전문적인 레이아웃

## 의존성 패키지

- **psutil (5.9.8)**: 시스템 및 프로세스 유틸리티
- **matplotlib (3.8.2)**: 그래프 시각화
- **numpy (1.26.3)**: 수치 연산
- **reportlab (4.0.9)**: PDF 생성
- **Pillow (10.2.0)**: 이미지 처리

## 문제 해결

### 온도 센서를 사용할 수 없음

Linux에서 온도 센서가 감지되지 않는 경우:

```bash
# lm-sensors 설치
sudo apt-get install lm-sensors

# 센서 감지
sudo sensors-detect

# 센서 확인
sensors
```

### GPU 정보를 사용할 수 없음

NVIDIA GPU의 경우 nvidia-smi가 설치되어 있어야 합니다:

```bash
# 설치 확인
nvidia-smi

# 설치되지 않은 경우 NVIDIA 드라이버 설치 필요
```

### tkinter가 없다는 오류

일부 Linux 배포판에서는 tkinter를 별도로 설치해야 합니다:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## 기술 스택

- **언어**: Python 3
- **GUI**: Tkinter
- **그래프**: Matplotlib
- **PDF**: ReportLab
- **시스템 모니터링**: psutil

## 라이선스

이 프로젝트의 라이선스는 LICENSE.md 파일을 참조하세요.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 작성자

System Resource Monitor Team

---

**참고**: 이 프로그램은 시스템 리소스를 실시간으로 모니터링하므로 약간의 시스템 리소스를 사용합니다.
그러나 최적화되어 있어 최소한의 오버헤드로 작동합니다.
