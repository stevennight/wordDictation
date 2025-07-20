import sys
import os
import winreg
import ctypes

try:
    import pyuac
except ImportError:
    pyuac = None

def is_admin():
    """Checks if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(command):
    """Re-runs the script with administrator privileges to execute a command."""
    if pyuac and not pyuac.isUserAdmin():
        try:
            pyuac.runAsAdmin(sys.argv + [command])
            return True, None # Indicates that it tried to elevate
        except Exception as e:
            return False, f"提权失败: {e}"
    return None, None # Already admin or pyuac not available

def do_register():
    """Registers the context menu item for .docx files."""
    try:
        if getattr(sys, 'frozen', False):
            executable_path = sys.executable
        else:
            # Fallback for development: assumes the exe is in the dist folder
            executable_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'dist', 'WordDictation.exe'))

        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"Executable not found at {executable_path}. Please build the application first.")

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'.docx') as key:
            prog_id = winreg.QueryValue(key, None)

        key_path = f"{prog_id}\\shell\\WordDictation"
        command_path = f"{key_path}\\command"

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "用默写工具打开")

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path) as key:
            command = f'\"{executable_path}\" \"%1\"'
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)
        return True, "右键菜单注册成功！"
    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        return False, f"注册失败: {e}"

def do_unregister():
    """Unregisters the context menu item."""
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'.docx') as key:
            prog_id = winreg.QueryValue(key, None)

        key_path = f"{prog_id}\\shell\\WordDictation"
        command_path = f"{key_path}\\command"

        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, command_path)
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
        return True, "右键菜单取消注册成功！"
    except FileNotFoundError:
        return True, "右键菜单未注册。"
    except Exception as e:
        return False, f"取消注册失败: {e}"