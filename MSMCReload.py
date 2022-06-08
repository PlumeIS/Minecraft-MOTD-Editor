import pyperclip
import tkinter
from tkinter.messagebox import showinfo
from tkinter.ttk import Separator
from functools import partial

colors = {"0": {"terminalColor": "7", "name": "黑色", "fontColor": "#000000"},
          "1": {"terminalColor": "34", "name": "深蓝色", "fontColor": "#0000AA"},
          "2": {"terminalColor": "32", "name": "深绿色", "fontColor": "#00AA00"},
          "3": {"terminalColor": "36", "name": "湖蓝色", "fontColor": "#00AAAA"},
          "4": {"terminalColor": "31", "name": "深红色", "fontColor": "#AA0000"},
          "5": {"terminalColor": "35", "name": "紫色", "fontColor": "#AA00AA"},
          "6": {"terminalColor": "33", "name": "金色", "fontColor": "#FFAA00"},
          "7": {"terminalColor": "90", "name": "灰色", "fontColor": "#AAAAAA"},
          "8": {"terminalColor": "32", "name": "深灰色", "fontColor": "#555555"},
          "9": {"terminalColor": "94", "name": "蓝色", "fontColor": "#5555FF"},
          "a": {"terminalColor": "92", "name": "绿色", "fontColor": "#55FF55"},
          "b": {"terminalColor": "96", "name": "天蓝色", "fontColor": "#55FFFF"},
          "c": {"terminalColor": "91", "name": "红色", "fontColor": "#FF5555"},
          "d": {"terminalColor": "95", "name": "粉红色", "fontColor": "#FF55FF"},
          "e": {"terminalColor": "93", "name": "黄色", "fontColor": "#FFFF55"},
          "f": {"terminalColor": "0", "name": "白色", "fontColor": "#FFFFFF"}}

styles = {"k": {"terminalColor": "0", "name": "随机字符", "fontStyle": ""},
          "l": {"terminalColor": "1", "name": "粗体", "fontStyle": "bold"},
          "m": {"terminalColor": "4", "name": "删除线", "fontStyle": "overstrike"},
          "n": {"terminalColor": "9", "name": "下划线", "fontStyle": "underline"},
          "r": {"terminalColor": "0", "name": "重置样式", "fontStyle": ""}}


class Motd:
    def __init__(self):
        self.paragraphList = []
        self.motdColor = "0"
        self.motdStyles = []
        self.uni = ""
        self.required = {"text": [], "color": [], "style": []}
        self.colorsList = colors
        self.stylesList = styles

    def add(self, text, color=None, style=None, index=None):
        if not color:
            color = self.motdColor
        else:
            self.motdColor = color
        if not style:
            style = self.motdStyles
        if not index:
            index = len(self.paragraphList)
        self.paragraphList.insert(index, {"text": text, "color": color, "style": style})

    def remove(self, index):
        self.paragraphList.pop(index)

    def unicode(self):
        self.uni = ""
        for paragraph in self.paragraphList:
            text = paragraph["text"]
            color = self.getColor(paragraph["color"])
            style = self.getStyle(paragraph["style"])
            self.uni += color
            self.uni += style
            self.uni += text.encode("unicode-escape").decode("utf-8")
        return self.uni.replace("\\\\n","\\n").replace("\\\\t","\\t")

    @staticmethod
    def getColor(color):
        return f"\\u00a7{color}"

    @staticmethod
    def getStyle(styleList):
        style = ""
        for s in styleList:
            style += f"\\u00a7{s}"
        return style

