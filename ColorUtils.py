import math


def normalize_float(f):
    """By pygal.colors"""
    """Round float errors"""
    if abs(f - round(f)) < .0000000000001:
        return round(f)
    return f


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


def rgb_to_hsl(r, g, b):
    """Convert a color in r, g, b to a color in h, s, l"""
    r = r or 0
    g = g or 0
    b = b or 0
    r /= 255
    g /= 255
    b /= 255
    max_ = max((r, g, b))
    min_ = min((r, g, b))
    d = max_ - min_

    if not d:
        h = 0
    elif r is max_:
        h = 60 * (g - b) / d
    elif g is max_:
        h = 60 * (b - r) / d + 120
    else:
        h = 60 * (r - g) / d + 240

    l = .5 * (max_ + min_)
    if not d:
        s = 0
    elif l < 0.5:
        s = .5 * d / l
    else:
        s = .5 * d / (1 - l)
    return tuple(map(normalize_float, (h % 360, s * 100, l * 100)))


def hsl_to_rgb(h, s, l):
    """Convert a color in h, s, l to a color in r, g, b"""
    h /= 360
    s /= 100
    l /= 100

    m2 = l * (s + 1) if l <= .5 else l + s - l * s
    m1 = 2 * l - m2

    def h_to_rgb(h):
        h = h % 1
        if 6 * h < 1:
            return m1 + 6 * h * (m2 - m1)
        if 2 * h < 1:
            return m2
        if 3 * h < 2:
            return m1 + 6 * (2 / 3 - h) * (m2 - m1)
        return m1

    r, g, b = map(
        lambda x: round(x * 255), map(h_to_rgb, (h + 1 / 3, h, h - 1 / 3))
    )

    return r, g, b
