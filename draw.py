#!/usr/bin/env python3
"""Draw the 24 November 2026 world-news image (1024x1024 PNG).

Design: cream broadsheet, navy + red. A small WORLD NEWS kicker, the date
as the huge serif masthead headline, a black "THE DAY IN UTC" timeline
strip, three large visual lead cards with drawn illustrations, then a dense
12-card grid (3x4) with the remaining verified stories. Every story comes
from the QA brief only; only 24 November 2026 news is shown.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (20, 33, 61)
RED = (179, 18, 46)
GRAY = (96, 96, 90)
DARK = (38, 38, 36)
GREEN = (28, 140, 80)
ORANGE = (228, 118, 28)
SKY = (178, 205, 225)
SEA = (38, 68, 110)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit in width."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_line(draw, text, fnt, width):
    """Truncate one line with an ellipsis so it fits in width."""
    if draw.textlength(text, font=fnt) <= width:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= width:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell


def spaced(text, n=1):
    return (" " * n).join(list(text.replace(" ", "   ")))


# ------------------------------------------------------------------ cards
LEADS = [
    {
        "label": "REINSTATED",
        "num": "1 · SANTA CLARA, USA — TECH",
        "head": "Huang back at Nvidia as shares add $1tn",
        "deck": ("Board restores Jensen Huang; Trump traded "
                 "$27–98M in Nvidia shares."),
        "src": "Reuters · CNN · WSJ",
        "art": "chart",
    },
    {
        "label": "CLAIMED",
        "num": "2 · OFF LIBYA — WAR",
        "head": "Ukraine drone hits Russian warship off Libya",
        "deck": ("Zelensky seeks four-party talks; refinery burns, "
                 "toll nears 700,000."),
        "src": "Reuters · AP",
        "art": "ship",
    },
    {
        "label": "ARRESTS",
        "num": "3 · SEATTLE, USA — IMMIGRATION",
        "head": "ICE arrests at Seattle airport",
        "deck": ("Father and daughter detained; a Princeton "
                 "neuroscientist held at D.C. airport."),
        "src": "AP · CNN",
        "art": "plane",
    },
]

TIMELINE = [
    "Nvidia shares surge",
    "Zelensky seeks talks",
    "ICE arrests, Seattle",
    "Megaspeed blacklisted",
    "Trump warns Iran",
]

# (category, [(headline, deck), ...]) — 12 cards, 39 stories with the leads
GRID = [
    ("WORLD", [
        ("COP31: what comes next",
         "Climate talks collapsed without a deal on 22 Nov; the focus now is what follows."),
        ("UN: agree AI rules in a year",
         "UN leader calls for the world to agree on AI regulation within one year."),
        ("Trump warns Iran",
         "“Very traumatic” outcome if a nuclear deal fails; a second carrier is weighed."),
    ]),
    ("WORLD", [
        ("US blacklists Megaspeed",
         "Singapore firm at the centre of the Nvidia spy case, plus six others, face export curbs."),
        ("Pentagon rebukes Canada",
         "Accused of falling short as a credible partner in defending North America."),
        ("China: death for spying",
         "Official surnamed Ma sentenced to death for spying for an unnamed country."),
    ]),
    ("WORLD", [
        ("Libya seeks UN probe",
         "Eastern region wants a probe into reports of Ukrainian troops in western Libya."),
        ("Mexico to try “El Chapo Isidro”",
         "Will prosecute the captured fugitive despite a US extradition request."),
        ("Georgia plans surrogacy ban",
         "Full ban planned amid trafficking concerns."),
    ]),
    ("ASIA", [
        ("India 3rd in Asia Power Index",
         "India retains third place in the regional power ranking."),
        ("SoftBank to invest $2B in Intel",
         "Japanese group plans a $2 billion investment in the chipmaker."),
        ("Bangladesh vaccinates 50M",
         "Month-long campaign against typhoid for 50 million children begins."),
    ]),
    ("ASIA", [
        ("Thai–Cambodia border on hold",
         "Fighting pauses following a truce."),
        ("Himalayan flood search",
         "Indian Army searches for scores missing; at least 4 dead, ~100 unaccounted."),
        ("Revanna jailed for life",
         "Former Indian lawmaker sentenced to life for rape."),
    ]),
    ("ASIA", [
        ("Banten fire: rescue goes on",
         "Rescue operations continue after the factory blaze that killed at least 24."),
        ("Australia: AI is a foreign-policy challenge",
         "Canberra to treat artificial intelligence as a major foreign-policy issue."),
        ("Russian jets enter KADIZ",
         "Russian aircraft entered South Korea’s air defence zone on Tuesday."),
    ]),
    ("WAR", [
        ("Refinery burning in Russia",
         "Novoshakhtinsk oil refinery ablaze after a Ukrainian drone attack."),
        ("Russian war toll nears 700,000",
         "Leaked government data puts the likely death toll near 700,000."),
    ]),
    ("TRADE", [
        ("Trump–Japan trade deal",
         "Deal announced as Tokyo’s Nikkei led an Asian rally."),
        ("Indonesia trade deal secured",
         "Trump secured a trade deal with Indonesia."),
        ("EU threatens $84B retaliation",
         "Brussels threatens $84 billion in tariff retaliation."),
    ]),
    ("U.S.", [
        ("Senate to vote on $9.4B cuts",
         "Vote due on Trump’s foreign-aid and media cuts."),
        ("Melat Kiros, 29, makes history",
         "Democratic socialist is the first Gen Z woman to enter Congress."),
        ("NJ women indicted in fake attack",
         "Two women charged over a faked anti-Trump slashing attack."),
    ]),
    ("U.S.", [
        ("FAA ends O’Hare ground stop",
         "Ground stop at Chicago O’Hare cancelled after staffing issues."),
        ("Trump’s Nvidia trades",
         "108+ trades in Nvidia shares since returning to the White House."),
    ]),
    ("SPORT", [
        ("Rockets 116–104 Clippers", "Rockets move to 13–5."),
        ("Bulls 122–108 Cavaliers", "Hawkins 19 pts; 63 points off the bench."),
        ("Trail Blazers 128–111 76ers", "Avdija 31 pts; ends Philadelphia’s five-game streak."),
        ("Pacers 125–120 Thunder", "Gilgeous-Alexander 38 pts on his return."),
    ]),
    ("SPORT", [
        ("Grizzlies 117–111 Hornets", "Ty Jerome 29 pts, 7 threes."),
        ("Timberwolves 142–116 Nets", "McDaniels 34 pts, 10 reb, 6 ast."),
        ("Suns 123–119 Pelicans (OT)", "Phoenix win in overtime."),
        ("India–New Zealand Test drawn", "Wellington Test ends in a draw."),
    ]),
]


def draw_chart(d, x, y, w, h):
    """Nvidia lead art: dark navy panel, green rising line, +$1tn."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 38, 60))
    for gy in range(4):
        yy = y + 14 + gy * (h - 28) // 3
        d.line([x + 8, yy, x + w - 8, yy], fill=(60, 90, 120), width=1)
    pts = []
    n = 9
    for i in range(n):
        px = x + 14 + i * (w - 28) // (n - 1)
        py = y + h - 16 - int((h - 44) * (i / (n - 1)) ** 1.7)
        pts.append((px, py))
    d.polygon(pts + [(pts[-1][0], y + h), (pts[0][0], y + h)],
              fill=(28, 140, 80))
    d.line(pts, fill=(90, 230, 150), width=4, joint="curve")
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(200, 255, 220))
    f = font(SERIF_B, 34)
    plus = "+$1tn"
    pw = d.textlength(plus, font=f)
    d.text((x + w - 14 - pw, y + 8), plus, font=f, fill=(120, 240, 170))
    f2 = font(SANS_B, 11)
    d.text((x + 14, y + 8), "NVIDIA · NASDAQ", font=f2,
           fill=(150, 190, 220))


