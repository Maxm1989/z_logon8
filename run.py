import sys
import tkinter as tk
from views.main import Main


_single_mutex = None
_single_kernel32 = None


def ensure_single_instance(mutex_name='Global\\ZLogon8_SingleInstance_Mutex'):
    """在 Windows 平台上创建命名互斥体以保证单实例。
    如果已存在实例，尝试激活已有窗口并返回 None。
    返回互斥体句柄以便后续关闭。
    """
    global _single_mutex, _single_kernel32
    if sys.platform != 'win32':
        return True
    try:
        import ctypes
        from ctypes import wintypes

        ERROR_ALREADY_EXISTS = 183
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        CreateMutexW = kernel32.CreateMutexW
        CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
        CreateMutexW.restype = wintypes.HANDLE

        # 创建命名互斥体
        h = CreateMutexW(None, False, mutex_name)
        err = ctypes.get_last_error()
        _single_mutex = h
        _single_kernel32 = kernel32

        if not h:
            return None
        if err == ERROR_ALREADY_EXISTS:
            # 尝试激活已存在窗口（根据窗口标题），然后退出
            try:
                user32 = ctypes.WinDLL('user32', use_last_error=True)
                FindWindowW = user32.FindWindowW
                FindWindowW.argtypes = (wintypes.LPCWSTR, wintypes.LPCWSTR)
                FindWindowW.restype = wintypes.HWND
                ShowWindow = user32.ShowWindow
                ShowWindow.argtypes = (wintypes.HWND, wintypes.INT)
                SetForegroundWindow = user32.SetForegroundWindow
                SetForegroundWindow.argtypes = (wintypes.HWND,)

                # 主窗口标题在 `views/main.py` 中为 "Z Logon"
                hwnd = FindWindowW(None, "Z Logon")
                if hwnd:
                    SW_RESTORE = 9
                    ShowWindow(hwnd, SW_RESTORE)
                    SetForegroundWindow(hwnd)
            except Exception:
                pass
            return None
        return h
    except Exception:
        return True


if __name__ == '__main__':
    mutex = ensure_single_instance()
    if sys.platform == 'win32' and not mutex:
        # 已有实例，直接退出
        sys.exit(0)

    root = Main()
    root.mainloop()

    # 退出前关闭互斥体句柄（Windows）
    try:
        if sys.platform == 'win32' and _single_mutex and _single_kernel32:
            _single_kernel32.CloseHandle(_single_mutex)
    except Exception:
        pass

    sys.exit(0)
