#!/usr/bin/env python3
"""One-day world news image: Tuesday 17 November 2026.

Draws a hand-drawn newspaper front page that sums up the day's news
in one 1024x1024 PNG. Pure Python standard library, fully deterministic:
no network, no clock, no randomness, no downloaded images. Every picture
element is drawn by this program.

Layout: crimson masthead with a hand-drawn globe, a full-width hero
story (Middle East) with its picture on the right, a 2x2 grid of the
next four stories with coloured spine bars, and a bottom ticker strip
for the sixth story (US finance).

Run:  MAKEFUN_OUTPUT_DIR=<dir> python3 main.py
Writes <dir>/entry.png (falls back to /output/entry.png).
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette

PAPER = (247, 242, 231)      # newsprint cream
CARD = (255, 253, 246)       # story card white
INK = (26, 26, 30)           # near-black ink
CRIMSON = (164, 18, 46)      # masthead red
CRIMSON_DARK = (122, 10, 32)
GOLD = (212, 160, 44)        # rule / accent
NAVY = (20, 33, 61)          # ticker strip
SKY = (178, 205, 222)        # hero picture sky
SEA = (52, 96, 128)          # hero picture sea
SEA_DARK = (38, 74, 100)
SUN = (242, 196, 90)
STEEL = (70, 78, 88)         # carrier hull
TANKER_RED = (150, 52, 44)
WHITE = (255, 255, 255)
CREAM_TEXT = (255, 226, 214)

SPINE_EUROPE = (36, 90, 160)
SPINE_ASIA = (198, 122, 22)
SPINE_TECH = (22, 130, 110)
SPINE_MIGRATION = (122, 62, 150)

# ------------------------------------------------------- 5x7 pixel font
# Each glyph is 7 rows of 5 cells; '1' is ink, '0' is blank.
# Written from scratch for this entry.

FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00001", "00010", "00010", "00100", "01000", "10000"),
    '(': ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ')': ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

BLANK_GLYPH = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


def glyph_for(ch):
    """Return the 7-row glyph for a character (letters upper-cased)."""
    if ch == ' ':
        return BLANK_GLYPH
    return FONT.get(ch.upper(), BLANK_GLYPH)


def text_width(text, scale):
    """Pixel width of text drawn at the given scale."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


# ---------------------------------------------------------------- canvas

class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(width * height * 3)
        r, g, b = colour
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = colour[0]
            self.buf[i + 1] = colour[1]
            self.buf[i + 2] = colour[2]

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, colour)

    def frame(self, x, y, w, h, colour, thick=3):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def hline(self, x0, x1, y, colour, thick=1):
        for yy in range(y, y + thick):
            for xx in range(x0, x1 + 1):
                self.px(xx, yy, colour)

    def vline(self, x, y0, y1, colour, thick=1):
        for xx in range(x, x + thick):
            for yy in range(y0, y1 + 1):
                self.px(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line, inclusive of both ends."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, colour)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, colour):
        """Midpoint circle outline."""
        x = 0
        y = r
        d = 1 - r
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.px(cx + sx, cy + sy, colour)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def disc(self, cx, cy, r, colour):
        """Filled circle."""
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            for xx in range(cx - half, cx + half + 1):
                self.px(xx, yy, colour)

    def ellipse(self, cx, cy, rx, ry, colour):
        """Ellipse outline, parametric."""
        steps = 120
        for i in range(steps + 1):
            a = 2.0 * math.pi * i / steps
            x = int(cx + rx * math.cos(a))
            y = int(cy + ry * math.sin(a))
            self.px(x, y, colour)

    # ------------------------------------------------------------ text

    def glyph(self, x, y, ch, scale, colour):
        rows = glyph_for(ch)
        for r, row in enumerate(rows):
            for c, cell in enumerate(row):
                if cell == '1':
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, colour)
            cx += 6 * scale
        return cx

    def centred(self, cx, y, s, scale, colour):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, colour)


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    words = text.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(cv, x, y, text, scale, colour, max_chars, leading):
    """Draw a wrapped paragraph; return the y just below the last line."""
    yy = y
    for line in wrap(text, max_chars):
        cv.text(x, yy, line, scale, colour)
        yy += 7 * scale + leading
    return yy


