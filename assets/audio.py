from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import pythoncom


def monitor_volume_changes(volume_level):  # Funktion zum Überwachen von Lautstärkeänderungen
    pythoncom.CoInitialize()
    interface = AudioUtilities.GetSpeakers().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    try:
        while True:
            time.sleep(1)  # Überprüfe alle 1 Sekunden
            current_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
            if current_volume != volume_level:
                set_system_volume(volume_level)
                print(f"Lautstärkeänderung erkannt. Reset zu {volume_level}%")
    finally:
        pythoncom.CoUninitialize()


def set_system_volume(volume_level):
    interface = AudioUtilities.GetSpeakers().Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    cast(interface, POINTER(IAudioEndpointVolume)).SetMasterVolumeLevelScalar((volume_level/100), None)


if __name__ == "__main__":
    import multiprocessing
    volume_process = multiprocessing.Process(target=monitor_volume_changes, args=(10, ), daemon=True)
    volume_process.start()
    x = 0
    while True:
        x += 1
        print("test", x)
        time.sleep(2)
