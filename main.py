#!/usr/bin/env python3
"""make.fun news-image-20261117 entry: draws one front page that sums up
Tuesday 17 November 2026 in a single image.

Six stories, chosen for breadth across regions and fields:

  1. MIDDLE EAST (hero) - the Gulf on fire: Iran fires drones at a US
     radar in Bahrain; a fourth tanker is hit by a mine in the Strait of
     Hormuz; a third US carrier is in the region.
  2. EUROPE - bridge war: Ukraine damages the Crimea bridge while Russia
     strikes Kyiv's bridges.
  3. ASIA - Trump flies to APEC in Shenzhen; nuclear talks with Xi and
     Putin are set for 19 November.
  4. TECH - the US closes the AI chip loophole; Singapore seeks trusted
     access to advanced chips.
  5. MIGRATION - five EU states plan a Rwanda return hub for rejected
     asylum seekers.
  6. US FINANCE (ticker strip) - a JPMorgan Chase software bug slows
     online banking and Zelle payments across the US.

Layout (distinct from the 13 November entry): a crimson masthead with a
hand-drawn globe, one full-width hero story with its picture on the
right, a 2x2 grid of stories marked by coloured spine bars, and a bottom
ticker strip for the sixth story.

Every pixel is drawn by this program at run time: no photos, no downloaded
images, no network, no clock, no randomness. Pure standard library, so it
runs exactly the same in the grader's Python 3.13 sandbox. It writes one
1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
Deterministic: two runs write byte-identical files.
"""

import math
import os
import struct
import zlib
from pathlib import Path

# Logical canvas, upscaled 4x with nearest neighbour (chunky pixel look that
# stays legible when the image is shown small).
W = 256
H = 256
SCALE = 4
OUT_W = W * SCALE
OUT_H = H * SCALE

# --- palette ---------------------------------------------------------------
PAPER = (250, 244, 230)
CRIMSON = (168, 32, 38)
CREAM = (250, 244, 230)
GOLD = (212, 160, 40)
INK = (28, 28, 32)
BODY = (64, 64, 72)
BORDER = (120, 118, 112)
WHITE = (255, 255, 255)
PANEL_BG = (255, 255, 255)

CAT_MIDEAST = (166, 42, 42)
CAT_EUROPE = (38, 74, 150)
CAT_ASIA = (14, 110, 105)
CAT_TECH = (74, 120, 10)
CAT_MIGRATION = (96, 60, 140)
CAT_FINANCE = (60, 64, 80)

SEA_LIGHT = (168, 208, 235)
SEA_DARK = (52, 110, 165)
SKY_BLUE = (135, 190, 225)
CHIP_GREEN = (38, 90, 10)
DARK_GRAY = (70, 72, 78)
RED = (192, 57, 43)
ORANGE = (235, 120, 30)
FLAME = (255, 176, 32)
TAN = (210, 180, 120)
LEAF = (60, 140, 60)

# --- 5x7 pixel font (uppercase, digits, a little punctuation) --------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    lines = []
    for word in text.split(" "):
        if not lines or len(lines[-1]) + 1 + len(word) > max_chars:
            lines.append(word)
        else:
            lines[-1] += " " + word
    return lines