# ------------------------------------------------------------- masthead

def draw_globe(cv, cx, cy, r, colour):
    """Hand-drawn globe: circle, latitude/longitude arcs, land blobs."""
    cv.circle(cx, cy, r, colour)
    cv.circle(cx, cy, r - 2, colour)
    # longitude arcs
    cv.ellipse(cx, cy, r // 3, r - 2, colour)
    cv.ellipse(cx, cy, 2 * r // 3, r - 2, colour)
    # latitude arcs (flattened ellipses)
    cv.ellipse(cx, cy - r // 2, r - 4, r // 4, colour)
    cv.ellipse(cx, cy + r // 2, r - 4, r // 4, colour)
    cv.hline(cx - r + 4, cx + r - 4, cy, colour)
    # rough continents: a few filled blobs inside the circle
    cv.disc(cx - r // 3, cy - r // 3, 9, colour)
    cv.disc(cx - r // 3 + 8, cy - r // 3 + 4, 6, colour)
    cv.disc(cx + r // 4, cy + r // 5, 8, colour)
    cv.disc(cx + r // 4 + 6, cy + r // 5 + 8, 5, colour)
    cv.disc(cx - r // 5, cy + r // 2, 6, colour)


def draw_masthead(cv):
    cv.rect(0, 0, W, 150, CRIMSON)
    cv.rect(0, 150, W, 6, GOLD)
    draw_globe(cv, 82, 75, 56, CREAM_TEXT)
    cv.text(168, 30, "ONE DAY ON EARTH", 6, WHITE)
    cv.text(168, 96, "TUESDAY, 17 NOVEMBER 2026", 3, CREAM_TEXT)
    cv.text(168, 122, "SIX STORIES - ONE DAY - THE WORLD IN ONE PAGE",
            2, (255, 190, 180))


# ------------------------------------------------------------- hero art

def draw_hero_picture(cv, x, y, w, h):
    """Gulf scene: carrier, tanker, drones, a mine in the strait."""
    cv.rect(x, y, w, h, SKY)
    # sun, top right
    cv.disc(x + w - 52, y + 44, 26, SUN)
    cv.circle(x + w - 52, y + 44, 30, GOLD)
    # clouds
    for cx, cy, cw in ((x + 30, y + 30, 90), (x + 150, y + 58, 70),
                       (x + 250, y + 26, 80)):
        cv.rect(cx, cy, cw, 10, WHITE)
        cv.rect(cx + 12, cy - 8, cw - 30, 10, WHITE)
    # sea
    sea_y = y + h * 3 // 5
    cv.rect(x, sea_y, w, h - (sea_y - y), SEA)
    cv.rect(x, sea_y, w, 4, SEA_DARK)
    # waves
    for wy in (sea_y + 26, sea_y + 58, sea_y + 92):
        for wx in range(x + 8, x + w - 8, 46):
            cv.line(wx, wy, wx + 22, wy - 5, (190, 220, 235))
            cv.line(wx + 22, wy - 5, wx + 44, wy, (190, 220, 235))
    # aircraft carrier, left: hull, deck, island tower
    hull_y = sea_y + 66
    cv.rect(x + 24, hull_y - 26, 190, 26, STEEL)
    cv.line(x + 24, hull_y, x + 214, hull_y - 26, STEEL)
    cv.rect(x + 14, hull_y - 32, 210, 7, (52, 58, 66))
    cv.rect(x + 150, hull_y - 58, 26, 26, (52, 58, 66))
    cv.rect(x + 158, hull_y - 70, 10, 12, (52, 58, 66))
    # little jets on the deck
    for jx in (x + 40, x + 80, x + 120):
        cv.line(jx, hull_y - 34, jx + 18, hull_y - 40, INK)
        cv.line(jx + 18, hull_y - 40, jx + 26, hull_y - 34, INK)
    # tanker, right: hull, tanks, smoke
    ty = sea_y + 78
    cv.rect(x + w - 190, ty - 30, 160, 30, TANKER_RED)
    cv.rect(x + w - 190, ty - 44, 160, 14, (120, 40, 34))
    for tx in (x + w - 176, x + w - 136, x + w - 96):
        cv.disc(tx + 12, ty - 52, 11, (232, 226, 210))
    cv.disc(x + w - 60, ty - 66, 9, (90, 90, 90))
    cv.disc(x + w - 48, ty - 80, 12, (110, 110, 110))
    cv.disc(x + w - 62, ty - 94, 8, (130, 130, 130))
    # naval mine floating in front of the carrier
    mx, my = x + 120, sea_y + 84
    cv.disc(mx, my, 12, INK)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        cv.line(mx + int(11 * math.cos(rad)), my + int(11 * math.sin(rad)),
                mx + int(19 * math.cos(rad)), my + int(19 * math.sin(rad)),
                INK)
    # drones in the sky: small crosses with dotted trails
    for dx, dy in ((x + 90, y + 110), (x + 150, y + 92), (x + 210, y + 118)):
        cv.line(dx - 8, dy, dx + 8, dy, INK)
        cv.line(dx, dy - 6, dx, dy + 6, INK)
        for t in range(1, 5):
            cv.px(dx - 14 - t * 5, dy + t, INK)
    cv.frame(x, y, w, h, INK, 4)


def draw_hero(cv):
    cv.rect(0, 156, W, 306, PAPER)
    cv.text(24, 176, "MIDDLE EAST", 3, CRIMSON)
    cv.text(24, 208, "GULF ON FIRE", 5, INK)
    cv.rect(24, 252, 330, 5, GOLD)
    body = (
        "Iran fires drones at the US radar base in Bahrain. Bahrain says "
        "it shot them down, with no damage. A fourth tanker is hit by a "
        "mine in the Strait of Hormuz in under 24 hours. A third US "
        "aircraft carrier, USS Theodore Roosevelt, sails into the region."
    )
    paragraph(cv, 24, 272, body, 2, INK, 46, 4)
    cv.text(24, 424, "4TH TANKER HIT IN 24 HOURS", 2, CRIMSON)
    draw_hero_picture(cv, 640, 172, 360, 276)


# -------------------------------------------------------------- grid cell

def draw_icon_bridge(cv, x, y, colour):
    """Suspension bridge: two towers, deck, cables."""
    cv.hline(x, x + 64, y + 44, colour, 3)
    cv.vline(x + 8, y + 6, y + 44, colour, 3)
    cv.vline(x + 52, y + 6, y + 44, colour, 3)
    cv.line(x + 8, y + 6, x + 32, y + 44, colour)
    cv.line(x + 52, y + 6, x + 32, y + 44, colour)
    cv.line(x + 8, y + 6, x + 52, y + 6, colour)
    for fx in (x + 18, x + 28, x + 38, x + 48):
        cv.vline(fx, y + 16, y + 44, colour, 2)


def draw_icon_summit(cv, x, y, colour):
    """Three flags on poles, for a summit meeting."""
    for i, fx in enumerate((x + 6, x + 26, x + 46)):
        cv.vline(fx, y + 4, y + 52, colour, 3)
        cv.rect(fx + 3, y + 4 + i * 2, 14, 10,
                (CRIMSON, GOLD, SPINE_EUROPE)[i])


def draw_icon_chip(cv, x, y, colour):
    """AI chip: square body, pins, inner core."""
    cv.frame(x + 8, y + 8, 48, 40, colour, 3)
    cv.frame(x + 20, y + 18, 24, 20, colour, 3)
    for px in (x + 16, x + 28, x + 40, x + 52):
        cv.vline(px, y, y + 8, colour, 2)
        cv.vline(px, y + 48, y + 56, colour, 2)
    for py in (y + 16, y + 28, y + 40):
        cv.hline(x, x + 8, py, colour, 2)
        cv.hline(x + 56, x + 64, py, colour, 2)


def draw_icon_hub(cv, x, y, colour):
    """Return hub: a circle with arrows pointing in."""
    cv.circle(x + 32, y + 28, 18, colour)
    cv.circle(x + 32, y + 28, 15, colour)
    for ang in (45, 135, 225, 315):
        rad = math.radians(ang)
        x0 = x + 32 + int(26 * math.cos(rad))
        y0 = y + 28 + int(26 * math.sin(rad))
        x1 = x + 32 + int(19 * math.cos(rad))
        y1 = y + 28 + int(19 * math.sin(rad))
        cv.line(x0, y0, x1, y1, colour)


CELL_STORIES = [
    {
        "kicker": "EUROPE",
        "headline": "BRIDGE WAR",
        "spine": SPINE_EUROPE,
        "icon": draw_icon_bridge,
        "body": (
            "Ukraine badly damages the Kerch bridge to Crimea for a second "
            "day. Russian missiles hit Kyiv's bridges over the Dnipro, "
            "cutting heat, water and power. Russia says it shot down "
            "1,336 drones."
        ),
    },
    {
        "kicker": "ASIA",
        "headline": "ASIA SUMMIT",
        "spine": SPINE_ASIA,
        "icon": draw_icon_summit,
        "body": (
            "Trump flies to the APEC leaders' meeting in Shenzhen. A "
            "trilateral meeting with Xi and Putin on nuclear risks is set "
            "for 19 November."
        ),
    },
    {
        "kicker": "TECH",
        "headline": "CHIP CURBS",
        "spine": SPINE_TECH,
        "icon": draw_icon_chip,
        "body": (
            "The US moves to close the loophole letting China rent US "
            "computing power. Singapore seeks trusted access to advanced "
            "AI chips."
        ),
    },
    {
        "kicker": "MIGRATION",
        "headline": "RWANDA HUB",
        "spine": SPINE_MIGRATION,
        "icon": draw_icon_hub,
        "body": (
            "Five EU states unveil plans in Vienna to send rejected asylum "
            "seekers to a return hub in Rwanda, with first transfers aimed "
            "for 2027."
        ),
    },
]


def draw_cell(cv, x, y, w, h, story):
    cv.rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK, 3)
    cv.rect(x + 3, y + 3, 10, h - 6, story["spine"])
    tx = x + 26
    cv.text(tx, y + 14, story["kicker"], 2, story["spine"])
    cv.text(tx, y + 38, story["headline"], 3, INK)
    cv.rect(tx, y + 66, 120, 4, story["spine"])
    story["icon"](cv, x + w - 92, y + 12, story["spine"])
    paragraph(cv, tx, y + 82, story["body"], 2, INK, 34, 3)


def draw_grid(cv):
    cv.rect(0, 462, W, 418, PAPER)
    positions = ((16, 470), (520, 470), (16, 674), (520, 674))
    for (x, y), story in zip(positions, CELL_STORIES):
        draw_cell(cv, x, y, 488, 194, story)


# ------------------------------------------------------------ ticker strip

def draw_ticker(cv):
    cv.rect(0, 880, W, 144, NAVY)
    cv.rect(0, 880, W, 5, GOLD)
    cv.rect(24, 898, 150, 30, GOLD)
    cv.text(32, 904, "US FINANCE", 2, NAVY)
    cv.text(24, 936, "CHASE BUG FREEZES ZELLE", 3, WHITE)
    body = (
        "A JPMorgan Chase software bug slows online banking and Zelle "
        "payments across the US. Chase says it was not a cyberattack, and "
        "service was restored by Monday evening."
    )
    paragraph(cv, 24, 968, body, 2, (214, 226, 240), 76, 3)


# ------------------------------------------------------------------- png

def encode_png(cv):
    """Encode the canvas as a PNG (filter 0 on every scanline)."""
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        start = yy * cv.w * 3
        raw += cv.buf[start:start + cv.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data))
        out += tag
        out += data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_hero(cv)
    draw_grid(cv)
    draw_ticker(cv)
    data = encode_png(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
