from process_manager import is_steamvr_running
import time
import subprocess
import psutil
import os

class AppController:
    def __init__(self):
        self.is_steamvr_running = False
        self.registered_programs = [
            "C:/Users/hppmm/OneDrive/바탕 화면/ShellProtectorOSC1.6/ShellProtectorOSC1.6.exe"
        ]
        self.check_steamvr_status()


    def check_steamvr_status(self):
        """
        SteamVR 프로세스 실행 상태를 주기적으로 확인합니다.
        """
        while True:
            if is_steamvr_running():
                if not self.is_steamvr_running:
                    self.is_steamvr_running = True
                    print("SteamVR is running")
                    self.start_registered_programs()
            else:
                if self.is_steamvr_running:
                    self.is_steamvr_running = False
                    print("SteamVR is not running")
                    self.stop_registered_programs()
            time.sleep(1)  # 1초 간격으로 상태 확인

    def start_registered_programs(self):
        """
        등록된 프로그램을 실행합니다.
        """
        for program in self.registered_programs:
            try:
                # 프로그램의 디렉토리 경로 추출
                program_dir = os.path.dirname(program)

                # 프로그램 실행 전 작업 디렉토리 변경
                current_dir = os.getcwd()
                os.chdir(program_dir)

                # 프로그램 실행
                subprocess.Popen(program)
                print(f"{program} started")

                # 작업 디렉토리 복원
                os.chdir(current_dir)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"Failed to start {program}")

    def stop_registered_programs(self):
        """
        등록된 프로그램을 종료합니다.
        """
        for program in self.registered_programs:
            try:
                # 프로그램의 디렉토리 경로 추출
                program_dir = os.path.dirname(program)

                # 프로그램 실행 전 작업 디렉토리 변경
                current_dir = os.getcwd()
                os.chdir(program_dir)

                # 프로세스 종료
                for proc in psutil.process_iter(['name']):
                    if os.path.basename(program).lower() in proc.info['name'].lower():
                        proc.terminate()
                        print(f"{os.path.basename(program)} stopped")

                # 작업 디렉토리 복원
                os.chdir(current_dir)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
