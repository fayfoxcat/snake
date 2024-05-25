import pyautogui
import webbrowser
import time

# 打开网页
webbrowser.open('https://pan.quark.cn/s/225c09a190b5#/list/share/baaed7e80e6c4ba8915cc28d7ce4ae24-1493')
time.sleep(10)  # 给网页一些时间来完全加载

# 假设按钮在屏幕上的位置是(x=100, y=200)，这需要你事先知道或者自己定位
pyautogui.click(x=100, y=200)
