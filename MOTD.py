from enum import Enum


class ComponentType:
    normal = "normal"
    gradient_color = "gradient_color"


class ChatStyle(Enum):
    obfuscated = r"\u00A7k"
    bold = r"\u00A7l"
    strikethrough = r"\u00A7m"
    underline = r"\u00A7n"
    italic = r"\u00A7o"
    reset = r"\u00A7r"

    @staticmethod
    def of(obfuscated=None, bold=None, strikethrough=None, underline=None, italic=None, reset=None):
        args = locals()
        return "".join([i.value for i in [i for i in ChatStyle] if eval(i.name, globals(), args)])

    @staticmethod
    def of_ui(obfuscated=None, bold=None, strikethrough=None, underline=None, italic=None, reset=None):
        args = locals()
        return [i.name for i in [i for i in ChatStyle] if eval(i.name, globals(), args)]

    @staticmethod
    def des(style: str):
        result = []
        for i in style.split(r"\u00A7"):
            match i:
                case "k":
                    result.append(ChatStyle.obfuscated.name)
                case "l":
                    result.append(ChatStyle.bold.name)
                case "m":
                    result.append(ChatStyle.strikethrough.name)
                case "n":
                    result.append(ChatStyle.underline.name)
                case "o":
                    result.append(ChatStyle.italic.name)
                case "r":
                    result.append(ChatStyle.reset.name)
        return result


class ChatColor:
    black = r"\u00A70"
    dark_blue = r"\u00A71"
    dark_green = r"\u00A72"
    dark_aqua = r"\u00A73"
    dark_red = r"\u00A74"
    dark_purple = r"\u00A75"
    gold = r"\u00A76"
    gray = r"\u00A77"
    dark_gray = r"\u00A78"
    blue = r"\u00A79"
    green = r"\u00A7a"
    aqua = r"\u00A7b"
    red = r"\u00A7c"
    light_purple = r"\u00A7d"
    yellow = r"\u00A7e"
    white = r"\u00A7f"

    black_hex = "#000000"
    dark_blue_hex = "#0000AA"
    dark_green_hex = "#00AA00"
    dark_aqua_hex = "#00AAAA"
    dark_red_hex = "#AA0000"
    dark_purple_hex = "#AA00AA"
    gold_hex = "#FFAA00"
    gray_hex = "#AAAAAA"
    dark_gray_hex = "#555555"
    blue_hex = "#5555FF"
    green_hex = "#55FF55"
    aqua_hex = "#55FFFF"
    red_hex = "#FF5555"
    light_purple_hex = "#FF55FF"
    yellow_hex = "#FFFF55"
    white_hex = "#FFFFFF"

    @staticmethod
    def of(color_hex: str):
        if color_hex[0] == r"#":
            return r"\u00A7x\u00A7" + r"\u00A7".join(color_hex[1:7].upper())
        return r"\u00A70"

    @staticmethod
    def hex(color: str):
        if len(color.split(r"\u00A7")) == 2:
            match color.split(r"\u00A7")[1]:
                case "0":
                    return ChatColor.black
                case "1":
                    return ChatColor.dark_blue_hex
                case "2":
                    return ChatColor.dark_green_hex
                case "3":
                    return ChatColor.dark_aqua_hex
                case "4":
                    return ChatColor.dark_red_hex
                case "5":
                    return ChatColor.dark_purple_hex
                case "6":
                    return ChatColor.gold_hex
                case "7":
                    return ChatColor.gray_hex
                case "8":
                    return ChatColor.dark_gray_hex
                case "9":
                    return ChatColor.blue_hex
                case "a":
                    return ChatColor.green_hex
                case "b":
                    return ChatColor.aqua_hex
                case "c":
                    return ChatColor.red_hex
                case "d":
                    return ChatColor.light_purple_hex
                case "e":
                    return ChatColor.yellow_hex
                case "f":
                    return ChatColor.white_hex
        else:
            return "#" + "".join(color.split(r"\u00A7")[2:])


class Show(dict):
    def __init__(self, component_type: str, colors: list, styles: list, text: str = None, start_color: str = None, end_color: str = None, style: str = None):
        super().__init__()
        self["component_type"] = component_type
        self["text"] = text
        self["colors"] = colors
        self["styles"] = styles

        self["start_color"] = start_color
        self["end_color"] = end_color
        self["style"] = style

    def set_component_type(self, component_type: str):
        self["component_type"] = component_type

    def set_text(self, text: str):
        self["text"] = text

    def set_colors(self, colors: list):
        self["colors"] = colors

    def set_styles(self, styles: list):
        self["styles"] = styles


class Component(dict):
    def __init__(self, text: str, color: str = ChatColor.white, style: str = ""):
        super().__init__()
        self["text"]: str = text
        self["color"]: str = color
        self["style"]: str = style

    def set_text(self, text: str):
        self["text"] = text

    def set_color(self, color: str):
        self["color"] = color

    def set_style(self, style: str):
        self["style"] = style

    def to_unicode(self):
        return self["color"] + self["style"] + self["text"].encode("unicode-escape").decode().replace(r"\\", "\\")


