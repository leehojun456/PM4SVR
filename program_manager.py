from process_manager import is_steamvr_running
import time
import subprocess
import psutil
import os
import webbrowser
from PyQt6.QtCore import QStandardPaths

class FileManager:
    def __init__(self, file_name):
        self.file_name = file_name

    def get_file_path(self):
        documents_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        file_path = os.path.join(documents_dir, self.file_name)
        return file_path

    def read_file(self):
        file_path = self.get_file_path()
        print(f"File successfully loaded at: {file_path}")
        try:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file.readlines()]
                return lines
        except FileNotFoundError:
            return []

    def write_file(self, program_paths):
        file_path = self.get_file_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as file:  # 'a' 모드는 파일의 끝에 추가합니다
            for path in program_paths:
                file.write(path + '\n')
                
        print(f"File successfully saved at: {file_path}")
        return True
    


class AppController:
    def __init__(self):
        self.is_steamvr_running = False
        self.is_vrchat_running = False
        self.program_list = FileManager("saved_programs.txt")

    def check_steamvr_status(self):
        """
        SteamVR 프로세스 실행 상태를 주기적으로 확인합니다.
        """
        while True:
            if is_steamvr_running():
                if not self.is_steamvr_running:
                    self.start_all_programs()
                    self.is_steamvr_running = True
            else:
                if self.is_steamvr_running:
                    self.stop_all_programs()
                    self.is_steamvr_running = False


            time.sleep(1)  # 1초 간격으로 상태 확인
            
        
    def check_vrchat_status(self):
        """
        VRChat 프로세스 실행 상태를 주기적으로 확인합니다.
        """
        while True:
            if is_steamvr_running():
                if not self.is_vrchat_running:
                    self.start_all_programs()
                    self.is_vrchat_running = True
            else:
                if self.is_steamvr_running:
                    self.stop_all_programs()
                    self.is_vrchat_running = False


            time.sleep(1)  # 1초 간격으로 상태 확인




    def start_registered_programs(self, program_path):
        """
        등록된 프로그램을 실행합니다.
        """
        try:
            if "://" in program_path:
                # 프로토콜 링크 처리
                webbrowser.open(program_path)
                print(f"Opened {program_path} in web browser")
                return

            # 이미 실행 중인 프로그램인지 확인
            program_name = os.path.basename(program_path)
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == program_name:
                    print(f"{program_name} is already running.")
                    return

            program_dir = os.path.dirname(program_path)

            # 프로그램 실행 전 작업 디렉토리 변경
            current_dir = os.getcwd()
            os.chdir(program_dir)

            # 프로그램 실행
            subprocess.Popen(program_path)
            print(f"{program_path} started")

            # 작업 디렉토리 복원
            os.chdir(current_dir)
        except FileNotFoundError:
            print(f"File not found: {program_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start {program_path}: {e}")
        except Exception as e:
            print(f"An error occurred while starting {program_path}: {e}")

    def stop_registered_programs(self, program_path):
        """
        등록된 프로그램을 종료합니다.
        """
        try:
            if "://" in program_path:
                # URL 링크의 경우 처리 불가 (추가 로직 필요)
                print(f"Cannot directly terminate process for URL: {program_path}")
                return

            # 프로그램의 파일 이름 추출
            program_name = os.path.basename(program_path).lower()

            # 모든 프로세스 탐색
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    exe_path = proc.info['exe']
                    if exe_path is not None and program_name in exe_path.lower():
                        proc.terminate()  # 프로세스 종료 시도
                        proc.wait()  # 프로세스 종료 대기
                        print(f"{program_name} stopped")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue  # 해당 프로세스가 더 이상 유효하지 않거나 접근이 거부된 경우 무시

            print(f"No running process found for {program_path}")

        except Exception as e:
            print(f"An error occurred while stopping {program_path}: {e}")

    #프로그램 리스트 파일 저장
    def save_programs_to_file(self, program_path):
        program_paths = self.program_list.read_file()
        
        
        # 중복 확인
        if program_path in program_paths:
            print(f"Program path '{program_path}' already exists in the file.")
            return False
        
        
        # 중복되지 않을 경우 프로그램 경로를 추가합니다
        program_paths.append(program_path)
        
        self.program_list.write_file(program_paths)
        return True
        
    #프로그램 리스트 가져오기
    def load_programs_to_file(self):
        return self.program_list.read_file()
    
    
    #프로그램 리스트에서 제거
    def remove_programs_to_file(self, index):
        program_paths = self.program_list.read_file()
        program_paths.pop(index)
        self.program_list.write_file(program_paths)
        

    # 현재 목록에 있는 모든 프로그램을 시작합니다.
    def start_all_programs(self):
        program_paths = self.program_list.read_file()
        for program_path in program_paths:
            self.start_registered_programs(program_path)

    # 현재 목록에 있는 모든 프로그램을 중지합니다.
    def stop_all_programs(self):
        program_paths = self.program_list.read_file()
        for program_path in program_paths:
            self.stop_registered_programs(program_path)