def draw_ship(d, x, y, w, h):
    """Ukraine lead art: warship silhouette at sea, orange explosion."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 214, 228))
    d.ellipse([x + w - 52, y + 10, x + w - 14, y + 48], fill=(250, 220, 140))
    sea_y = y + int(h * 0.62)
    d.rectangle([x, sea_y, x + w, y + h], fill=SEA)
    d.line([x, sea_y, x + w, sea_y], fill=(255, 255, 255), width=2)
    # warship hull + superstructure + mast
    hull = [(x + 40, sea_y - 6), (x + w - 30, sea_y - 6),
            (x + w - 62, sea_y + 22), (x + 78, sea_y + 22)]
    d.polygon(hull, fill=(30, 34, 40))
    d.rectangle([x + 120, sea_y - 34, x + 190, sea_y - 6], fill=(30, 34, 40))
    d.rectangle([x + 196, sea_y - 26, x + 214, sea_y - 6], fill=(30, 34, 40))
    d.line([x + 150, sea_y - 34, x + 150, sea_y - 58], fill=(30, 34, 40),
           width=4)
    d.line([x + 150, sea_y - 58, x + 176, sea_y - 50], fill=(30, 34, 40),
           width=3)
    # explosion burst over the deck
    cx, cy = x + 232, sea_y - 44
    for r, col in ((34, (255, 170, 40)), (24, (255, 110, 20)),
                   (14, (255, 220, 90))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for dx, dy in ((-40, -18), (-30, 6), (34, -14), (40, 10), (8, -34)):
        d.ellipse([cx + dx - 9, cy + dy - 9, cx + dx + 9, cy + dy + 9],
                  fill=(120, 120, 120))
    # small drone
    d.ellipse([x + 46, y + 22, x + 54, y + 30], fill=(30, 34, 40))
    d.line([x + 38, y + 26, x + 62, y + 26], fill=(30, 34, 40), width=2)


def draw_plane(d, x, y, w, h):
    """ICE lead art: airport scene, plane on the runway, terminal."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 216, 232))
    d.ellipse([x + w - 56, y + 12, x + w - 16, y + 52], fill=(252, 240, 180))
    # terminal + tower
    d.rectangle([x + 14, y + 52, x + 120, y + 96], fill=(120, 128, 138))
    for wx in range(22, 112, 18):
        d.rectangle([x + wx, y + 62, x + wx + 10, y + 76],
                    fill=(220, 235, 245))
    d.rectangle([x + 132, y + 30, x + 142, y + 96], fill=(100, 108, 118))
    d.rectangle([x + 126, y + 18, x + 148, y + 32], fill=(90, 98, 108))
    # runway
    ry = y + 96
    d.rectangle([x, ry, x + w, y + h], fill=(70, 74, 80))
    for dx in range(10, w - 20, 34):
        d.rectangle([x + dx, ry + 12, x + dx + 18, ry + 16],
                    fill=(240, 240, 240))
    # plane silhouette
    px, py = x + 168, ry + 12
    d.ellipse([px, py - 12, px + 118, py + 8], fill=(245, 245, 245))
    d.polygon([(px + 96, py - 8), (px + 132, py - 2), (px + 96, py + 4)],
              fill=(245, 245, 245))
    d.polygon([(px + 40, py - 4), (px + 66, py - 26), (px + 82, py - 26),
               (px + 66, py - 4)], fill=(220, 220, 220))
    d.polygon([(px + 20, py - 2), (px + 34, py - 18), (px + 44, py - 18),
               (px + 38, py - 2)], fill=(220, 220, 220))
    d.polygon([(px + 6, py - 6), (px + 6, py + 2), (px + 22, py + 2),
               (px + 22, py - 6)], fill=(200, 200, 200))
    for wx in range(28, 96, 14):
        d.rectangle([px + wx, py - 8, px + wx + 7, py - 3], fill=INK)


