#!/usr/bin/env python3
"""
System Resource Monitor - Main Entry Point
시스템 리소스 실시간 모니터링 프로그램

사용법:
    python main.py
"""

import sys
import tkinter as tk
from tkinter import messagebox


def check_dependencies():
    """필수 라이브러리 확인"""
    missing_packages = []

    try:
        import psutil
    except ImportError:
        missing_packages.append('psutil')

    try:
        import matplotlib
    except ImportError:
        missing_packages.append('matplotlib')

    try:
        import reportlab
    except ImportError:
        missing_packages.append('reportlab')

    if missing_packages:
        error_msg = (
            "다음 패키지가 설치되어 있지 않습니다:\n"
            f"{', '.join(missing_packages)}\n\n"
            "다음 명령어로 설치하세요:\n"
            f"pip install {' '.join(missing_packages)}"
        )
        print(error_msg)
        messagebox.showerror("패키지 누락", error_msg)
        return False

    return True


def main():
    """메인 함수"""
    print("="*60)
    print("시스템 리소스 모니터")
    print("="*60)
    print("실시간 시스템 리소스 모니터링 프로그램을 시작합니다...")
    print()

    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)

    # UI 실행
    try:
        from monitor_ui import MonitorUI

        root = tk.Tk()
        app = MonitorUI(root)

        print("UI가 실행되었습니다.")
        print("프로그램을 종료하려면 창을 닫으세요.")
        print()

        root.mainloop()

    except Exception as e:
        error_msg = f"프로그램 실행 중 오류가 발생했습니다:\n{str(e)}"
        print(error_msg)
        messagebox.showerror("오류", error_msg)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
