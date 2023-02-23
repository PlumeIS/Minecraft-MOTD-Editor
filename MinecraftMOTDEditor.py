import json
import random
import re
import string
import sys
import time
from threading import Thread

import PySide6
import pyperclip
from PySide6 import QtGui
from PySide6.QtCore import QRectF, Qt, QThread
from PySide6.QtGui import QLinearGradient, QColor, QGradient, QBrush, QFont, QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QGroupBox, QPushButton, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsView, QLabel, QGraphicsRectItem, QLineEdit, QSpacerItem,
    QSizePolicy, QCheckBox, QFrame, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QMainWindow, QMenuBar
)

import MOTD
from ColorUtils import *


def style_parser(prefix, styles):
    style = ""
    for i in styles:
        if i == MOTD.ChatStyle.bold.name:
            style += "font-weight:bold;"
        if i == MOTD.ChatStyle.strikethrough.name:
            style += "text-decoration:line-through;"
        if i == MOTD.ChatStyle.underline.name:
            style += "text-decoration:underline;"
        if i == MOTD.ChatStyle.italic.name:
            style += "font-style:italic;"
        if i == MOTD.ChatStyle.reset.name:
            style = ""
    return prefix + style + "}"


def show_parser(color, style):
    style_sheet = f"QLabel{{color:{color};"
    return style_parser(style_sheet, style)


class ListClearListener(Thread):
    def __init__(self, list_widget: QListWidget, func):
        super().__init__()
        self.daemon = True
        self.list_widget = list_widget
        self.func = func
        self.is_start = False

    def run(self) -> None:
        while True:
            try:
                if self.is_start and not self.list_widget.selectedIndexes():
                    self.is_start = False
                    self.func()
            except RuntimeError:
                pass

    def continue_listener(self):
        self.is_start = True


class TextRandomer(QThread):
    def __init__(self, interval):
        super().__init__()
        self.labels = {}
        self.interval = interval
        self.counter = 0
        self.is_run = True

    def run(self) -> None:
        while self.is_run:
            self.counter += 1
            labels = self.labels.copy()
            for k, v in labels.items():
                try:
                    k.setText("".join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(v)]))
                except RuntimeError:
                    labels.pop(k)
                time.sleep(self.interval / len(labels))

    def clear(self):
        self.labels = {}

    def add(self, label):
        self.labels[label] = len(label.text())


class MOTDView(QFrame):
    def __init__(self, height, **kwargs):
        super().__init__(**kwargs)
        QtGui.QFontDatabase.addApplicationFont("minecraft.ttf")
        self.setFixedHeight(height)
        self.setStyleSheet('QWidget{background-image: url("view.png")}')
        self.adding_count = 0
        self.index = -1

        self.line_layout = QVBoxLayout()
        self.first_line = QHBoxLayout()
        self.first_line.setSpacing(0)
        space = QLabel()
        space.setFixedWidth(0)
        self.second_line = QHBoxLayout()
        self.second_line.setSpacing(0)
        self.second_line.addWidget(space)
        self.air_line = QHBoxLayout()
        self.first_line.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.second_line.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.line_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.line_layout.addLayout(self.first_line)
        self.line_layout.addLayout(self.second_line)
        self.line_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(self.line_layout)
        self.font = QFont()
        self.font.setFamily("Minecraft AE")
        self.font.setPixelSize(16)
        self.randomer = TextRandomer(0.02)
        self.randomer.start()

    def add_component(self, text, style, style_sheet, line):
        paragraph = QLabel(text)
        if text == "":
            paragraph.setFixedWidth(0)
        paragraph.setFont(self.font)
        paragraph.setFixedHeight(16)
        if MOTD.ChatStyle.reset.name in style:
            paragraph.setStyleSheet("QLabel{color:#AAAAAA}")
        else:
            if MOTD.ChatStyle.underline.name in style:
                paragraph.setText(f"<u>{text}</u>")
            paragraph.setStyleSheet(style_sheet)
            if MOTD.ChatStyle.obfuscated.name in style:
                if MOTD.ChatStyle.italic.name in style:
                    paragraph.setFixedWidth(paragraph.fontMetrics().horizontalAdvance("".join(["A" for _ in text])) + 2)
                else:
                    paragraph.setFixedWidth(paragraph.fontMetrics().horizontalAdvance("".join(["A" for _ in text])))
                self.randomer.add(paragraph)
        line.addWidget(paragraph)

    def update_view(self, motd):
        self.adding_count = 0
        for i in range(self.first_line.count()):
            try:
                self.first_line.itemAt(i).widget().deleteLater()
            except AttributeError:
                self.first_line.removeItem(self.first_line.itemAt(i))
        for i in range(self.second_line.count()):
            try:
                self.second_line.itemAt(i).widget().deleteLater()
            except AttributeError:
                self.second_line.removeItem(self.second_line.itemAt(i))
        space = QLabel("")
        space.setFixedWidth(0)
        self.second_line.addWidget(space)

        self.randomer.clear()
        adding_line = self.first_line
        for i in motd:
            if i["show"]["component_type"] == MOTD.ComponentType.normal:
                if len(i["show"]["text"].split(r"\n")) > 1:
                    for text in i["show"]["text"].split(r"\n"):
                        self.add_component(text.replace(r"\t", "      "), i["show"]["styles"], show_parser(i["show"]["colors"][0], i["show"]["styles"]),
                                           adding_line)
                        if self.adding_count == 0:
                            adding_line = self.second_line
                        elif self.adding_count == 2:
                            adding_line = self.air_line
                        self.adding_count += 1
                else:
                    self.add_component(i["show"]["text"].replace(r"\t", "      "), i["show"]["styles"],
                                       show_parser(i["show"]["colors"][0], i["show"]["styles"]),
                                       adding_line)
            if i["show"]["component_type"] == MOTD.ComponentType.gradient_color:
                if len(i["show"]["text"].split(r"\n")) > 1:
                    colors = []
                    index = 0
                    for text in i["show"]["text"].split(r"\n"):
                        colors.append(i["show"]["colors"][index:index + len(text)])
                        index += len(text) + 1
                    for text, colors in zip(i["show"]["text"].split(r"\n"), colors):
                        for char, color in zip(text, colors):
                            self.add_component(char.replace(r"\t", "    "), i["show"]["styles"], show_parser(color, i["show"]["styles"]), adding_line)
                        if self.adding_count == 0:
                            adding_line = self.second_line
                        elif self.adding_count == 2:
                            adding_line = self.air_line
                        self.adding_count += 1
                else:
                    for char, color in zip(i["show"]["text"], i["show"]["colors"]):
                        self.add_component(char.replace(r"\t", "    "), i["show"]["styles"], show_parser(color, i["show"]["styles"]), adding_line)

        self.first_line.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.second_line.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