def draw_lead(d, x, y, w, h, lead):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=INK, width=1)
    art_h = 132
    if lead["art"] == "chart":
        draw_chart(d, x, y, w, art_h)
    elif lead["art"] == "ship":
        draw_ship(d, x, y, w, art_h)
    else:
        draw_plane(d, x, y, w, art_h)
    tx = x + 10
    ty = y + art_h + 10
    # label chip + confirmed badge
    lab = font(SANS_B, 11)
    lw = d.textlength(lead["label"], font=lab) + 14
    d.rectangle([tx, ty, tx + lw, ty + 18], fill=RED)
    d.text((tx + 7, ty + 3), lead["label"], font=lab, fill=(255, 255, 255))
    cf = font(SANS_B, 10)
    cw = d.textlength("✓ CONFIRMED", font=cf)
    d.text((x + w - 10 - cw, ty + 3), "✓ CONFIRMED", font=cf, fill=GREEN)
    # number + location
    nf = font(SANS, 10)
    d.text((tx, ty + 24), lead["num"], font=nf, fill=GRAY)
    # headline
    hf = font(SERIF_B, 21)
    lines = wrap(d, lead["head"], hf, w - 20)[:2]
    hy = ty + 42
    for ln in lines:
        d.text((tx, hy), ln, font=hf, fill=INK)
        hy += 24
    # deck
    df = font(SERIF, 12)
    dlines = wrap(d, lead["deck"], df, w - 20)[:3]
    dy = hy + 4
    for ln in dlines:
        d.text((tx, dy), ln, font=df, fill=DARK)
        dy += 16
    # source
    sf = font(SANS, 10)
    d.text((tx, y + h - 20), lead["src"], font=sf, fill=GRAY)