# --- canvas ----------------------------------------------------------------
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)

    def set(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(H, y1 + 1)):
            for x in range(max(0, x0), min(W, x1 + 1)):
                self.set(x, y, color)

    def rect_outline(self, x0, y0, x1, y1, color):
        self.fill_rect(x0, y0, x1, y0, color)
        self.fill_rect(x0, y1, x1, y1, color)
        self.fill_rect(x0, y0, x0, y1, color)
        self.fill_rect(x1, y0, x1, y1, color)

    def circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            self.circle(x, y, max(0, width // 2), color)

    def arc(self, cx, cy, r, a0, a1, color, thick=2):
        """Arc of a circle; angles in degrees, y-down screen coords."""
        for y in range(cy - r - thick, cy + r + thick + 1):
            for x in range(cx - r - thick, cx + r + thick + 1):
                dx, dy = x - cx, y - cy
                d = math.hypot(dx, dy)
                if abs(d - r) > thick / 2 + 0.6:
                    continue
                ang = math.degrees(math.atan2(dy, dx))
                if a0 <= ang <= a1:
                    self.set(x, y, color)

    def triangle(self, p0, p1, p2, color):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]

        def sign(ax, ay, bx, by, cx, cy):
            return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

        for y in range(min(ys), max(ys) + 1):
            for x in range(min(xs), max(xs) + 1):
                d0 = sign(x, y, p0[0], p0[1], p1[0], p1[1])
                d1 = sign(x, y, p1[0], p1[1], p2[0], p2[1])
                d2 = sign(x, y, p2[0], p2[1], p0[0], p0[1])
                if (d0 >= 0 and d1 >= 0 and d2 >= 0) or (
                    d0 <= 0 and d1 <= 0 and d2 <= 0
                ):
                    self.set(x, y, color)

    def rounded_rect(self, x0, y0, x1, y1, r, color):
        self.fill_rect(x0 + r, y0, x1 - r, y1, color)
        self.fill_rect(x0, y0 + r, x1, y1 - r, color)
        self.circle(x0 + r, y0 + r, r, color)
        self.circle(x1 - r, y0 + r, r, color)
        self.circle(x0 + r, y1 - r, r, color)
        self.circle(x1 - r, y1 - r, r, color)

    def text(self, text, x, y, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "1":
                        self.fill_rect(
                            cx + col * scale,
                            y + row * scale,
                            cx + col * scale + scale - 1,
                            y + row * scale + scale - 1,
                            color,
                        )
            cx += 6 * scale

    def text_bold(self, text, x, y, scale, color):
        self.text(text, x, y, scale, color)
        self.text(text, x + 1, y, scale, color)


# --- PNG encoding (stdlib only) --------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    # Upscale 4x nearest neighbour, filter byte 0 per row.
    raw = bytearray()
    for ly in range(H):
        row = bytearray()
        for lx in range(W):
            i = (ly * W + lx) * 3
            px = canvas.px[i : i + 3]
            row += px * SCALE
        raw.append(0)
        raw += row
        for _ in range(SCALE - 1):
            raw.append(0)
            raw += row
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", OUT_W, OUT_H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# --- icons -----------------------------------------------------------------
def icon_gulf_big(c, ix, iy):
    """60x60: sky, sea, radar island, tanker ablaze, drone overhead."""
    c.fill_rect(ix, iy, ix + 59, iy + 34, SKY_BLUE)
    c.fill_rect(ix, iy + 35, ix + 59, iy + 59, SEA_DARK)
    c.line(ix, iy + 39, ix + 59, iy + 39, WHITE, width=1)
    c.line(ix, iy + 47, ix + 59, iy + 47, WHITE, width=1)
    c.line(ix, iy + 54, ix + 59, iy + 54, WHITE, width=1)
    # Distant tanker silhouette.
    c.fill_rect(ix + 30, iy + 36, ix + 41, iy + 39, DARK_GRAY)
    c.fill_rect(ix + 37, iy + 32, ix + 40, iy + 36, DARK_GRAY)
    # Radar island, bottom left.
    c.ellipse(ix + 12, iy + 50, 11, 5, LEAF)
    c.line(ix + 12, iy + 38, ix + 12, iy + 50, DARK_GRAY, width=1)
    c.arc(ix + 12, iy + 38, 6, 190, 350, WHITE, thick=2)
    c.circle(ix + 12, iy + 38, 1, RED)
    # Main tanker, centre right.
    c.fill_rect(ix + 24, iy + 42, ix + 54, iy + 50, DARK_GRAY)
    c.fill_rect(ix + 44, iy + 34, ix + 51, iy + 42, DARK_GRAY)
    c.fill_rect(ix + 46, iy + 30, ix + 49, iy + 34, RED)
    # Smoke + flame burst above the funnel.
    c.circle(ix + 47, iy + 26, 3, (160, 160, 160))
    c.circle(ix + 48, iy + 21, 2, (190, 190, 190))
    c.circle(ix + 47, iy + 17, 3, ORANGE)
    c.circle(ix + 47, iy + 18, 2, RED)
    for k in range(4):
        ang = math.radians(k * 90 + 45)
        c.line(
            round(ix + 47 + math.cos(ang) * 4),
            round(iy + 17 + math.sin(ang) * 4),
            round(ix + 47 + math.cos(ang) * 7),
            round(iy + 17 + math.sin(ang) * 7),
            ORANGE,
            width=1,
        )
    # Drone, top right.
    c.circle(ix + 53, iy + 8, 2, DARK_GRAY)
    c.line(ix + 49, iy + 5, ix + 57, iy + 5, DARK_GRAY, width=1)
    c.line(ix + 49, iy + 11, ix + 57, iy + 11, DARK_GRAY, width=1)
    c.line(ix + 49, iy + 5, ix + 53, iy + 8, DARK_GRAY, width=1)
    c.line(ix + 57, iy + 5, ix + 53, iy + 8, DARK_GRAY, width=1)
    c.line(ix + 49, iy + 11, ix + 53, iy + 8, DARK_GRAY, width=1)
    c.line(ix + 57, iy + 11, ix + 53, iy + 8, DARK_GRAY, width=1)


def icon_bridge(c, ix, iy):
    """28x28: a bridge broken in two over a river, blast in the gap."""
    c.fill_rect(ix, iy, ix + 27, iy + 19, SEA_LIGHT)
    c.fill_rect(ix, iy + 20, ix + 27, iy + 27, SEA_DARK)
    # Drones overhead.
    for dx, dy in ((ix + 5, iy + 3), (ix + 14, iy + 2), (ix + 23, iy + 4)):
        c.circle(dx, dy, 1, DARK_GRAY)
        c.line(dx - 2, dy - 1, dx + 2, dy - 1, DARK_GRAY, width=1)
    # Bridge halves.
    c.fill_rect(ix + 1, iy + 12, ix + 11, iy + 14, DARK_GRAY)
    c.fill_rect(ix + 17, iy + 12, ix + 27, iy + 14, DARK_GRAY)
    c.fill_rect(ix + 3, iy + 15, ix + 4, iy + 20, DARK_GRAY)
    c.fill_rect(ix + 24, iy + 15, ix + 25, iy + 20, DARK_GRAY)
    # Blast in the gap.
    c.circle(ix + 14, iy + 10, 3, FLAME)
    for k in range(6):
        ang = math.radians(k * 60)
        c.line(
            round(ix + 14 + math.cos(ang) * 4),
            round(iy + 10 + math.sin(ang) * 4),
            round(ix + 14 + math.cos(ang) * 6),
            round(iy + 10 + math.sin(ang) * 6),
            ORANGE,
            width=1,
        )
    c.circle(ix + 11, iy + 6, 2, (160, 160, 160))
    c.circle(ix + 17, iy + 5, 2, (190, 190, 190))


def icon_summit(c, ix, iy):
    """28x28: three flags (US, China, Russia) over a Shenzhen skyline."""
    c.fill_rect(ix, iy, ix + 27, iy + 27, (200, 220, 240))
    # Skyline blocks.
    for bx, bh in ((ix + 1, 8), (ix + 7, 12), (ix + 13, 7), (ix + 19, 10),
                   (ix + 24, 6)):
        c.fill_rect(bx, iy + 28 - bh, bx + 4, iy + 27, (70, 85, 110))
    # Flag poles.
    for px in (ix + 5, ix + 13, ix + 21):
        c.line(px, iy + 3, px, iy + 18, DARK_GRAY, width=1)
    # US flag: stripes + blue canton.
    c.fill_rect(ix + 6, iy + 3, ix + 11, iy + 7, (178, 34, 52))
    c.fill_rect(ix + 6, iy + 4, ix + 11, iy + 4, WHITE)
    c.fill_rect(ix + 6, iy + 6, ix + 11, iy + 6, WHITE)
    c.fill_rect(ix + 6, iy + 3, ix + 8, iy + 5, (40, 60, 120))
    # China flag: red + yellow star.
    c.fill_rect(ix + 14, iy + 3, ix + 19, iy + 7, (222, 41, 16))
    c.circle(ix + 16, iy + 5, 1, (255, 222, 0))
    # Russia flag: white / blue / red bands.
    c.fill_rect(ix + 22, iy + 3, ix + 27, iy + 4, WHITE)
    c.fill_rect(ix + 22, iy + 5, ix + 27, iy + 5, (40, 90, 180))
    c.fill_rect(ix + 22, iy + 6, ix + 27, iy + 7, (200, 40, 40))


def icon_chip(c, ix, iy):
    """28x28: a green AI chip with pins and a red falling arrow."""
    c.fill_rect(ix, iy, ix + 27, iy + 27, (238, 238, 232))
    for yy in (iy + 9, iy + 14, iy + 19):
        c.line(ix + 1, yy, ix + 3, yy, DARK_GRAY, width=1)
        c.line(ix + 24, yy, ix + 26, yy, DARK_GRAY, width=1)
    c.rounded_rect(ix + 4, iy + 4, ix + 23, iy + 20, 2, CHIP_GREEN)
    c.text("AI", ix + 9, iy + 9, 1, WHITE)
    c.line(ix + 24, iy + 21, ix + 24, iy + 25, RED, width=2)
    c.triangle(
        (ix + 21, iy + 24), (ix + 27, iy + 24), (ix + 24, iy + 27), RED
    )


def icon_rwanda(c, ix, iy):
    """28x28: Africa in tan, a red pin on Rwanda, a plane flying in."""
    c.fill_rect(ix, iy, ix + 27, iy + 27, (222, 232, 222))
    c.triangle((ix + 6, iy + 3), (ix + 20, iy + 2), (ix + 24, iy + 9), TAN)
    c.triangle((ix + 6, iy + 3), (ix + 24, iy + 9), (ix + 21, iy + 20), TAN)
    c.triangle((ix + 6, iy + 3), (ix + 21, iy + 20), (ix + 15, iy + 26), TAN)
    c.triangle((ix + 6, iy + 3), (ix + 15, iy + 26), (ix + 8, iy + 21), TAN)
    c.triangle((ix + 6, iy + 3), (ix + 8, iy + 21), (ix + 4, iy + 9), TAN)
    # Dashed flight path from the top left to the pin.
    for k in range(5):
        c.circle(ix + 5 + k * 3, iy + 4 + k * 2, 1, DARK_GRAY)
    # Little plane.
    c.triangle((ix + 2, iy + 2), (ix + 7, iy + 4), (ix + 2, iy + 6), WHITE)
    # Pin on Rwanda (east-central Africa).
    c.circle(ix + 19, iy + 13, 2, RED)
    c.arc(ix + 19, iy + 13, 5, 0, 360, RED, thick=1)


def icon_bank(c, ix, iy):
    """22x22: a bank with columns, crossed by a red glitch zigzag."""
    c.fill_rect(ix, iy, ix + 21, iy + 21, (238, 238, 232))
    c.triangle((ix + 2, iy + 8), (ix + 19, iy + 8), (ix + 10, iy + 2), (40, 60, 120))
    c.fill_rect(ix + 2, iy + 8, ix + 19, iy + 10, (40, 60, 120))
    for cx in (ix + 4, ix + 10, ix + 16):
        c.fill_rect(cx, iy + 11, cx + 1, iy + 18, (40, 60, 120))
    c.fill_rect(ix + 2, iy + 19, ix + 19, iy + 21, (40, 60, 120))
    c.line(ix + 3, iy + 12, ix + 8, iy + 16, RED, width=1)
    c.line(ix + 8, iy + 16, ix + 13, iy + 12, RED, width=1)
    c.line(ix + 13, iy + 12, ix + 18, iy + 16, RED, width=1)


# --- stories ----------------------------------------------------------------
# (category tag, tag colour, headline, body, icon key)
GRID_STORIES = [
    (
        "EUROPE",
        CAT_EUROPE,
        "BRIDGE WAR",
        "UKRAINE HITS CRIMEA BRIDGE, RUSSIA HITS KYIV BRIDGES",
        "bridge",
    ),
    (
        "ASIA",
        CAT_ASIA,
        "ASIA SUMMIT",
        "TRUMP FLIES TO APEC FOR NUCLEAR TALKS WITH XI, PUTIN",
        "summit",
    ),
    (
        "TECH",
        CAT_TECH,
        "CHIP CURBS",
        "US SHUTS AI CHIP LOOPHOLE, SINGAPORE SEEKS ACCESS",
        "chip",
    ),
    (
        "MIGRATION",
        CAT_MIGRATION,
        "RWANDA HUB",
        "EU FIVE PLAN RWANDA HUB FOR REJECTED ASYLUM SEEKERS",
        "rwanda",
    ),
]

HERO_BODY = "IRAN FIRES DRONES AT US RADAR IN BAHRAIN, FOURTH TANKER HIT BY MINE IN HORMUZ"
STRIP_HEADLINE = "US BANKS: CHASE BUG FREEZES ZELLE"
STRIP_BODY = "CHASE SOFTWARE BUG SLOWS ONLINE BANKING AND ZELLE ACROSS THE US"

ICONS = {
    "bridge": icon_bridge,
    "summit": icon_summit,
    "chip": icon_chip,
    "rwanda": icon_rwanda,
}

PANEL_W = 124
PANEL_H = 62
GRID_X = (2, 130)
GRID_Y = (100, 164)


def draw_masthead(c):
    c.fill_rect(0, 0, W - 1, 30, CRIMSON)
    # Little globe, left of the title.
    c.circle(16, 15, 9, CREAM)
    c.ellipse(16, 15, 2, 9, CRIMSON)
    c.line(7, 15, 25, 15, CRIMSON, width=1)
    title = "ONE DAY ON EARTH"
    c.text_bold(title, (W - text_width(title, 2)) // 2 + 6, 4, 2, CREAM)
    date = "TUESDAY, 17 NOVEMBER 2026"
    c.text(date, (W - text_width(date, 1)) // 2, 22, 1, GOLD)
    c.fill_rect(0, 31, W - 1, 32, GOLD)


def draw_hero(c):
    px, py = 2, 34
    c.fill_rect(px, py, px + 251, py + 63, PANEL_BG)
    c.rect_outline(px, py, px + 251, py + 63, BORDER)
    # Category chip, top left.
    c.fill_rect(px + 3, py + 3, px + 3 + 71, py + 11, CAT_MIDEAST)
    c.text("MIDDLE EAST", px + 6, py + 4, 1, WHITE)
    # Big picture on the right.
    icon_gulf_big(c, px + 189, py + 2)
    # Headline + body on the left.
    c.text_bold("GULF ON FIRE", px + 3, py + 15, 2, INK)
    lines = wrap_text(HERO_BODY, 29)
    assert len(lines) <= 3, lines
    for i, line in enumerate(lines):
        c.text(line, px + 3, py + 32 + i * 8, 1, BODY)
    c.text("SRC: REUTERS, JUST SECURITY", px + 3, py + 56, 1, (100, 100, 108))


def draw_grid_panel(c, px, py, story):
    tag, color, headline, body, icon_key = story
    c.fill_rect(px, py, px + PANEL_W - 1, py + PANEL_H - 1, PANEL_BG)
    c.rect_outline(px, py, px + PANEL_W - 1, py + PANEL_H - 1, BORDER)
    # Coloured spine bar on the left.
    c.fill_rect(px + 1, py + 1, px + 4, py + PANEL_H - 2, color)
    # Category tag.
    c.text(tag, px + 8, py + 2, 1, color)
    # Icon (28x28) at left, headline beside it.
    ICONS[icon_key](c, px + 8, py + 12)
    c.text_bold(headline, px + 40, py + 20, 1, INK)
    # Body: 3 wrapped lines across the full panel width.
    lines = wrap_text(body, 19)
    assert len(lines) <= 3, (headline, lines)
    for i, line in enumerate(lines):
        c.text(line, px + 6, py + 40 + i * 7, 1, BODY)


def draw_strip(c):
    px, py = 2, 228
    c.fill_rect(px, py, px + 251, py + 26, PANEL_BG)
    c.rect_outline(px, py, px + 251, py + 26, BORDER)
    c.fill_rect(px + 1, py + 1, px + 4, py + 25, CAT_FINANCE)
    icon_bank(c, px + 7, py + 2)
    c.text_bold(STRIP_HEADLINE, px + 32, py + 2, 1, INK)
    lines = wrap_text(STRIP_BODY, 36)
    assert len(lines) <= 2, lines
    for i, line in enumerate(lines):
        c.text(line, px + 32, py + 11 + i * 8, 1, BODY)


def build_canvas():
    c = Canvas()
    c.fill_rect(0, 0, W - 1, H - 1, PAPER)
    draw_masthead(c)
    draw_hero(c)
    for i, story in enumerate(GRID_STORIES):
        px = GRID_X[i % 2]
        py = GRID_Y[i // 2]
        draw_grid_panel(c, px, py, story)
    draw_strip(c)
    return c


def main():
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "entry.png").write_bytes(encode_png(build_canvas()))


if __name__ == "__main__":
    main()