class UIComponent(Component):
    def __init__(self, show: Show, text: str, color: str = ChatColor.white, style: str = ""):
        super().__init__(text, color, style)
        self["show"] = show

    def set_component_type(self, component_type: str):
        self["show"].set_component_type(component_type)

    def set_text(self, text: str):
        self["text"] = text

    def set_color(self, color: str):
        self["color"] = color

    def set_style(self, style: str):
        self["style"] = style

    @staticmethod
    def build_by_raw(raw):
        return UIComponent(raw["show"], raw["text"], raw["color"], raw["style"])


class MOTD(list):
    def __init__(self):
        super().__init__()

    def add_component(self, text: str, color: str = ChatColor.white, style: str = ""):
        self.append(Component(text, color, style))

    def insert_component(self, index: int, text: str, color: str = ChatColor.white, style: str = ""):
        self.insert(index, Component(text, color, style))

    def del_component(self, index):
        self.pop(index)

    def set_component_text(self, index: int, text: str):
        self[index].set_text(text)

    def set_component_color(self, index: int, color: str):
        self[index].set_color(color)

    def set_component_style(self, index: int, style: str):
        self[index].set_style(style)

    def to_unicode(self):
        return "".join([i.to_unicode() for i in self])

    def __hash__(self):
        return hash(str([i for i in self]))


class MOTDGenerator(MOTD):
    def __init__(self):
        super().__init__()

    def add_component(self, text: str, color: str = ChatColor.white, style: str = ""):
        self.append(UIComponent(Show(ComponentType.normal, [ChatColor.hex(color)], ChatStyle.des(style), text), text, color, style))

    def insert_component(self, index: int, text: str, color: str = ChatColor.white, style: str = ""):
        self.insert(index, UIComponent(Show(ComponentType.normal, [ChatColor.hex(color)], ChatStyle.des(style), text), text, color, style))

    def set_component_text(self, index: int, text: str):
        if self[index]["show"]["component_type"] == ComponentType.normal:
            self[index].set_text(text)
            self[index]["show"].set_text(text)
        else:
            start_color = self[index]["show"]["start_color"]
            end_color = self[index]["show"]["end_color"]
            show, text = self.get_gradient_color_result(text, start_color, end_color, self[index]["show"]["style"])
            self[index]["show"] = show
            self[index].set_text(text)

    def set_component_color(self, index: int, color: str, end_color: str | None = None):
        if not end_color:
            self[index].set_color(color)
            self[index]["show"].set_colors([ChatColor.hex(color)])
        else:
            style = self[index]["show"]["style"]
            show, text = self.get_gradient_color_result(self[index]["show"]["text"], color, end_color, style)
            self[index]["show"] = show
            self[index].set_text(text)

    def set_component_style(self, index: int, style: str):
        if self[index]["show"]["component_type"] == ComponentType.normal:
            self[index].set_style(style)
            self[index]["show"].set_styles(ChatStyle.des(style))
        else:
            start_color = self[index]["show"]["start_color"]
            end_color = self[index]["show"]["end_color"]
            show, text = self.get_gradient_color_result(self[index]["show"]["text"], start_color, end_color, style)
            self[index]["show"] = show
            self[index].set_text(text)

    def add_gradient_color_component(self, text: str, start_color: str, end_color: str, style=""):
        show, text = self.get_gradient_color_result(text, start_color, end_color, style)
        self.append(UIComponent(show, text, color=""))

    def insert_gradient_color_component(self, index: int, text: str, start_color: str, end_color: str, style=""):
        show, text = self.get_gradient_color_result(text, start_color, end_color, style)
        self.insert(index, UIComponent(show, text, color=""))

    @staticmethod
    def get_gradient_color_result(text: str, start_color: str, end_color: str, style=""):
        r1, g1, b1 = tuple(int(start_color.replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(end_color.replace("#", "")[i:i + 2], 16) for i in (0, 2, 4))

        num_colors = len(text.replace(" ", ""))
        gradient = []
        counter = 0
        for chunk in text.split(" "):
            color = []
            for i in range(counter, len(chunk) + counter):
                counter += 1
                color.append((int(r1 + (r2 - r1) * i / num_colors),
                              int(g1 + (g2 - g1) * i / num_colors),
                              int(b1 + (b2 - b1) * i / num_colors)))
            gradient.append(color)

        colors = []
        for i in gradient:
            for (r, g, b) in i:
                colors.append(f"#{r:02x}{g:02x}{b:02x}")
            colors.append(f"#000000")
        colors.pop(-1)

        return (Show(ComponentType.gradient_color, colors, ChatStyle.des(style), text, start_color, end_color, style),
                " ".join(["".join([ChatColor.of(f"#{r:02x}{g:02x}{b:02x}") + style + chunk[index]
                                   for index, (r, g, b) in enumerate(colors)])
                          for chunk, colors in zip(text.split(" "), gradient)]))

    def add_by_raw(self, raw):
        self.append(raw)

    def __repr__(self):
        return f'<{self.__class__.__name__} len={len(self)} show={"".join([i["show"]["text"] for i in self])} raw={[i for i in self]}>'
