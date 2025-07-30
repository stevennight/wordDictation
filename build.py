import PyInstaller.__main__
import os
import tkinterdnd2
import customtkinter

if __name__ == '__main__':
    # 获取 tkinterdnd2 和 customtkinter 的路径
    tkinterdnd2_path = os.path.dirname(tkinterdnd2.__file__)
    customtkinter_path = os.path.dirname(customtkinter.__file__)

    # 打包主程序
    PyInstaller.__main__.run([
        'main.py',
        '--name=WordDictation',
        '--onefile',
        '--windowed',
        '--icon=src/icon.ico',
        f'--add-data={customtkinter_path};customtkinter',
        f'--add-data={tkinterdnd2_path};tkinterdnd2',
        '--add-data=src;src',
    ])

    print("打包完成！请在 'dist' 文件夹中查找 WordDictation.exe")