def draw_grid_card(d, x, y, w, h, category, stories):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                outline=(180, 175, 160), width=1)
    d.line([x, y, x + w, y], fill=RED, width=3)
    lf = font(SANS_B, 11)
    d.text((x + 9, y + 7), category, font=lf, fill=RED)
    inner_w = w - 18
    n = len(stories)
    top = y + 26
    slot = (h - 30) // n
    hf = font(SANS_B, 12)
    df = font(SERIF, 10)
    for i, (head, deck) in enumerate(stories):
        sy = top + i * slot
        hl = fit_line(d, head, hf, inner_w)
        d.text((x + 9, sy), hl, font=hf, fill=INK)
        if n <= 3:
            dl = fit_line(d, deck, df, inner_w)
            d.text((x + 9, sy + 15), dl, font=df, fill=GRAY)
        else:
            dl = fit_line(d, deck, df, inner_w)
            d.text((x + 9, sy + 14), dl, font=df, fill=GRAY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # double border
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=3)
    d.rectangle([12, 12, W - 13, H - 13], outline=INK, width=1)
    # kicker
    kf = font(SANS_B, 15)
    kicker = spaced("WORLD NEWS", 1)
    kw = d.textlength(kicker, font=kf)
    d.text(((W - kw) / 2, 24), kicker, font=kf, fill=RED)
    # masthead: the date itself, auto-fit
    date = "TUESDAY 24 NOVEMBER 2026"
    size = 58
    while size > 30:
        mf = font(SERIF_B, size)
        if d.textlength(date, font=mf) <= 958:
            break
        size -= 2
    mf = font(SERIF_B, size)
    mw = d.textlength(date, font=mf)
    d.text(((W - mw) / 2, 44), date, font=mf, fill=INK)
    # red rule under masthead
    d.line([20, 112, W - 20, 112], fill=RED, width=3)
    # timeline strip
    d.rectangle([20, 122, W - 20, 172], fill=(18, 18, 18))
    tf = font(SANS_B, 12)
    d.text((32, 140), "THE DAY IN UTC", font=tf, fill=RED)
    itf = font(SANS, 11)
    tx = 166
    for i, ev in enumerate(TIMELINE):
        d.ellipse([tx, 146, tx + 7, 153], fill=RED)
        d.text((tx + 11, 140), ev, font=itf, fill=(255, 255, 255))
        tx += 11 + d.textlength(ev, font=itf) + 18
    # three lead cards
    lead_y, lead_h, lead_w, gap = 182, 290, 320, 12
    for i, lead in enumerate(LEADS):
        draw_lead(d, 20 + i * (lead_w + gap), lead_y, lead_w, lead_h, lead)
    # 12-card grid, 3 x 4
    gy, gh, gw = 484, 118, 320
    for i, (cat, stories) in enumerate(GRID):
        row, col = divmod(i, 3)
        draw_grid_card(d, 20 + col * (gw + gap), gy + row * (gh + 12),
                       gw, gh, cat, stories)
    # footer
    ff = font(SANS, 9)
    foot = ("ALL STORIES FROM TUESDAY 24 NOVEMBER 2026  ·  "
            "SOURCES: REUTERS, AP, CNN, WSJ, THE TIMES")
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 1004), foot, font=ff, fill=GRAY)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
