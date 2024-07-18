from process_manager import is_steamvr_running
import time
import subprocess
import psutil
import os

class AppController:
    def __init__(self):
        self.is_steamvr_running = False
        self.registered_programs = []

    def check_steamvr_status(self):
        """
        SteamVR 프로세스 실행 상태를 주기적으로 확인합니다.
        """
        while True:
            # 파일에서 프로그램 목록을 읽어옵니다.
            try:
                # 현재 실행 파일의 디렉토리 경로 가져오기
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_name = "saved_programs.txt"
                file_path = os.path.join(script_dir, file_name)
                with open(file_path, 'r') as f:
                    program_paths = f.readlines()
                    if is_steamvr_running():
                        if not self.is_steamvr_running:
                            for path in program_paths:
                                print(path)
                                path = path.strip()
                                self.start_registered_programs(path)
                            self.is_steamvr_running = True
                    else:
                        if self.is_steamvr_running:
                            for path in program_paths:
                                print(path)
                                path = path.strip()
                                self.stop_registered_programs(path)
                            self.is_steamvr_running = False
            except FileNotFoundError:
                # 파일이 없는 경우 아무 작업도 하지 않습니다.
                pass

            time.sleep(1)  # 1초 간격으로 상태 확인

    def register_program(self, program_path):
        """
        프로그램을 등록합니다.
        """
        if program_path not in self.registered_programs:
            self.registered_programs.append(program_path)

    def start_registered_programs(self, program_path):
        """
        등록된 프로그램을 실행합니다.
        """
        try:
            # 프로그램의 디렉토리 경로 추출
            program_dir = os.path.dirname(program_path)

            # 프로그램 실행 전 작업 디렉토리 변경
            current_dir = os.getcwd()
            os.chdir(program_dir)

            # 프로그램 실행
            subprocess.Popen(program_path)
            print(f"{program_path} started")

            # 작업 디렉토리 복원
            os.chdir(current_dir)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Failed to start {program_path}")

    def stop_registered_programs(self, program_path):
        """
        등록된 프로그램을 종료합니다.
        """
        try:
            # 프로그램의 디렉토리 경로 추출
            program_dir = os.path.dirname(program_path)

            # 프로그램 실행 전 작업 디렉토리 변경
            current_dir = os.getcwd()
            os.chdir(program_dir)

            # 프로세스 종료
            for proc in psutil.process_iter(['name']):
                if os.path.basename(program_path).lower() in proc.info['name'].lower():
                    proc.terminate()
                    print(f"{os.path.basename(program_path)} stopped")

            # 작업 디렉토리 복원
            os.chdir(current_dir)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass