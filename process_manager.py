import psutil

def is_steamvr_running():
    """
    SteamVR 프로세스가 실행 중인지 확인합니다.
    """
    for proc in psutil.process_iter(['name']):
        try:
            if 'vrserver.exe' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def is_vrchat_running():
    """
    VRchat 프로세스가 실행 중인지 확인합니다.
    """
    for proc in psutil.process_iter(['name']):
        try:
            if 'vrchat.exe' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False