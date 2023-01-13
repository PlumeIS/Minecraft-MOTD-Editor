import math


def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b


def rgb2hsv(rgb):
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    delta = c_max - c_min
    h = 0
    if delta == 0:
        h = 0
    elif c_max == r:
        h = (g - b) / delta % 6
    elif c_max == g:
        h = (b - r) / delta + 2
    elif c_max == b:
        h = (r - g) / delta + 4
    h = h * 60
    s = 0 if c_max == 0 else delta / c_max
    v = c_max
    return h, s, v


def rgb2hex(rgb):
    return '#' + ''.join(['0{0:x}'.format(v) if v < 16 else '{0:x}'.format(v) for v in rgb])


def hex2rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
