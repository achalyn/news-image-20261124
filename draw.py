#!/usr/bin/env python3
"""Draw the 24 Nov 2026 world-news image as a NEWSPAPER front page
(1024x1024 PNG) for make.fun.

One dominant main story (Huawei guilty), everything else clearly smaller.
All 39 stories come from qa-brief-2026-11-24-addendum.md (verified 24 Nov
2026). Structure lessons from top3-comparison-r3.md. Drawn scenes only --
no photographs.
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 12
CW = W - 2 * M  # 1000 content width

# ---- palette ----
PAPER = (250, 247, 238)
INK = (24, 24, 24)
MUTED = (90, 86, 78)
RULE = (24, 24, 24)
RED = (178, 34, 34)
REDB = (150, 22, 22)
CARD = (255, 255, 255)
CARDLINE = (200, 194, 182)
SEA = (198, 222, 235)
LAND = (232, 214, 178)

REG_COLORS = {
    "N. AMERICA": (43, 108, 176),
    "LATIN AMERICA": (49, 130, 206),
    "EAST ASIA": (221, 107, 32),
    "S. & SE ASIA": (214, 158, 46),
    "E. EUROPE": (47, 133, 90),
    "W. EUROPE": (56, 161, 105),
    "MIDDLE EAST": (197, 48, 48),
    "AFRICA": (128, 90, 213),
    "OCEANIA": (49, 151, 149),
}

# ---- fonts ----
FD = "/usr/share/fonts/truetype/dejavu"
FL = "/usr/share/fonts/truetype/liberation"
_FONTS = {}


def font(kind, size):
    key = (kind, size)
    if key not in _FONTS:
        if kind == "serif":
            path = f"{FD}/DejaVuSerif-Bold.ttf"
        elif kind == "bold":
            path = f"{FD}/DejaVuSans-Bold.ttf"
        elif kind == "italic":
            path = f"{FL}/LiberationSans-Italic.ttf"
        else:
            path = f"{FD}/DejaVuSans.ttf"
        _FONTS[key] = ImageFont.truetype(path, size)
    return _FONTS[key]


def wrap(text, f, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(d, text, f, max_w, max_lines, x, y, fill, lh=None, align="left"):
    """Draw text wrapped to max_lines; hard-fail if it does not fit."""
    lines = wrap(text, f, max_w)
    assert len(lines) <= max_lines, f"OVERFLOW ({len(lines)}>{max_lines}): {text!r}"
    if lh is None:
        lh = f.size + 2
    for i, line in enumerate(lines):
        lx = x
        if align == "center":
            lx = x + (max_w - f.getlength(line)) // 2
        d.text((lx, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


def one_line(d, text, f, max_w, x, y, fill):
    """Draw a single line; hard-fail if it is too wide."""
    assert f.getlength(text) <= max_w, f"TOO WIDE: {text!r}"
    d.text((x, y), text, font=f, fill=fill)


# ---- content (from the QA addendum; verified 24 Nov 2026 only) ----
NAMEPLATE = "THE 24 NOVEMBER TIMES"
DATELINE = ("TUESDAY 24 NOVEMBER 2026  \u00b7  39 STORIES, ALL FROM TUESDAY 24 NOV"
            "  \u00b7  9 REGIONS  \u00b7  18 FIELDS")

CHIPS = [("N. AMERICA", 8), ("LATIN AMERICA", 4), ("EAST ASIA", 6),
         ("S. & SE ASIA", 4), ("E. EUROPE", 6), ("W. EUROPE", 4),
         ("MIDDLE EAST", 5), ("AFRICA", 1), ("OCEANIA", 1)]

TIMELINE = [
    ("00:30", "Kannauj bus crash, 4 children killed"),
    ("01:00", "Hanoi gas blast, 6 dead"),
    ("05:30", "Sanofi announces $41bn Insmed deal"),
    ("07:52 KST", "Ulleung air-raid alert"),
    ("11:14", "Ariane 6 lifts off from Kourou"),
    ("15:00", "US confidence released: 103.3"),
    ("21:00", "Dow closes above 50,000"),
]

NUMBERS = [
    ("11", "INJURED IN RIYADH"),
    ("10/12", "HUAWEI COUNTS GUILTY"),
    ("50,000", "DOW CLOSE"),
    ("$41bn", "SANOFI BUYS INSMED"),
    ("5,258", "ENGLAND HEAT DEATHS"),
    ("13", "DEAD IN UAE BUS CRASH"),
]

# The ONE main story: Huawei guilty. Largest headline, biggest scene,
# longest deck, top position, full page width.
MAIN = {
    "banner": "GUILTY 10 OF 12 COUNTS",
    "label": "NEW YORK  \u00b7  COURTS",
    "headline": "HUAWEI GUILTY ON 10 OF 12 COUNTS",
    "deck": ("A Brooklyn jury convicted Huawei of bank fraud, wire fraud, "
             "sanctions violations and conspiracy to steal trade secrets "
             "after an 11-week trial, clearing it of racketeering and "
             "obstruction. Huawei will appeal; sentencing is 14 September "
             "2027."),
    "callout": "10/12",
    "callout_text": "COUNTS GUILTY",
    "badge": "CONFIRMED",
    "source": "Reuters \u00b7 WSJ \u00b7 CNN \u00b7 Bloomberg Law",
}

# Secondary stories: clearly smaller than the main story.
SECONDARY = [
    {
        "banner": "11 INJURED",
        "scene": "tower",
        "label": "SAUDI ARABIA  \u00b7  CONFLICT",
        "headline": "HOUTHI DRONE HITS RIYADH TOWER, 11 INJURED",
        "deck": ("Drone hits a tower in Riyadh's financial district \u2014 "
                 "witnesses say the PIF Tower \u2014 injuring 11 people, "
                 "the second strike on the building in under a week."),
        "callout": "11",
        "callout_text": "INJURED",
        "badge": "CONFIRMED",
        "source": "Bloomberg \u00b7 Reuters \u00b7 Saudi Civil Defence",
    },
    {
        "banner": "UNDER INVESTIGATION",
        "scene": "govt",
        "label": "CHINA  \u00b7  POLITICS",
        "headline": "CHINA PROBES SHANGHAI PARTY CHIEF CHEN JINING",
        "deck": ("Beijing put Shanghai party chief Chen Jining, 62, under "
                 "investigation \u2014 the fourth Politburo member probed "
                 "since 2025."),
        "callout": "4th",
        "callout_text": "POLITBURO MEMBER",
        "badge": "OFFICIAL",
        "source": "Xinhua \u00b7 Reuters \u00b7 WSJ",
    },
]

GRID = [
    {"band": "$41BN DEAL", "band_color": (27, 94, 93), "scene": "pill",
     "headline": "SANOFI BUYS INSMED FOR $41BN",
     "deck": "Sanofi to buy US biotech Insmed for $175 a share \u2014 $41bn.",
     "badge": "CONFIRMED", "source": "Sanofi \u00b7 WSJ"},
    {"band": "DOW 50,000", "band_color": (27, 94, 93), "scene": "chart",
     "headline": "DOW BACK ABOVE 50,000 AS NASDAQ SLIDES",
     "deck": "Dow rose 0.85% to 50,018.70 \u2014 back above 50,000.",
     "badge": "CONFIRMED", "source": "Zacks \u00b7 MarketWatch"},
    {"band": "TAIEX +8.99%", "band_color": (27, 94, 93), "scene": "chip",
     "headline": "TAIEX +8.99%, RECORD POINT GAIN",
     "deck": "Taiex closed up 3,310 points (+8.99%) at 40,122.35.",
     "badge": "CONFIRMED", "source": "Focus Taiwan \u00b7 CNA"},
    {"band": "2 DEAD \u00b7 40+ HURT", "band_color": (150, 22, 22),
     "scene": "blast",
     "headline": "ZAPORIZHZHIA RAID: 2 DEAD, 40+ HURT",
     "deck": "Dawn Russian strike destroyed a house; two dead, 40+ hurt.",
     "badge": "CONFIRMED", "source": "Reuters \u00b7 AP"},
    {"band": "36 SATELLITES", "band_color": (27, 94, 93), "scene": "rocket",
     "headline": "ARIANE 6 LOFTS 36 AMAZON SATELLITES",
     "deck": "Ariane 6's tenth flight lifted 36 Amazon satellites.",
     "badge": "CONFIRMED", "source": "Spaceflight Now"},
    {"band": "KURDISH OIL", "band_color": (27, 94, 93), "scene": "oil",
     "headline": "IRAQ ORDERS SEIZURE OF KURDISH OILFIELDS",
     "deck": "PM ordered the Oil Ministry to take over Kurdish oilfields.",
     "badge": "REPORTED", "source": "Reuters"},
    {"band": "CHINA PACT", "band_color": (27, 94, 93), "scene": "island",
     "headline": "SOLOMONS TO END CHINA SECURITY PACT",
     "deck": "Honiara told Beijing it will not renew the 2022 pact.",
     "badge": "REPORTED", "source": "Reuters \u00b7 SMH \u00b7 BBC"},
    {"band": "AFCON", "band_color": (27, 94, 93), "scene": "trophy",
     "headline": "CAS RESTORES SENEGAL'S AFCON TITLE",
     "deck": "CAS overturned CAF's 3-0 forfeit; Senegal champions again.",
     "badge": "CONFIRMED", "source": "AP \u00b7 Reuters"},
    {"band": "5,258 RECORD", "band_color": (150, 22, 22), "scene": "thermo",
     "headline": "ENGLAND: RECORD 5,258 HEAT DEATHS",
     "deck": "UKHSA: 5,258 heat deaths in England in summer 2026.",
     "badge": "OFFICIAL", "source": "UKHSA \u00b7 Reuters"},
    {"band": "CONFIDENCE 103.3", "band_color": (27, 94, 93), "scene": "gauge",
     "headline": "US CONFIDENCE JUMPS TO 103.3",
     "deck": "Index rose 11.4 points to 103.3, highest since Jan 2025.",
     "badge": "OFFICIAL", "source": "Conference Board"},
]

# ALSO items 14-39: (number, text, source letter)
# C = 2+ outlets, O = official, R = one outlet, CL = one side's claim
ALSO = [
    (14, "UAE bus crash: 13 dead, 14 hurt", "C"),
    (15, "Hanoi gas blast: 6 dead, 10+ hurt", "C"),
    (16, "Nepal quake M5.3, felt in 4 countries", "C"),
    (17, "Ulleung alert: Russian jets near island", "C"),
    (18, "Turkey helicopter crash: 5 soldiers dead", "C"),
    (19, "Colombia car bomb: 23 hurt", "R"),
    (20, "Cartagena siege: ~30 hostages, 10 freed", "C"),
    (21, "Kannauj bus crash: 4 children killed", "R"),
    (22, "Andhra Pradesh: 9 dead in 3 accidents", "R"),
    (23, "Russian drone enters Polish airspace", "R"),
    (24, "Odesa strikes: 2 killed, 3 hurt", "C"),
    (25, "Kyiv drone debris fire, 2 hurt", "R"),
    (26, "Kharkiv strikes: 1 killed, 14 hurt", "R"),
    (27, "Chernihiv strike: 1 killed", "O"),
    (28, "Dell: record $54.9bn quarter, stock -11.8%", "C"),
    (29, "Nvidia -5.9%; Micron -11%, AMD -9%", "C"),
    (30, "S&P 500 -0.50% to 7,201", "C"),
    (31, "Kospi tops 5,000 on chip rally", "C"),
    (32, "Trump held up to 370,000 Nvidia shares", "R"),
    (33, "Tu-160 bombers fly 10 hours over Sea of Japan", "CL"),
    (34, "Europe heat deaths: 50,000+ this summer", "R"),
    (35, "US: verdict 'a step towards accountability'", "O"),
    (36, "Saudi coalition vows firm response", "CL"),
    (37, "Baghdad cracks down on oil-smuggling ring", "R"),
    (38, "Seoul summons Russia's defence attach\u00e9", "R"),
    (39, "Drones hit police HQ in C\u00facuta", "R"),
]

# Map pins 1-13: (number, label, region) -- positions set in draw_map()
PINS = [
    (1, "New York", "N. AMERICA"),
    (2, "Riyadh", "MIDDLE EAST"),
    (3, "Shanghai", "EAST ASIA"),
    (4, "Paris", "W. EUROPE"),
    (5, "Taipei", "EAST ASIA"),
    (6, "Zaporizhzhia", "E. EUROPE"),
    (7, "Kourou", "LATIN AMERICA"),
    (8, "Baghdad", "MIDDLE EAST"),
    (9, "Honiara", "OCEANIA"),
    (10, "Dakar", "AFRICA"),
    (11, "London", "W. EUROPE"),
    (12, "Ras Al Khaimah", "MIDDLE EAST"),
    (13, "Hanoi", "S. & SE ASIA"),
]


# ---- badges ----
BADGE_COLORS = {"CONFIRMED": (27, 94, 93), "OFFICIAL": (43, 108, 176),
                "REPORTED": (120, 90, 20), "CLAIM": (150, 22, 22)}


def badge(d, x, y, text):
    f = font("bold", 9)
    w = f.getlength(text) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=6,
                        fill=BADGE_COLORS.get(text, (90, 86, 78)))
    d.text((x + 5, y + 2), text, font=f, fill=(255, 255, 255))
    return w


# ---- illustrated scenes (drawn, never photographs) ----
def scene_court_big(d, x0, y0, x1, y1):
    """Large courthouse scene for the main story."""
    d.rectangle([x0, y0, x1, y1], fill=(28, 42, 74))
    # sky stars
    for sx, sy in [(x0 + 18, y0 + 10), (x0 + 52, y0 + 6), (x1 - 24, y0 + 12),
                   (x1 - 60, y0 + 7), (x0 + 90, y0 + 14)]:
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
    # ground + steps
    d.rectangle([x0, y1 - 16, x1, y1], fill=(120, 110, 96))
    d.rectangle([x0, y1 - 22, x1, y1 - 16], fill=(150, 142, 128))
    # courthouse body
    bw = (x1 - x0) * 0.72
    bx = x0 + (x1 - x0 - bw) / 2
    by = y0 + 22
    d.rectangle([bx, by + 18, bx + bw, y1 - 22], fill=(238, 228, 200))
    # pediment
    d.polygon([(bx - 10, by + 20), (bx + bw + 10, by + 20),
               (bx + bw / 2, by)], fill=(238, 228, 200))
    d.ellipse([bx + bw / 2 - 9, by + 5, bx + bw / 2 + 9, by + 19],
              fill=(214, 158, 46))
    # columns
    for i in range(5):
        cx = bx + 14 + i * (bw - 28) / 4
        d.rectangle([cx - 6, by + 22, cx + 6, y1 - 24], fill=(255, 252, 240))
        d.rectangle([cx - 8, by + 20, cx + 8, by + 24], fill=(255, 252, 240))
        d.rectangle([cx - 8, y1 - 28, cx + 8, y1 - 24], fill=(255, 252, 240))
    # door
    d.rectangle([bx + bw / 2 - 14, y1 - 48, bx + bw / 2 + 14, y1 - 22],
                fill=(28, 42, 74))
    # scales of justice on the left
    sx = x0 + 34
    sy = y0 + y1 - y0 - 58
    d.line([sx, sy - 18, sx, sy + 18], fill=(214, 158, 46), width=3)
    d.line([sx - 16, sy - 18, sx + 16, sy - 18], fill=(214, 158, 46), width=3)
    d.ellipse([sx - 3, sy - 24, sx + 3, sy - 18], fill=(214, 158, 46))
    d.polygon([(sx - 18, sy - 6), (sx - 10, sy - 6), (sx - 14, sy + 4)],
              fill=(214, 158, 46))
    d.polygon([(sx + 10, sy - 6), (sx + 18, sy - 6), (sx + 14, sy + 4)],
              fill=(214, 158, 46))
    # flag on the right
    fx = x1 - 30
    d.line([fx, y0 + 12, fx, y0 + 52], fill=(255, 255, 255), width=2)
    d.polygon([(fx, y0 + 12), (fx + 26, y0 + 17), (fx, y0 + 22)],
              fill=(197, 48, 48))


def scene_tower(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(52, 32, 64))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(30, 26, 40))
    cx = (x0 + x1) // 2
    d.polygon([(cx - 30, y1 - 8), (cx - 22, y0 + 6), (cx + 22, y0 + 6),
               (cx + 30, y1 - 8)], fill=(214, 158, 46))
    for r in range(2):
        yy = y0 + 11 + r * 8
        for c in range(3):
            xx = cx - 16 + c * 12
            d.rectangle([xx, yy, xx + 7, yy + 5], fill=(255, 240, 180))
    d.ellipse([cx - 30, y0 + 1, cx + 6, y0 + 13], fill=(120, 116, 120))
    d.ellipse([cx - 16, y0, cx + 18, y0 + 10], fill=(150, 146, 150))
    d.ellipse([x1 - 26, y0 + 6, x1 - 18, y0 + 14], fill=(240, 240, 240))
    d.ellipse([x1 - 22, y0 + 10, x1 - 14, y0 + 18], fill=(240, 240, 240))


def scene_govt(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(150, 22, 22))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(120, 110, 96))
    bw = (x1 - x0) * 0.66
    bx = x0 + (x1 - x0 - bw) / 2
    d.rectangle([bx, y0 + 12, bx + bw, y1 - 8], fill=(238, 228, 200))
    d.polygon([(bx - 6, y0 + 13), (bx + bw + 6, y0 + 13), (bx + bw / 2, y0 + 3)],
              fill=(214, 158, 46))
    for i in range(4):
        cx = bx + 10 + i * (bw - 20) / 3
        d.rectangle([cx - 4, y0 + 16, cx + 4, y1 - 10], fill=(150, 22, 22))
    d.ellipse([x0 + 10, y0 + 3, x0 + 24, y0 + 17], fill=(214, 158, 46))
    d.polygon([(x0 + 17, y0 + 6), (x0 + 19, y0 + 10), (x0 + 23, y0 + 10),
               (x0 + 20, y0 + 13), (x0 + 21, y0 + 16), (x0 + 17, y0 + 14),
               (x0 + 13, y0 + 16), (x0 + 14, y0 + 13), (x0 + 11, y0 + 10),
               (x0 + 15, y0 + 10)], fill=(150, 22, 22))


def mini_scene(d, kind, x0, y0, x1, y1):
    """Small illustrated strip for a grid card."""
    if kind == "pill":
        d.rectangle([x0, y0, x1, y1], fill=(27, 94, 93))
        d.rounded_rectangle([x0 + 30, y0 + 6, x1 - 30, y0 + 20], radius=7,
                            fill=(255, 255, 255))
        d.rounded_rectangle([x0 + 30, y0 + 6, (x0 + x1) // 2, y0 + 20],
                            radius=7, fill=(214, 158, 46))
        d.text(((x0 + x1) // 2 - 5, y0 + 8), "$", font=font("bold", 11),
               fill=(255, 255, 255))
    elif kind == "chart":
        d.rectangle([x0, y0, x1, y1], fill=(24, 42, 60))
        pts = [(x0 + 10, y1 - 6), (x0 + 45, y1 - 12), (x0 + 80, y1 - 8),
               (x0 + 115, y1 - 16), (x0 + 150, y1 - 20), (x1 - 10, y1 - 22)]
        d.line(pts, fill=(72, 187, 120), width=3)
        d.ellipse([x1 - 16, y1 - 26, x1 - 8, y1 - 18], fill=(72, 187, 120))
    elif kind == "chip":
        d.rectangle([x0, y0, x1, y1], fill=(24, 42, 60))
        for i, h in enumerate([8, 16, 10, 20, 14, 22]):
            xx = x0 + 22 + i * 24
            d.rectangle([xx, y1 - 4 - h, xx + 14, y1 - 4],
                        fill=(214, 158, 46) if i % 2 else (72, 187, 120))
    elif kind == "blast":
        d.rectangle([x0, y0, x1, y1], fill=(40, 26, 26))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        d.ellipse([cx - 20, cy - 10, cx + 20, cy + 10], fill=(237, 137, 54))
        d.ellipse([cx - 11, cy - 6, cx + 11, cy + 6], fill=(246, 224, 94))
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=(255, 255, 255))
    elif kind == "rocket":
        d.rectangle([x0, y0, x1, y1], fill=(20, 28, 52))
        for sx, sy in [(x0 + 20, y0 + 4), (x0 + 60, y0 + 8), (x1 - 30, y0 + 6),
                       (x0 + 100, y0 + 3), (x1 - 60, y0 + 12)]:
            d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 255, 255))
        cx = (x0 + x1) // 2
        d.polygon([(cx, y0 + 3), (cx + 6, y0 + 14), (cx - 6, y0 + 14)],
                  fill=(255, 255, 255))
        d.rectangle([cx - 6, y0 + 14, cx + 6, y0 + 20], fill=(214, 158, 46))
        d.polygon([(cx, y0 + 20), (cx + 4, y0 + 25), (cx - 4, y0 + 25)],
                  fill=(237, 137, 54))
    elif kind == "oil":
        d.rectangle([x0, y0, x1, y1], fill=(30, 30, 34))
        bx = x0 + 70
        d.polygon([(bx, y0 + 4), (bx + 24, y0 + 4), (bx + 17, y1 - 6),
                   (bx + 7, y1 - 6)], fill=(214, 158, 46))
        d.line([bx + 12, y0 + 4, bx + 24, y1 - 14], fill=(214, 158, 46),
               width=2)
        d.ellipse([x1 - 40, y0 + 8, x1 - 28, y0 + 20], fill=(246, 224, 94))
    elif kind == "island":
        d.rectangle([x0, y0, x1, y1], fill=(66, 135, 190))
        d.ellipse([x0 + 40, y0 + 6, x1 - 40, y1 - 6], fill=(104, 211, 145))
        d.ellipse([x0 + 70, y0 + 9, x0 + 86, y0 + 17], fill=(34, 120, 60))
        d.rectangle([x0 + 120, y0 + 8, x0 + 122, y0 + 18], fill=(255, 255, 255))
        d.polygon([(x0 + 122, y0 + 8), (x0 + 136, y0 + 12), (x0 + 122, y0 + 16)],
                  fill=(214, 158, 46))
    elif kind == "trophy":
        d.rectangle([x0, y0, x1, y1], fill=(27, 94, 60))
        cx = (x0 + x1) // 2
        d.ellipse([cx - 13, y0 + 4, cx + 13, y0 + 20], fill=(214, 158, 46))
        d.rectangle([cx - 3, y0 + 18, cx + 3, y0 + 24], fill=(214, 158, 46))
        d.rectangle([cx - 10, y0 + 23, cx + 10, y0 + 26], fill=(214, 158, 46))
        d.ellipse([cx - 18, y0 + 6, cx - 10, y0 + 14],
                  outline=(214, 158, 46), width=2)
        d.ellipse([cx + 10, y0 + 6, cx + 18, y0 + 14],
                  outline=(214, 158, 46), width=2)
    elif kind == "thermo":
        d.rectangle([x0, y0, x1, y1], fill=(190, 80, 40))
        cx = (x0 + x1) // 2
        d.rounded_rectangle([cx - 5, y0 + 4, cx + 5, y0 + 20], radius=5,
                            fill=(255, 255, 255))
        d.rectangle([cx - 2, y0 + 9, cx + 2, y0 + 18], fill=(197, 48, 48))
        d.ellipse([cx - 8, y0 + 16, cx + 8, y0 + 26], fill=(197, 48, 48))
    elif kind == "gauge":
        d.rectangle([x0, y0, x1, y1], fill=(43, 108, 176))
        cx, cy = (x0 + x1) // 2, y1 - 3
        d.pieslice([cx - 22, cy - 22, cx + 22, cy + 22], 180, 360,
                   fill=(255, 255, 255))
        d.line([cx, cy, cx + 15, cy - 13], fill=(197, 48, 48), width=3)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(24, 24, 24))


# ---- section drawing ----
def section_line(d, y):
    d.line([M, y, W - M, y], fill=RULE, width=2)
    return y + 2


def draw_masthead(d, y):
    """Newspaper nameplate + double rule + dateline strip."""
    f = font("serif", 50)
    w = f.getlength(NAMEPLATE)
    d.text(((W - w) // 2, y), NAMEPLATE, font=f, fill=INK)
    y += 54
    # thin double rule under the nameplate
    d.line([M, y, W - M, y], fill=RULE, width=3)
    y += 5
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y += 6
    f2 = font("bold", 12)
    w2 = f2.getlength(DATELINE)
    d.text(((W - w2) // 2, y), DATELINE, font=f2, fill=INK)
    return y + 15


def draw_chips(d, y):
    y = section_line(d, y)
    f3 = font("bold", 11)
    x = M
    for name, count in CHIPS:
        label = f"{name} {count}"
        w = f3.getlength(label) + 14
        col = REG_COLORS[name]
        d.rounded_rectangle([x, y, x + w, y + 19], radius=9,
                            outline=col, width=2)
        d.text((x + 7, y + 4), label, font=f3, fill=col)
        x += w + 6
    return y + 20


def draw_timeline(d, y):
    y = section_line(d, y)
    f = font("bold", 11)
    d.text((M, y + 3), "THE DAY IN UTC", font=f, fill=INK)
    f2 = font("bold", 10)
    note = "ALL TIMES VERIFIED"
    d.text((W - M - f2.getlength(note), y + 4), note, font=f2, fill=MUTED)
    y += 18
    col_w = CW // 7
    ft = font("bold", 13)
    fe = font("regular", 10)
    for i, (t, ev) in enumerate(TIMELINE):
        x = M + i * col_w + 4
        d.text((x, y), t, font=ft, fill=RED)
        fit(d, ev, fe, col_w - 10, 2, x, y + 16, INK, lh=11)
        if i:
            d.line([M + i * col_w, y, M + i * col_w, y + 38], fill=CARDLINE)
    return y + 40


def draw_numbers(d, y):
    y = section_line(d, y)
    f = font("bold", 11)
    d.text((M, y + 3), "THE DAY IN NUMBERS", font=f, fill=INK)
    y += 18
    box_w = CW // 6
    fn = font("bold", 22)
    fl = font("regular", 9)
    for i, (num, label) in enumerate(NUMBERS):
        x = M + i * box_w
        d.rectangle([x + 2, y, x + box_w - 2, y + 34], outline=CARDLINE)
        nw = fn.getlength(num)
        d.text((x + (box_w - nw) // 2, y + 1), num, font=fn, fill=RED)
        lw = fl.getlength(label)
        d.text((x + (box_w - lw) // 2, y + 23), label, font=fl, fill=MUTED)
    return y + 38


def draw_main(d, y):
    """The ONE dominant story: full width, biggest headline, biggest scene."""
    y = section_line(d, y)
    card_h = 164
    d.rectangle([M, y, W - M, y + card_h], outline=CARDLINE)
    # big red banner
    d.rectangle([M, y, W - M, y + 22], fill=REDB)
    fb = font("bold", 14)
    bw = fb.getlength(MAIN["banner"])
    d.text((M + (CW - bw) // 2, y + 3), MAIN["banner"], font=fb,
           fill=(255, 255, 255))
    # big drawn scene on the left
    sx0, sy0 = M, y + 22
    sx1, sy1 = M + 420, y + card_h
    scene_court_big(d, sx0, sy0, sx1, sy1)
    d.line([sx1, sy0, sx1, sy1], fill=CARDLINE)
    # text on the right
    tx = sx1 + 12
    tw = W - M - tx
    ty = sy0 + 2
    fl = font("bold", 10)
    d.text((tx, ty), MAIN["label"], font=fl, fill=RED)
    ty += 12
    fh = font("serif", 28)
    fit(d, MAIN["headline"], fh, tw, 2, tx, ty, INK, lh=30)
    ty += 60
    fd = font("regular", 12)
    fit(d, MAIN["deck"], fd, tw, 3, tx, ty, INK, lh=13)
    ty += 39
    fc = font("bold", 18)
    d.text((tx, ty), MAIN["callout"], font=fc, fill=RED)
    cw = fc.getlength(MAIN["callout"])
    fct = font("bold", 9)
    d.text((tx + cw + 4, ty + 6), MAIN["callout_text"], font=fct, fill=INK)
    badge(d, tx + cw + 4 + fct.getlength(MAIN["callout_text"]) + 10,
          ty + 2, MAIN["badge"])
    ty += 16
    fs = font("regular", 9)
    d.text((tx, ty), MAIN["source"], font=fs, fill=MUTED)
    return y + card_h


def draw_secondary(d, y):
    """Two smaller stories, clearly subordinate to the main one."""
    y = section_line(d, y)
    gap = 8
    card_w = (CW - gap) // 2
    card_h = 136
    scenes = {"tower": scene_tower, "govt": scene_govt}
    for i, sec in enumerate(SECONDARY):
        x = M + i * (card_w + gap)
        d.rectangle([x, y, x + card_w, y + card_h], outline=CARDLINE)
        d.rectangle([x, y, x + card_w, y + 18], fill=REDB)
        fb = font("bold", 12)
        bw = fb.getlength(sec["banner"])
        d.text((x + (card_w - bw) // 2, y + 2), sec["banner"], font=fb,
               fill=(255, 255, 255))
        sy = y + 18
        scenes[sec["scene"]](d, x, sy, x + card_w, sy + 34)
        ty = sy + 34
        fl = font("bold", 10)
        d.text((x + 6, ty + 2), sec["label"], font=fl, fill=RED)
        ty += 12
        fh = font("bold", 16)
        ty = fit(d, sec["headline"], fh, card_w - 12, 2, x + 6, ty, INK,
                 lh=18)
        fd = font("regular", 10)
        ty = fit(d, sec["deck"], fd, card_w - 12, 2, x + 6, ty, INK, lh=12)
        fc = font("bold", 15)
        d.text((x + 6, ty), sec["callout"], font=fc, fill=RED)
        cw = fc.getlength(sec["callout"])
        fct = font("bold", 9)
        d.text((x + 8 + cw, ty + 4), sec["callout_text"], font=fct, fill=INK)
        badge(d, x + card_w - 86, ty + 1, sec["badge"])
        ty += 15
        fs = font("regular", 9)
        d.text((x + 6, ty), sec["source"], font=fs, fill=MUTED)
    return y + card_h


def draw_grid(d, y):
    y = section_line(d, y)
    f = font("bold", 11)
    d.text((M, y + 3), "THE DAY IN TEN", font=f, fill=INK)
    y += 20
    gap = 6
    card_w = (CW - 4 * gap) // 5
    card_h = 108
    for row in range(2):
        for col in range(5):
            g = GRID[row * 5 + col]
            x = M + col * (card_w + gap)
            yy = y + row * (card_h + gap)
            d.rectangle([x, yy, x + card_w, yy + card_h], outline=CARDLINE)
            d.rectangle([x, yy, x + card_w, yy + 16], fill=g["band_color"])
            fb = font("bold", 10)
            d.text((x + 5, yy + 2), g["band"], font=fb, fill=(255, 255, 255))
            mini_scene(d, g["scene"], x, yy + 16, x + card_w, yy + 42)
            ty = yy + 45
            fh = font("bold", 11)
            fit(d, g["headline"], fh, card_w - 10, 2, x + 5, ty, INK, lh=13)
            ty += 25
            fd = font("regular", 9)
            deck_lines = wrap(g["deck"], fd, card_w - 10)
            assert len(deck_lines) <= 2, f"GRID DECK OVERFLOW: {g['deck']!r}"
            fit(d, g["deck"], fd, card_w - 10, 2, x + 5, ty, INK, lh=11)
            ty += len(deck_lines) * 11 + 1
            bw3 = badge(d, x + 5, ty, g["badge"])
            fs = font("regular", 9)
            sw = fs.getlength(g["source"])
            assert bw3 + 6 + sw <= card_w - 10, \
                f"SOURCE TOO WIDE: {g['source']!r}"
            d.text((x + card_w - 5 - sw, ty + 1), g["source"], font=fs,
                   fill=MUTED)
    return y + 2 * card_h + gap


def draw_also_map(d, y):
    y = section_line(d, y)
    f = font("bold", 11)
    d.text((M, y + 3), "ALSO TODAY \u2014 STORIES 14\u201339", font=f, fill=INK)
    f2 = font("bold", 9)
    legend = "C = 2+ OUTLETS \u00b7 O = OFFICIAL \u00b7 R = ONE OUTLET \u00b7 CL = ONE SIDE'S CLAIM"
    d.text((W - M - f2.getlength(legend), y + 4), legend, font=f2, fill=MUTED)
    y += 18
    also_w = 660
    map_x = M + also_w + 10
    map_w = W - M - map_x
    col_w = also_w // 2
    fa = font("regular", 10)
    for idx, (num, text, letter) in enumerate(ALSO):
        col = idx // 13
        row = idx % 13
        x = M + col * col_w
        yy = y + row * 11
        item = f"{num}. {text} \u2014 {letter}"
        one_line(d, item, fa, col_w - 8, x, yy, INK)
    map_h = 13 * 11 + 6
    draw_map(d, map_x, y, map_x + map_w, y + map_h)
    return y + map_h + 3


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=CARDLINE)
    f = font("bold", 9)
    d.text((x0 + 4, y0 + 2), "WHERE IT HAPPENED \u2014 PINS 1\u201313", font=f,
           fill=INK)
    my = y0 + 16
    mh = y1 - my - 26
    mw = x1 - x0
    # simplified continents (abstract blobs, drawn not photographed)
    d.polygon([(x0 + mw * 0.06, my + mh * 0.18), (x0 + mw * 0.20, my + mh * 0.10),
               (x0 + mw * 0.28, my + mh * 0.22), (x0 + mw * 0.24, my + mh * 0.42),
               (x0 + mw * 0.14, my + mh * 0.48), (x0 + mw * 0.06, my + mh * 0.34)],
              fill=LAND)
    d.polygon([(x0 + mw * 0.16, my + mh * 0.55), (x0 + mw * 0.26, my + mh * 0.52),
               (x0 + mw * 0.30, my + mh * 0.72), (x0 + mw * 0.22, my + mh * 0.92),
               (x0 + mw * 0.14, my + mh * 0.78)], fill=LAND)
    d.polygon([(x0 + mw * 0.44, my + mh * 0.12), (x0 + mw * 0.58, my + mh * 0.06),
               (x0 + mw * 0.62, my + mh * 0.24), (x0 + mw * 0.52, my + mh * 0.34),
               (x0 + mw * 0.44, my + mh * 0.26)], fill=LAND)
    d.polygon([(x0 + mw * 0.50, my + mh * 0.38), (x0 + mw * 0.62, my + mh * 0.36),
               (x0 + mw * 0.66, my + mh * 0.62), (x0 + mw * 0.58, my + mh * 0.86),
               (x0 + mw * 0.48, my + mh * 0.66)], fill=LAND)
    d.polygon([(x0 + mw * 0.64, my + mh * 0.10), (x0 + mw * 0.94, my + mh * 0.06),
               (x0 + mw * 0.96, my + mh * 0.34), (x0 + mw * 0.82, my + mh * 0.52),
               (x0 + mw * 0.68, my + mh * 0.40)], fill=LAND)
    d.polygon([(x0 + mw * 0.86, my + mh * 0.72), (x0 + mw * 0.96, my + mh * 0.70),
               (x0 + mw * 0.94, my + mh * 0.86), (x0 + mw * 0.84, my + mh * 0.88)],
              fill=LAND)
    # pin positions (fractions of map area, spread so no two overlap)
    pos = {1: (0.13, 0.24), 2: (0.58, 0.46), 3: (0.84, 0.22),
           4: (0.52, 0.16), 5: (0.90, 0.34), 6: (0.60, 0.22),
           7: (0.24, 0.62), 8: (0.60, 0.32), 9: (0.92, 0.76),
           10: (0.47, 0.52), 11: (0.46, 0.10), 12: (0.66, 0.40),
           13: (0.83, 0.40)}
    fp = font("bold", 8)
    for num, _label, region in PINS:
        fx, fy = pos[num]
        px, py = x0 + fx * mw, my + fy * mh
        col = REG_COLORS[region]
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col,
                  outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((px - fp.getlength(s) / 2, py - 5), s, font=fp,
               fill=(255, 255, 255))
    # region color legend (two rows at the bottom of the map)
    fl = font("bold", 8)
    for row_i, names in enumerate([
            ["N. AMERICA", "LATIN AMERICA", "E. EUROPE", "W. EUROPE"],
            ["MIDDLE EAST", "EAST ASIA", "S. & SE ASIA", "AFRICA",
             "OCEANIA"]]):
        lx = x0 + 4
        ly = y1 - 24 + row_i * 11
        for name in names:
            col = REG_COLORS[name]
            d.rectangle([lx, ly, lx + 7, ly + 7], fill=col)
            lx += 9
            w = fl.getlength(name)
            d.text((lx, ly), name, font=fl, fill=MUTED)
            lx += w + 7


def draw_footer(d, y):
    y = section_line(d, y)
    f = font("bold", 10)
    fd = font("regular", 9)
    d.text((M, y + 3), "DATE CHECK", font=f, fill=RED)
    y += 14
    lines = [
        ("Left off as earlier news: ",
         "Merkury sinking (22 Nov) \u00b7 ICE arrests (21 Nov) \u00b7 Huang reinstatement (23 Nov) \u00b7 first PIF strike (19 Nov) \u00b7 COP31 ended (22 Nov)"),
        ("Not yet: ",
         "Cartagena rescue (25 Nov) \u00b7 Solomons\u2013Australia treaty (25 Nov) \u00b7 Shanghai loyalty pledge (25 Nov)"),
        ("HOW THIS PAGE WAS CHECKED: ",
         "every story matched to reports dated 24 Nov 2026; disputed accounts carry CLAIM; tolls cross-checked."),
    ]
    for head, body in lines:
        hw = f.getlength(head)
        d.text((M, y), head, font=f, fill=INK)
        wrapped = wrap(body, fd, CW - hw)
        assert len(wrapped) <= 1, f"FOOTER OVERFLOW: {body!r}"
        d.text((M + hw, y + 1), wrapped[0], font=fd, fill=INK)
        y += 11
    return y


def draw_bottom(d, y):
    fi = font("italic", 10)
    line = "illustrations are drawn, not photographs \u00b7 every story names its sources"
    w = fi.getlength(line)
    d.text(((W - w) // 2, y), line, font=fi, fill=MUTED)
    return y + 13


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8
    y = draw_masthead(d, y)
    y += 1
    y = draw_chips(d, y)
    y += 1
    y = draw_timeline(d, y)
    y += 1
    y = draw_numbers(d, y)
    y += 1
    y = draw_main(d, y)
    y += 1
    y = draw_secondary(d, y)
    y += 1
    y = draw_grid(d, y)
    y += 1
    y = draw_also_map(d, y)
    y += 1
    y = draw_footer(d, y)
    y += 1
    y = draw_bottom(d, y)
    assert y <= H, f"IMAGE TOO TALL: {y} > {H}"
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True, compress_level=9)
    data = open(out, "rb").read()
    print(f"entry.png: {len(data)} bytes, sha256 "
          f"{hashlib.sha256(data).hexdigest()}")
    print(f"final y: {y} of {H}")


if __name__ == "__main__":
    main()
