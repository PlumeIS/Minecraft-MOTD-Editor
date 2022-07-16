import tkinter
import pyperclip
from MSMCReload import Motd,colors,styles
from functools import partial
from tkinter.ttk import Separator
from tkinter.messagebox import showinfo


class MotdUI(Motd):
    def __init__(self):
        super().__init__()
        self.ui = tkinter.Tk()
        self.ui.iconbitmap(resourcePath("icon.ico"))

    def init(self):
        self.ui.title("我的世界服务器信息生成器by很绿の羽毛v1.0.5")
        self.ui.resizable(True, True)
        self.ui.geometry("485x350")
        self.ui.minsize(485,350)
        self.edit = 0

        colorButtonCounter = 0
        colorButtonX = 5
        colorButtonY = 30

        tkinter.Frame(self.ui,bg="#ded7b8",width=485,height=95).place(x=0,y=0)
        tkinter.Frame(self.ui, bg="#ded7b8", width=485, height=60).place(x=0, y=240)

        colorText = tkinter.Label(text="当前颜色为:",bg="#ded7b8")
        colorText.place(x=5, y=5)
        self.colorC = tkinter.Label(text="黑色", bg="#ded7b8")
        self.colorC.place(x=80, y=5)

        self.selectList = []
        self.showList = []

        for c, v in colors.items():
            if colorButtonCounter % 8 == 0 and colorButtonCounter != 0:
                colorButtonX = 5
                colorButtonY += 35
            button = tkinter.Button(self.ui,
                                    text=v["name"],
                                    fg=v["fontColor"],
                                    bg="#ded7b8",
                                    width=6,
                                    relief="flat",
                                    )
            button["command"] = partial(self.setColor, c)
            button.place(x=colorButtonX, y=colorButtonY)
            colorButtonX += 60
            colorButtonCounter += 1

        tkinter.Label(self.ui, text="样式选择:").place(x=5, y=96)
        self.styleStates = {}
        styleButtonX = 5
        for s, v in styles.items():
            self.styleStates[s] = False
            b = tkinter.Button(self.ui,
                               text=v["name"],
                               width=7,
                               font=("", 10, v["fontStyle"]),
                               relief="groove"
                               )
            b["command"] = partial(self.setStyle, s, b)
            b.place(x=styleButtonX, y=120)
            if v["name"] == "粗体":
                styleButtonX += 7
            styleButtonX += 65

        self.ui.update()
        Separator(self.ui, orient=tkinter.HORIZONTAL).pack(fill=tkinter.X, pady=150)
        self.inputArea = tkinter.Entry(self.ui, width=35)
        self.inputArea.place(x=5, y=160)
        tkinter.Button(self.ui, text="添加", command=lambda: [self.addPara(), self.updatePara(), self.updateShow(), self.updateUnicode()],font=("", 10),relief="groove").place(x=260, y=159)
        tkinter.Button(self.ui, text="更改", command=lambda: [self.changeText(), self.updatePara(), self.updateShow(), self.updateUnicode()],font=("", 10),relief="groove").place(x=300, y=159)
        tkinter.Button(self.ui, text="删除", command=lambda: [self.deletePara(), self.updatePara(), self.updateShow(), self.updateUnicode()],font=("", 10), fg="#FF5555",relief="groove").place(x=340, y=159)
        tkinter.Button(self.ui, text="颜色", command=lambda: [self.changeColor(), self.updatePara(), self.updateShow(), self.updateUnicode()],font=("", 10),relief="groove").place(x=405, y=159)
        tkinter.Button(self.ui, text="样式", command=lambda: [self.changeStyle(), self.updatePara(), self.updateShow(), self.updateUnicode()],font=("", 10),relief="groove").place(x=445, y=159)

        tkinter.Label(self.ui, text="预览:",bg="#ded7b8").place(x=5, y=240)
        tkinter.Label(self.ui, text="导出:").place(x=5, y=300)

        self.unicodeEntry = tkinter.Entry(self.ui, state="readonly", width=60)
        self.unicodeEntry.place(x=5, y=320)
        self.copyButton = tkinter.Button(self.ui, text="复制", font=("", 10), relief="groove")
        self.copyButton.place(x=435,y=319)

    def updateUnicode(self):
        unicodeText = self.unicode()
        self.unicodeEntry["state"] = "normal"
        self.unicodeEntry.update()
        self.unicodeEntry.delete(0,"end")
        self.unicodeEntry.insert(0,unicodeText)
        self.unicodeEntry["state"] = "readonly"
        self.unicodeEntry.update()
        self.copyButton["command"] = lambda:[pyperclip.copy(unicodeText),showinfo("结果","复制成功!")]
        self.copyButton.update()

    def updateShow(self):
        placeX = 5
        placeY = 260
        for i in self.showList:
            i.place_forget()
            i.update()
        for s in self.paragraphList:
            if "\\n" in s["text"]:
                placeX = 5
                placeY += 20
                showArea = tkinter.Label(self.ui, text=s["text"].replace("\\n", ""), bg="#ded7b8", fg=colors[s["color"]]["fontColor"],font=("", 10, " ".join([styles[i]["fontStyle"] for i in s["style"] if styles[i]["fontStyle"] != ""])))
            elif "\\t" in s["text"]:
                showArea = tkinter.Label(self.ui, text=s["text"].replace("\\t", "    "), bg="#ded7b8", fg=colors[s["color"]]["fontColor"], font=("", 10, " ".join([styles[i]["fontStyle"] for i in s["style"] if styles[i]["fontStyle"] != ""])))
            else:
                showArea = tkinter.Label(self.ui, text=s["text"], bg="#ded7b8", fg=colors[s["color"]]["fontColor"], font=("", 10, " ".join([styles[i]["fontStyle"] for i in s["style"] if styles[i]["fontStyle"] != ""])))
            if "k" in s["style"]:
                showArea["text"] += "(随机字符)"
                threading.Thread(target=MotdUI.updateRandomChar, args=(showArea,len(s["text"])),daemon=True).start()
            showArea.place(x=placeX, y=placeY)
            showArea.update()
            if not "\\n" in s["text"]:
                placeX += (showArea.winfo_width() - 3)
            self.showList.append(showArea)

    @staticmethod
    def updateRandomChar(label,length):
        while True:
            label["text"] = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            label.update()
            time.sleep(0.2)

    def updateEdit(self, edit, b):
        self.edit = edit
        for i in self.selectList:
            i["bg"] = "#EFEFEF"
        b["bg"] = "#AAAAAA"
        self.inputArea.delete(0, "end")
        self.inputArea.insert(0, b.realText)

    def updatePara(self):
        for i in self.selectList:
            i.place_forget()
            i.update()
        placeX = 5
        placeY = 190
        for e, p in enumerate(self.paragraphList):
            if len(p["text"]) <= 7:
                text = p["text"]
            else:
                text = p["text"][:7] + "..."
            if e == self.edit:
                bgColor = "#AAAAAA"
            else:
                bgColor = "#EFEFEF"
            paraButton = tkinter.Button(self.ui, text=text, font=("", 10), bg=bgColor)
            paraButton.realText = p["text"]
            paraButton["command"] = partial(self.updateEdit, e, paraButton)
            paraButton.place(x=placeX, y=placeY)
            paraButton.update()
            self.selectList.append(paraButton)
            width = paraButton.winfo_width()
            placeX += width + 5
            self.ui.update()
            if placeX + width > self.ui.winfo_width() and placeY < 215:
                placeY += 25
                placeX = 5

    def deletePara(self):
        self.paragraphList.pop(self.edit)
        if self.edit > 0:
            self.edit -= 1

    def addPara(self):
        self.paragraphList.insert(self.edit + 1, {"text": self.inputArea.get(),
                                                  "color": self.motdColor,
                                                  "style": [k for k, i in self.styleStates.items() if i]})
        self.inputArea.delete(0, "end")
        self.edit += 1

    def changeText(self):
        self.paragraphList[self.edit] = {"text": self.inputArea.get(),
                                         "color": self.paragraphList[self.edit]["color"],
                                         "style": self.paragraphList[self.edit]["style"]}

    def changeColor(self):
        self.paragraphList[self.edit] = {"text": self.paragraphList[self.edit]["text"],
                                         "color": self.motdColor,
                                         "style": self.paragraphList[self.edit]["style"]}

    def changeStyle(self):
        self.paragraphList[self.edit] = {"text": self.paragraphList[self.edit]["text"],
                                         "color": self.motdColor,
                                         "style": [k for k, i in self.styleStates.items() if i]}

    def setStyle(self, style, button):
        v = not self.styleStates[style]
        self.styleStates[style] = v
        if v:
            button["bg"] = "#AAAAAA"
        else:
            button["bg"] = "#EFEFEF"

    def setColor(self, color):
        self.motdColor = color
        self.colorC["text"] = colors[color]["name"]
        self.colorC["fg"] = colors[color]["fontColor"]

    def loop(self):
        self.ui.mainloop()


if __name__ == '__main__':
    mu = MotdUI()
    mu.init()
    mu.loop()