class ColorView(QGraphicsView):
    def __init__(self, size, color):
        super().__init__()
        self.size = size
        self.setFixedSize(*size)
        self.color_scene = QGraphicsScene()
        self.setScene(self.color_scene)
        self.color_item = QGraphicsRectItem(0, 0, self.size[0] - 5, self.size[1] - 5)
        self.update_color(color)

    def update_color(self, color):
        self.color_scene = QGraphicsScene()
        self.setScene(self.color_scene)
        self.color_item = QGraphicsRectItem(0, 0, self.size[0] - 5, self.size[0] - 5)
        self.color_item.setBrush(QBrush(QColor(*color, 255)))
        self.color_scene.addItem(self.color_item)
        self.color_scene.clearSelection()


class ColorPalette(QGraphicsView):
    def __init__(self, parent, size, strip):
        super().__init__()
        self.parent = parent
        self.strip = strip
        self.setFixedSize(*size)
        self.update_palette(0, 0)
        self.is_press = False
        self.waiting = 0

        self.h = 0
        self.v = 1

    def only_update_pos(self, x, y):
        rect = QRectF(0, 0, self.width() - 2,
                      self.height() - 2)
        scene = QGraphicsScene(rect)
        self.setScene(scene)
        color_gradient = QLinearGradient(0, 0, self.width(), 0)
        color_gradient.setSpread(QGradient.RepeatSpread)
        color_gradient.setColorAt(0, QColor(255, 0, 0, 255))
        color_gradient.setColorAt(0.166, QColor(255, 255, 0, 255))
        color_gradient.setColorAt(0.333, QColor(0, 255, 0, 255))
        color_gradient.setColorAt(0.5, QColor(0, 255, 255, 255))
        color_gradient.setColorAt(0.666, QColor(0, 0, 255, 255))
        color_gradient.setColorAt(0.833, QColor(255, 0, 255, 255))
        color_gradient.setColorAt(1, QColor(255, 0, 0, 255))
        black_gradient = QLinearGradient(0, 0, 0, self.height())
        black_gradient.setSpread(QGradient.RepeatSpread)
        black_gradient.setColorAt(0, QColor(0, 0, 0, 0))
        black_gradient.setColorAt(1, QColor(0, 0, 0, 250))
        item = QGraphicsEllipseItem(-2, -2, 4, 4)
        item.setPos(x, y)
        item.setBrush(Qt.black)
        scene.setBackgroundBrush(color_gradient)
        scene.setForegroundBrush(black_gradient)
        scene.addItem(item)
        scene.clearSelection()

    def update_palette(self, select_x, select_y):
        select_x = select_x if select_x >= 0 else 0
        select_x = select_x if select_x < self.width() else self.width()
        select_y = select_y if select_y >= 0 else 0
        select_y = select_y if select_y < self.height() else self.height()

        self.parent.is_updating = True
        self.only_update_pos(select_x, select_y)

        self.h = select_x / self.size().width() * 360
        self.v = 1 - (select_y / self.size().height())

        self.strip.update_color(hsv2rgb(self.h, 1, self.v), hsv2rgb(self.h, 0, self.v))
        self.parent.custom_color()
        self.parent.is_updating = False

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.is_press = True
        self.update_palette(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.is_press = False

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        if self.is_press:
            self.update_palette(event.position().x(), event.position().y())


class ColorStrip(QGraphicsView):
    def __init__(self, parent, size):
        super().__init__()
        self.parent = parent
        self.setFixedSize(*size)
        self.is_press = False
        self.color_top = QColor(255, 0, 0, 255)
        self.color_bottom = QColor(0, 0, 0, 255)
        self.update_strip(0, 0)
        self.y = 0
        self.s = 0

    def update_color(self, color_top, color_bottom):
        self.color_top = QColor(*color_top, 255)
        self.color_bottom = QColor(*color_bottom, 255)
        self.update_strip(0, self.y)

    def only_update_pos(self, y, color_top, color_bottom):
        self.color_top = QColor(*color_top, 255)
        self.color_bottom = QColor(*color_bottom, 255)
        rect = QRectF(0, 0, self.width() - 2,
                      self.height() - 2)
        scene = QGraphicsScene(rect)
        self.setScene(scene)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setSpread(QGradient.RepeatSpread)
        gradient.setColorAt(0, QColor(self.color_top))
        gradient.setColorAt(1, QColor(self.color_bottom))
        scene.setBackgroundBrush(gradient)
        item = QGraphicsRectItem(0, 0, 25, 6)
        item.setBrush(Qt.black)
        item.setPos(0, y)
        scene.addItem(item)
        scene.clearSelection()

    def update_strip(self, select_x, select_y):
        if 0 <= select_x <= self.width() and -1 <= select_y <= self.height() - 8:
            self.parent.is_updating = True
            self.only_update_pos(select_y, (self.color_top.red(), self.color_top.green(), self.color_top.blue()),
                                 (self.color_bottom.red(), self.color_bottom.green(), self.color_bottom.blue()))

            self.y = select_y
            self.s = 1 - (max(select_y, 0) / (self.height() - 8))
            self.parent.custom_color()
            self.parent.is_updating = False

    def mousePressEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.is_press = True
        self.update_strip(event.position().x(), event.position().y())

    def mouseReleaseEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        self.is_press = False

    def mouseMoveEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:
        if self.is_press:
            self.update_strip(event.position().x(), event.position().y())


class MOTDGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOTD Editor - 1.0.5")
        self.setGeometry(100, 100, 800, 600)
        self.setMouseTracking(True)
        self.generator = MOTDGeneratorWidget()
        self.setCentralWidget(self.generator)

        self.file = None

        self.menu_bar = QMenuBar()

        self.file_menu = self.menu_bar.addMenu("文件")

        self.load_action = QAction("打开(.motd)", self)
        self.load_action.triggered.connect(self.load_from_file)
        self.file_menu.addAction(self.load_action)

        self.file_menu.addSeparator()
        self.save_action = QAction("保存(.motd)", self)
        self.save_action.triggered.connect(self.save_with_file)
        self.save_action.setEnabled(False)
        self.file_menu.addAction(self.save_action)
        self.save_as_action = QAction("另存为(.motd)", self)
        self.save_as_action.triggered.connect(self.save_as_file)
        self.save_as_action.setEnabled(False)
        self.file_menu.addAction(self.save_as_action)

        self.setMenuBar(self.menu_bar)

    def load_from_file(self):
        file = QFileDialog.getOpenFileName(self, "加载文件", ".", "MOTD服务器简介文件 (*.motd)")
        self.file = file[0]
        self.generator.load_from_file(file)
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)

    def save_with_file(self):
        with open(self.file, "w", encoding="utf-8") as file:
            file.write(self.generator.to_file_data())
        QMessageBox(self.generator).information(self.generator, "保存成功!", "保存成功!")

    def save_as_file(self):
        self.generator.save_as_file()

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        self.generator.view_widget.randomer.is_run = False


class MOTDGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.is_updating = False
        self.color = r"\u00A7f"
        self.custom_color_hex = "#ff0000"
        self.color_r = 255
        self.color_g = 0
        self.color_b = 0
        self.gradient_color_start_hex = "#ff0000"
        self.gradient_color_end_hex = "#ff0000"
        self.motd = MOTD.MOTDGenerator()
        self.select_index = -1

        self.central_layout = QHBoxLayout(self)
        self.control_layout = QVBoxLayout(self)
        self.setLayout(self.central_layout)
        self.central_layout.addLayout(self.control_layout)

        self.color_group = QGroupBox("颜色选择", self)
        self.color_group.setObjectName("ColorGroup")
        self.color_group_layout = QVBoxLayout()
        self.color_group.setLayout(self.color_group_layout)
        self.control_layout.addWidget(self.color_group)

        self.color_button_group = QGroupBox("常规颜色")
        self.color_button_group.setStyleSheet('QPushButton{text-decoration: none; text-shadow: 0px 0px 10px #000;}')
        self.color_button_layout = QGridLayout()
        self.color_button_group.setLayout(self.color_button_layout)
        self.color_group_layout.addWidget(self.color_button_group)

        self.black_color_button = QPushButton("黑色")
        self.black_color_button.setStyleSheet('QPushButton{color:#000000}')
        self.dark_blue_color_button = QPushButton("深蓝色")
        self.dark_blue_color_button.setStyleSheet('QPushButton{color:#0000AA}')
        self.dark_green_color_button = QPushButton("深绿色")
        self.dark_green_color_button.setStyleSheet('QPushButton{color:#00AA00}')
        self.dark_aqua_color_button = QPushButton("湖蓝色")
        self.dark_aqua_color_button.setStyleSheet('QPushButton{color:#00AAAA}')
        self.dark_red_color_button = QPushButton("深红色")
        self.dark_red_color_button.setStyleSheet('QPushButton{color:#AA0000}')
        self.dark_purple_color_button = QPushButton("紫色")
        self.dark_purple_color_button.setStyleSheet('QPushButton{color:#AA00AA}')
        self.gold_color_button = QPushButton("金色")
        self.gold_color_button.setStyleSheet('QPushButton{color:#FFAA00}')
        self.gray_color_button = QPushButton("灰色")
        self.gray_color_button.setStyleSheet('QPushButton{color:#AAAAAA}')
        self.dark_gray_color_button = QPushButton("深灰色")
        self.dark_gray_color_button.setStyleSheet('QPushButton{color:#555555}')
        self.blue_color_button = QPushButton("蓝色")
        self.blue_color_button.setStyleSheet('QPushButton{color:#5555FF}')
        self.green_color_button = QPushButton("绿色")
        self.green_color_button.setStyleSheet('QPushButton{color:#55FF55}')
        self.aqua_color_button = QPushButton("天蓝色")
        self.aqua_color_button.setStyleSheet('QPushButton{color:#55FFFF}')
        self.red_color_button = QPushButton("红色")
        self.red_color_button.setStyleSheet('QPushButton{color:#FF5555}')
        self.light_purple_color_button = QPushButton("粉红色")
        self.light_purple_color_button.setStyleSheet('QPushButton{color:#FF55FF}')
        self.yellow_color_button = QPushButton("黄色")
        self.yellow_color_button.setStyleSheet('QPushButton{color:#FFFF55}')
        self.white_color_button = QPushButton("白色")
        self.white_color_button.setStyleSheet('QPushButton{color:#FFFFFF}')

        self.black_color_button.clicked.connect(lambda: self.update_normal_color(f'黑色', MOTD.ChatColor.black, MOTD.ChatColor.black_hex))
        self.dark_blue_color_button.clicked.connect(lambda: self.update_normal_color(f'深蓝色', MOTD.ChatColor.dark_blue, MOTD.ChatColor.dark_blue_hex))
        self.dark_green_color_button.clicked.connect(lambda: self.update_normal_color(f'深绿色', MOTD.ChatColor.dark_green, MOTD.ChatColor.dark_green_hex))
        self.dark_aqua_color_button.clicked.connect(lambda: self.update_normal_color(f'湖蓝色', MOTD.ChatColor.dark_aqua, MOTD.ChatColor.dark_aqua_hex))
        self.dark_red_color_button.clicked.connect(lambda: self.update_normal_color(f'深红色', MOTD.ChatColor.dark_red, MOTD.ChatColor.dark_red_hex))
        self.dark_purple_color_button.clicked.connect(lambda: self.update_normal_color(f'紫色', MOTD.ChatColor.dark_purple, MOTD.ChatColor.dark_purple_hex))
        self.gold_color_button.clicked.connect(lambda: self.update_normal_color(f'金色', MOTD.ChatColor.gold, MOTD.ChatColor.gold_hex))
        self.gray_color_button.clicked.connect(lambda: self.update_normal_color(f'灰色', MOTD.ChatColor.gray, MOTD.ChatColor.gray_hex))
        self.dark_gray_color_button.clicked.connect(lambda: self.update_normal_color(f'深灰色', MOTD.ChatColor.dark_gray, MOTD.ChatColor.dark_gray_hex))
        self.blue_color_button.clicked.connect(lambda: self.update_normal_color(f'蓝色', MOTD.ChatColor.blue, MOTD.ChatColor.blue_hex))
        self.green_color_button.clicked.connect(lambda: self.update_normal_color(f'绿色', MOTD.ChatColor.green, MOTD.ChatColor.green_hex))
        self.aqua_color_button.clicked.connect(lambda: self.update_normal_color(f'天蓝色', MOTD.ChatColor.aqua, MOTD.ChatColor.aqua_hex))
        self.red_color_button.clicked.connect(lambda: self.update_normal_color(f'红色', MOTD.ChatColor.red, MOTD.ChatColor.red_hex))
        self.light_purple_color_button.clicked.connect(
            lambda: self.update_normal_color(f'粉红色', MOTD.ChatColor.light_purple, MOTD.ChatColor.light_purple_hex))
        self.yellow_color_button.clicked.connect(lambda: self.update_normal_color(f'黄色', MOTD.ChatColor.yellow, MOTD.ChatColor.yellow_hex))
        self.white_color_button.clicked.connect(lambda: self.update_normal_color(f'白色', MOTD.ChatColor.white, MOTD.ChatColor.white_hex))

        self.color_button_layout.addWidget(self.black_color_button, 0, 0)
        self.color_button_layout.addWidget(self.dark_blue_color_button, 0, 1)
        self.color_button_layout.addWidget(self.dark_green_color_button, 0, 2)
        self.color_button_layout.addWidget(self.dark_aqua_color_button, 0, 3)
        self.color_button_layout.addWidget(self.dark_red_color_button, 0, 4)
        self.color_button_layout.addWidget(self.dark_purple_color_button, 0, 5)
        self.color_button_layout.addWidget(self.gold_color_button, 0, 6)
        self.color_button_layout.addWidget(self.gray_color_button, 0, 7)
        self.color_button_layout.addWidget(self.dark_gray_color_button, 1, 0)
        self.color_button_layout.addWidget(self.blue_color_button, 1, 1)
        self.color_button_layout.addWidget(self.green_color_button, 1, 2)
        self.color_button_layout.addWidget(self.aqua_color_button, 1, 3)
        self.color_button_layout.addWidget(self.red_color_button, 1, 4)
        self.color_button_layout.addWidget(self.light_purple_color_button, 1, 5)
        self.color_button_layout.addWidget(self.yellow_color_button, 1, 6)
        self.color_button_layout.addWidget(self.white_color_button, 1, 7)

        self.custom_color_group = QGroupBox("自定义颜色")
        self.custom_color_layout = QHBoxLayout()
        self.custom_color_group.setLayout(self.custom_color_layout)
        self.color_group_layout.addWidget(self.custom_color_group)

        self.color_strip = ColorStrip(self, (25, 150))
        self.color_palette = ColorPalette(self, (150, 150), self.color_strip)
        self.custom_color_layout.addWidget(self.color_palette)
        self.custom_color_layout.addWidget(self.color_strip)

        self.custom_color_setting_layout = QVBoxLayout()
        self.custom_color_setting_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.color_hint = QLabel("颜色预览:")
        self.color_box = QHBoxLayout()
        self.color_view = ColorView((20, 20), (255, 0, 0))
        self.color_box.addWidget(self.color_hint)
        self.color_box.addWidget(self.color_view)
        self.color_box.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.custom_color_setting_layout.addLayout(self.color_box)

        self.color_hex_box = QHBoxLayout()
        self.color_hex_hint = QLabel("Hex:")
        self.color_hex_input = QLineEdit("#ff0000")
        self.color_hex_input.textChanged.connect(self.update_palette_by_hex)
        self.color_hex_input.setMaximumWidth(100)
        self.color_hex_box.addWidget(self.color_hex_hint)
        self.color_hex_box.addWidget(self.color_hex_input)
        self.color_hex_box.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.custom_color_setting_layout.addLayout(self.color_hex_box)

        self.color_r_hint = QLabel("R:")
        self.color_g_hint = QLabel("G:")
        self.color_b_hint = QLabel("B:")
        self.color_r_input = QLineEdit("255")
        self.color_r_input.textChanged.connect(self.update_palette_by_rgb)
        self.color_g_input = QLineEdit("0")
        self.color_g_input.textChanged.connect(self.update_palette_by_rgb)
        self.color_b_input = QLineEdit("0")
        self.color_b_input.textChanged.connect(self.update_palette_by_rgb)
        self.color_r_input.setMaximumWidth(70)
        self.color_g_input.setMaximumWidth(70)
        self.color_b_input.setMaximumWidth(70)
        self.color_r_box = QHBoxLayout()
        self.color_g_box = QHBoxLayout()
        self.color_b_box = QHBoxLayout()
        self.color_r_box.addWidget(self.color_r_hint)
        self.color_r_box.addWidget(self.color_r_input)
        self.color_r_box.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.color_g_box.addWidget(self.color_g_hint)
        self.color_g_box.addWidget(self.color_g_input)
        self.color_g_box.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.color_b_box.addWidget(self.color_b_hint)
        self.color_b_box.addWidget(self.color_b_input)
        self.color_b_box.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.custom_color_setting_layout.addLayout(self.color_r_box)
        self.custom_color_setting_layout.addLayout(self.color_g_box)
        self.custom_color_setting_layout.addLayout(self.color_b_box)

        self.set_custom_color_button = QPushButton("应用颜色")
        self.set_custom_color_button.setMinimumWidth(100)
        self.set_custom_color_button.clicked.connect(lambda: self.update_custom_color(f"自定义颜色: {self.custom_color_hex}", self.custom_color_hex))
        self.custom_color_setting_layout.addWidget(self.set_custom_color_button, alignment=Qt.AlignLeft)

        self.custom_color_setting_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.custom_color_layout.addLayout(self.custom_color_setting_layout)

        self.gradient_color_layout = QVBoxLayout()
        self.gradient_color_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.gradient_color_setting_box = QGroupBox("渐变颜色设置")
        self.gradient_color_setting_box.setMinimumHeight(150)
        self.gradient_color_setting_layout = QHBoxLayout()
        self.gradient_color_setting_box.setLayout(self.gradient_color_setting_layout)

        self.gradient_color_start_layout = QVBoxLayout()
        self.gradient_color_start_view_box = QHBoxLayout()
        self.gradient_color_start_view_hint = QLabel("初始颜色预览:")
        self.gradient_color_start_view_item = ColorView((20, 20), (255, 0, 0))
        self.gradient_color_start_view_box.addWidget(self.gradient_color_start_view_hint)
        self.gradient_color_start_view_box.addWidget(self.gradient_color_start_view_item)
        self.gradient_color_start_hex_box = QHBoxLayout()
        self.gradient_color_start_hex_hint = QLabel("Hex:")
        self.gradient_color_start_hex_input = QLineEdit("#ff0000")
        self.gradient_color_start_hex_input.textChanged.connect(lambda: self.update_gradient_color("start"))
        self.gradient_color_start_hex_box.addWidget(self.gradient_color_start_hex_hint)
        self.gradient_color_start_hex_box.addWidget(self.gradient_color_start_hex_input)
        self.gradient_color_start_setting_button = QPushButton("将自定义颜色填入")
        self.gradient_color_start_setting_button.clicked.connect(lambda: self.copy_custom_to_gradient_color("start"))
        self.gradient_color_start_layout.addLayout(self.gradient_color_start_view_box)
        self.gradient_color_start_layout.addLayout(self.gradient_color_start_hex_box)
        self.gradient_color_start_layout.addWidget(self.gradient_color_start_setting_button)

        self.gradient_color_end_layout = QVBoxLayout()
        self.gradient_color_end_view_box = QHBoxLayout()
        self.gradient_color_end_view_hint = QLabel("末尾颜色预览:")
        self.gradient_color_end_view_item = ColorView((20, 20), (255, 0, 0))
        self.gradient_color_end_view_box.addWidget(self.gradient_color_end_view_hint)
        self.gradient_color_end_view_box.addWidget(self.gradient_color_end_view_item)
        self.gradient_color_end_hex_box = QHBoxLayout()
        self.gradient_color_end_hex_hint = QLabel("Hex:")
        self.gradient_color_end_hex_input = QLineEdit("#ff0000")
        self.gradient_color_end_hex_input.textChanged.connect(lambda: self.update_gradient_color("end"))
        self.gradient_color_end_hex_box.addWidget(self.gradient_color_end_hex_hint)
        self.gradient_color_end_hex_box.addWidget(self.gradient_color_end_hex_input)
        self.gradient_color_end_setting_button = QPushButton("将自定义颜色填入")
        self.gradient_color_end_setting_button.clicked.connect(lambda: self.copy_custom_to_gradient_color("end"))
        self.gradient_color_end_layout.addLayout(self.gradient_color_end_view_box)
        self.gradient_color_end_layout.addLayout(self.gradient_color_end_hex_box)
        self.gradient_color_end_layout.addWidget(self.gradient_color_end_setting_button)

        self.gradient_color_setting_layout.addLayout(self.gradient_color_start_layout)
        self.h_spliter = QFrame()
        self.h_spliter.setFixedWidth(1)
        self.h_spliter.setStyleSheet('QFrame{background:#dcdcdc}')
        self.gradient_color_setting_layout.addWidget(self.h_spliter)
        self.gradient_color_setting_layout.addLayout(self.gradient_color_end_layout)

        self.gradient_color_layout.addWidget(self.gradient_color_setting_box)
        self.gradient_color_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.custom_color_layout.addLayout(self.gradient_color_layout)
        self.custom_color_group.setMaximumHeight(190)

        self.style_group = QGroupBox("样式设置")
        self.control_layout.addWidget(self.style_group)
        self.style_layout = QHBoxLayout()
        self.style_group.setLayout(self.style_layout)
        self.style_obfuscated = QCheckBox("随机字符")
        self.style_bold = QCheckBox("粗体")
        self.style_bold.setStyleSheet('QCheckBox{font-weight:bold}')
        self.style_strikethrough = QCheckBox("删除线")
        self.style_strikethrough.setStyleSheet('QCheckBox{text-decoration:line-through}')
        self.style_underline = QCheckBox("下划线")
        self.style_underline.setStyleSheet('QCheckBox{text-decoration:underline}')
        self.style_italic = QCheckBox("斜体")
        self.style_italic.setStyleSheet('QCheckBox{font-style:italic}')
        self.style_reset = QCheckBox("重置文字样式")

        self.style_layout.addWidget(self.style_obfuscated)
        self.style_layout.addWidget(self.style_bold)
        self.style_layout.addWidget(self.style_strikethrough)
        self.style_layout.addWidget(self.style_underline)
        self.style_layout.addWidget(self.style_italic)
        self.style_layout.addWidget(self.style_reset)

        self.edit_layout = QVBoxLayout()
        self.control_layout.addLayout(self.edit_layout)

        self.text_edit_layout = QHBoxLayout()

        self.paragraph_edit_layout = QVBoxLayout()
        self.paragraph_add_layout = QHBoxLayout()
        self.text_input = QLineEdit()
        self.paragraph_add_button = QPushButton("添加")
        self.paragraph_add_button.clicked.connect(self.add_component)
        self.paragraph_remove_button = QPushButton("删除")
        self.paragraph_remove_button.clicked.connect(self.remove_component)
        self.paragraph_remove_button.setStyleSheet('QPushButton{color:#b46565}')
        self.paragraph_add_layout.addWidget(self.text_input)
        self.paragraph_add_layout.addWidget(self.paragraph_add_button)
        self.paragraph_add_layout.addWidget(self.paragraph_remove_button)
        self.paragraph_remove_button.setEnabled(False)

        self.paragraph_change_layout = QHBoxLayout()
        self.paragraph_gradient_color_add_button = QPushButton("添加渐变颜色段落")
        self.paragraph_gradient_color_add_button.clicked.connect(self.add_gradient_color_component)
        self.paragraph_text_change_button = QPushButton("更改文本")
        self.paragraph_text_change_button.clicked.connect(self.change_text)
        self.paragraph_style_change_button = QPushButton("更改颜色样式")
        self.paragraph_style_change_button.clicked.connect(self.change_color_style)
        self.paragraph_change_layout.addWidget(self.paragraph_gradient_color_add_button, 3)
        self.paragraph_change_layout.addWidget(self.paragraph_text_change_button, 1)
        self.paragraph_change_layout.addWidget(self.paragraph_style_change_button, 1)
        self.paragraph_text_change_button.setEnabled(False)
        self.paragraph_style_change_button.setEnabled(False)

        self.view_widget = MOTDView(60, parent=self)
        self.view_widget.update_view(self.motd)

        self.paragraph_edit_layout.addLayout(self.paragraph_add_layout)
        self.paragraph_edit_layout.addLayout(self.paragraph_change_layout)

        self.result_box = QGroupBox("结果")
        self.result_layout = QVBoxLayout()
        self.result_box.setLayout(self.result_layout)
        self.result_output_layout = QHBoxLayout()
        self.result_output_line = QLineEdit()
        self.result_output_line.setEnabled(False)
        self.result_output_line.setReadOnly(True)
        self.result_output_copy_button = QPushButton("复制")
        self.result_output_copy_button.clicked.connect(self.copy_result)
        self.result_output_layout.addWidget(self.result_output_line)
        self.result_output_layout.addWidget(self.result_output_copy_button)
        self.result_layout.addLayout(self.result_output_layout)
        self.result_file_layout = QHBoxLayout()
        self.result_file_save_button = QPushButton("保存为文件(.motd)")
        self.result_file_save_button.clicked.connect(self.save_as_file)
        self.result_file_load_button = QPushButton("从文件加载(.motd)")
        self.result_file_load_button.clicked.connect(self.load_from_file)
        self.result_file_layout.addWidget(self.result_file_save_button)
        self.result_file_layout.addWidget(self.result_file_load_button)
        self.result_layout.addLayout(self.result_file_layout)

        self.paragraph_edit_layout.addWidget(self.result_box)

        self.v_spliter = QFrame()
        self.v_spliter.setFixedHeight(1)
        self.v_spliter.setStyleSheet('QFrame{background:#dcdcdc}')

        self.text_edit_layout.addLayout(self.paragraph_edit_layout)
        self.edit_layout.addLayout(self.text_edit_layout)

        self.view_widget.update_view(self.motd)
        self.select_list = QListWidget()
        self.select_list.clicked.connect(self.select_list_click_event)
        self.list_listener = ListClearListener(self.select_list, self.on_select_clear)
        self.list_listener.start()
        self.list_listener.continue_listener()
        self.update_select_list()
        self.text_edit_layout.addWidget(self.select_list)

        self.control_layout.addWidget(self.v_spliter)
        self.control_layout.addWidget(self.view_widget)

    def update_normal_color(self, show, color, color_hex):
        self.color_group.setTitle(f"颜色选择: {show}")
        self.color_group.setStyleSheet(f"#ColorGroup{{color: {color_hex}}}")
        self.color = color

    def update_custom_color(self, show, color_hex):
        self.color_group.setTitle(f"颜色选择: {show}")
        self.color_group.setStyleSheet(f"#ColorGroup{{color: {color_hex}}}")
        self.color = MOTD.ChatColor.of(color_hex)

    def update_palette_by_hex(self):
        color_hex = self.color_hex_input.text()
        if re.match("^#[A-Fa-f0-9]{6}$", color_hex) and not self.is_updating:
            self.is_updating = True
            h, s, v = rgb2hsv(hex2rgb(color_hex))
            self.update_palette(h, s, v)
            self.is_updating = False

    def update_palette(self, h, s, v):
        color_hex = rgb2hex(hsv2rgb(h, s, v))
        x = int((h / 360) * self.color_palette.width())
        y = int((1 - v) * self.color_palette.height())
        self.color_palette.only_update_pos(x, y)
        y = int((1 - s) * (self.color_strip.height() - 8))
        self.color_strip.only_update_pos(y, hsv2rgb(h, 1, v), hsv2rgb(h, 0, v))
        self.color_view.update_color(hex2rgb(color_hex))
        self.color_palette.h = h
        self.color_strip.s = s
        self.color_palette.v = v
        rgb = hsv2rgb(h, s, v)
        self.color_r = rgb[0]
        self.color_g = rgb[1]
        self.color_b = rgb[2]
        self.color_r_input.setText(str(rgb[0]))
        self.color_g_input.setText(str(rgb[1]))
        self.color_b_input.setText(str(rgb[2]))
        self.custom_color_hex = color_hex

    def update_palette_by_rgb(self):
        try:
            self.is_updating = True
            r = self.color_r_input.text()
            g = self.color_g_input.text()
            b = self.color_b_input.text()
            if 0 <= int(r) <= 255 and 0 <= int(g) <= 255 and 0 <= int(b) <= 255 and not self.is_updating:
                self.update_palette(*rgb2hsv((int(r), int(g), int(b))))
                self.color_hex_input.setText(rgb2hex((int(r), int(g), int(b))))
            self.is_updating = False
        except AttributeError:
            pass
        except ValueError:
            pass
        finally:
            self.is_updating = False

    def custom_color(self, h=None, s=None, v=None):
        try:
            h = h or self.color_palette.h
            s = s or self.color_strip.s
            v = v or self.color_palette.v
            rgb = hsv2rgb(h, s, v)
            self.color_r = rgb[0]
            self.color_g = rgb[1]
            self.color_b = rgb[2]
            color_hex = rgb2hex(rgb)
            self.color_view.update_color(rgb)
            self.color_hex_input.setText(color_hex)
            self.color_r_input.setText(str(rgb[0]))
            self.color_g_input.setText(str(rgb[1]))
            self.color_b_input.setText(str(rgb[2]))
            self.custom_color_hex = color_hex
        except AttributeError:
            pass

    def update_gradient_color(self, w):
        if w == "start" and re.match("^#[A-Fa-f0-9]{6}$", self.gradient_color_start_hex_input.text()):
            self.gradient_color_start_view_item.update_color(hex2rgb(self.gradient_color_start_hex_input.text()))
            self.gradient_color_start_hex = self.gradient_color_start_hex_input.text()
        if w == "end" and re.match("^#[A-Fa-f0-9]{6}$", self.gradient_color_end_hex_input.text()):
            self.gradient_color_end_view_item.update_color(hex2rgb(self.gradient_color_start_hex_input.text()))
            self.gradient_color_end_hex = self.gradient_color_end_hex_input.text()

    def copy_custom_to_gradient_color(self, w):
        if w == "start":
            self.gradient_color_start_view_item.update_color(hex2rgb(self.custom_color_hex))
            self.gradient_color_start_hex_input.setText(self.custom_color_hex)
            self.gradient_color_start_hex = self.custom_color_hex
        else:
            self.gradient_color_end_hex_input.setText(self.custom_color_hex)
            self.gradient_color_end_hex = self.custom_color_hex
            self.gradient_color_end_view_item.update_color(hex2rgb(self.custom_color_hex))

    def on_select_clear(self):
        self.select_list.setCurrentRow(self.select_list.count() - 1)
        self.list_listener.continue_listener()
        self.paragraph_add_button.setText("添加")
        self.paragraph_gradient_color_add_button.setText("添加渐变颜色段落")
        self.paragraph_remove_button.setEnabled(False)
        self.paragraph_text_change_button.setEnabled(False)
        self.paragraph_style_change_button.setEnabled(False)
        self.paragraph_remove_button.setStyleSheet("QPushButton{color:#b46565}")
        self.select_index = -1
        self.text_input.setText("")

    def select_list_click_event(self, index):
        if index.row() == self.select_list.count() - 1:
            self.select_index = -1
            self.paragraph_add_button.setText("添加")
            self.paragraph_gradient_color_add_button.setText("添加渐变颜色段落")
            self.paragraph_remove_button.setEnabled(False)
            self.paragraph_text_change_button.setEnabled(False)
            self.paragraph_style_change_button.setEnabled(False)
            self.paragraph_remove_button.setStyleSheet("QPushButton{color:#b46565}")
            self.text_input.setText("")
        else:
            self.paragraph_add_button.setText("上方插入")
            self.paragraph_gradient_color_add_button.setText("插入渐变颜色段落")
            self.paragraph_remove_button.setEnabled(True)
            self.paragraph_text_change_button.setEnabled(True)
            self.paragraph_style_change_button.setEnabled(True)
            self.paragraph_remove_button.setStyleSheet('QPushButton{color:#cc0000}')
            self.select_index = index.row()
            self.select_list.setCurrentRow(index.row())
            self.text_input.setText(self.motd[self.select_index]["show"]["text"])

    def update_select_list(self):
        self.select_list.clear()
        for i in [i["show"]["text"] for i in self.motd]:
            self.select_list.addItem(QListWidgetItem(i))
        item = QListWidgetItem("<添加新段落>")
        item.setForeground(QColor(120, 120, 120))
        self.select_list.addItem(item)
        if self.select_index == -1:
            pass
        else:
            self.select_list.setCurrentRow(self.select_index)

    def add_component(self):
        style = MOTD.ChatStyle.of(self.style_obfuscated.isChecked(),
                                  self.style_bold.isChecked(),
                                  self.style_strikethrough.isChecked(),
                                  self.style_underline.isChecked(),
                                  self.style_italic.isChecked(),
                                  self.style_reset.isChecked())
        if self.select_index == -1:
            self.motd.add_component(self.text_input.text(), self.color, style)
        else:
            self.motd.insert_component(self.select_index, self.text_input.text(), self.color, style)
            self.select_index += 1
        self.list_listener.is_start = False
        self.update_select_list()
        self.view_widget.update_view(self.motd)
        self.update_result()
        self.list_listener.is_start = True
        self.text_input.setText("")

    def add_gradient_color_component(self):
        style = MOTD.ChatStyle.of(self.style_obfuscated.isChecked(),
                                  self.style_bold.isChecked(),
                                  self.style_strikethrough.isChecked(),
                                  self.style_underline.isChecked(),
                                  self.style_italic.isChecked(),
                                  self.style_reset.isChecked())
        if self.select_index == -1:
            self.motd.add_gradient_color_component(self.text_input.text(), self.gradient_color_start_hex, self.gradient_color_end_hex, style)
        else:
            self.motd.insert_gradient_color_component(self.select_index - 1, self.text_input.text(), self.gradient_color_start_hex, self.gradient_color_end_hex,
                                                      style)
        self.list_listener.is_start = False
        self.update_select_list()
        self.view_widget.update_view(self.motd)
        self.update_result()
        self.list_listener.is_start = True
        self.text_input.setText("")

    def remove_component(self):
        self.motd.pop(self.select_index)
        if self.select_index == self.select_list.count() - 2:
            self.on_select_clear()
        else:
            self.text_input.setText(self.motd[self.select_index]["show"]["text"])
        self.list_listener.is_start = False
        self.update_select_list()
        self.view_widget.update_view(self.motd)
        self.update_result()
        self.list_listener.is_start = True

    def change_text(self):
        self.motd.set_component_text(self.select_index, self.text_input.text())
        self.list_listener.is_start = False
        self.update_select_list()
        self.view_widget.update_view(self.motd)
        self.update_result()
        self.list_listener.is_start = True

    def change_color_style(self):
        if self.motd[self.select_index]["show"]["component_type"] == MOTD.ComponentType.normal:
            self.motd.set_component_color(self.select_index, self.color)
        else:
            self.motd.set_component_color(self.select_index, self.gradient_color_start_hex, self.gradient_color_end_hex)
        style = MOTD.ChatStyle.of(self.style_obfuscated.isChecked(),
                                  self.style_bold.isChecked(),
                                  self.style_strikethrough.isChecked(),
                                  self.style_underline.isChecked(),
                                  self.style_italic.isChecked(),
                                  self.style_reset.isChecked())
        self.motd.set_component_style(self.select_index, style)
        self.list_listener.is_start = False
        self.update_select_list()
        self.view_widget.update_view(self.motd)
        self.update_result()
        self.list_listener.is_start = True

    def copy_result(self):
        pyperclip.copy(self.result_output_line.text())
        QMessageBox(self).information(self, "结果", "复制成功!")

    def update_result(self):
        self.result_output_line.setEnabled(True)
        self.result_output_line.setText(self.motd.to_unicode())

    def to_file_data(self):
        return json.dumps(self.motd, indent=True)

    def load(self, file_data):
        old_motd = self.motd
        try:
            self.motd = MOTD.MOTDGenerator()
            for i in file_data:
                self.motd.append(MOTD.UIComponent.build_by_raw(i))
            self.list_listener.is_start = False
            self.update_select_list()
            self.view_widget.update_view(self.motd)
            self.update_result()
            self.list_listener.is_start = True
        except Exception as err:
            QMessageBox(self).warning(self, "加载失败!", f"原因:{err}")
            self.motd = old_motd
            self.list_listener.is_start = False
            self.update_select_list()
            self.view_widget.update_view(self.motd)
            self.update_result()
            self.list_listener.is_start = True
        else:
            QMessageBox(self).information(self, "加载成功!", f"MOTD文件已加载")

    def save_as_file(self):
        if not self.result_output_line.text() == "":
            file = QFileDialog.getSaveFileName(self, "保存文件", ".", "MOTD服务器简介文件 (*.motd)")
            if file[0]:
                with open(file[0], "w") as save_file:
                    save_file.write(json.dumps(self.motd, indent=True))
                QMessageBox(self).information(self, "保存成功!", f"保存成功!")

    def load_from_file(self, file=None):
        file = file or QFileDialog.getOpenFileName(self, "加载文件", ".", "MOTD服务器简介文件 (*.motd)")
        if file[0]:
            with open(file[0], "r") as load_file:
                self.load(json.loads(load_file.read()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MOTDGeneratorWindow()
    window.show()
    if len(sys.argv) >= 2:
        window.generator.load_from_file((sys.argv[1], ""))
    sys.exit(app.exec())
