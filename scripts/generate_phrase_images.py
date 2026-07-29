#!/usr/bin/env python3
"""Generate static visual mnemonic cards for jp_phrases.html.

Run from the repository root:
    python scripts/generate_phrase_images.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "phrases" / "main.json"
IMAGE_ROOT = ROOT / "phrases" / "images"
CARD_DIR = IMAGE_ROOT / "cards"
MANIFEST_PATH = IMAGE_ROOT / "manifest.json"
SIZE = 640

FONT_SERIF = Path(r"C:\Windows\Fonts\NotoSerifJP-VF.ttf")
FONT_SANS = Path(r"C:\Windows\Fonts\NotoSansJP-VF.ttf")
FONT_EMOJI = Path(r"C:\Windows\Fonts\seguiemj.ttf")

TYPE_CONFIG = {
    "四字熟語": {
        "background": IMAGE_ROOT / "backgrounds" / "yojijukugo.png",
        "accent": (167, 139, 250),
        "badge": (98, 75, 160),
        "fallback": "⛰️",
    },
    "ことわざ": {
        "background": IMAGE_ROOT / "backgrounds" / "kotowaza.png",
        "accent": (251, 146, 60),
        "badge": (174, 84, 28),
        "fallback": "🌾",
    },
    "慣用句": {
        "background": IMAGE_ROOT / "backgrounds" / "kanyouku.png",
        "accent": (52, 211, 153),
        "badge": (24, 120, 93),
        "fallback": "👐",
    },
}

# Literal-word cues make every illustration relevant without revealing the
# hidden reading or definition. More specific rules intentionally come first.
SYMBOL_RULES = [
    ("有言実行", "💬✅"),
    ("一石二鳥", "🪨🐦"),
    ("二兎", "🐇🐇"),
    ("以心伝心", "💗🤝"),
    ("一期一会", "🍵🤝"),
    ("温故知新", "📜💡"),
    ("自業自得", "⚖️🪞"),
    ("十人十色", "👥🌈"),
    ("臨機応変", "🧩🔄"),
    ("喜怒哀楽", "🎭"),
    ("試行錯誤", "🧪🧩"),
    ("前代未聞", "❗👂"),
    ("一刀両断", "⚔️"),
    ("大器晩成", "🌱🌳"),
    ("馬耳東風", "🐎🌬️"),
    ("付和雷同", "👥⚡"),
    ("七転八起", "🧗🌅"),
    ("七転び八起き", "🧗🌅"),
    ("危機一髪", "⚠️💨"),
    ("五里霧中", "🌫️🧭"),
    ("四苦八苦", "🔥😣"),
    ("竜頭蛇尾", "🐉🐍"),
    ("噂", "🗣️👂"),
    ("急がば回れ", "🛤️⏳"),
    ("覆水", "💧🏺"),
    ("石の上", "🪨🧘"),
    ("猿も木", "🐒🌳"),
    ("出る杭", "📌🔨"),
    ("論より証拠", "📄🔍"),
    ("良薬", "💊"),
    ("転ばぬ先の杖", "🦯⚠️"),
    ("百聞", "👂👁️"),
    ("笑う門", "😊🏠"),
    ("情け", "🤲💗"),
    ("君子の交わり", "🤝💧"),
    ("虎穴", "🐅🕳️"),
    ("塵も積もれば", "✨🏔️"),
    ("能ある鷹", "🦅"),
    ("袖振り合う", "👘🤝"),
    ("足を引っ張る", "👣🪢"),
    ("油を売る", "🛢️⏰"),
    ("頭が固い", "🧠🧱"),
    ("腹を割る", "💬🤝"),
    ("目から鱗", "👁️✨"),
    ("馬が合う", "🐎🤝"),
    ("口が滑る", "💬💨"),
    ("腰が低い", "🙇"),
    ("手を焼く", "✋🔥"),
    ("耳が痛い", "👂⚡"),
    ("棚に上げる", "📦⬆️"),
    ("水に流す", "💧🌊"),
    ("顔が広い", "🙂👥"),
    ("肩身が狭い", "😔↔️"),
    ("気が置けない", "☕🤝"),
    ("二の足", "👣⏸️"),
    ("根も葉もない", "🌿❌"),
    ("悪戦苦闘", "⚔️🔥"),
    ("一目瞭然", "👁️✨"),
    ("起死回生", "🌱🌅"),
    ("孤軍奮闘", "🛡️🔥"),
    ("明鏡止水", "🪞💧"),
    ("切磋琢磨", "💎✨"),
    ("因果応報", "⚖️🔄"),
    ("弱肉強食", "🦁🐾"),
    ("千載一遇", "🌠"),
    ("油断大敵", "⚠️👁️"),
    ("一喜一憂", "😊😟"),
    ("粉骨砕身", "💪🔥"),
    ("朝令暮改", "🌅🌙"),
    ("針小棒大", "🪡📏"),
    ("七転八倒", "💫😣"),
    ("一寸先は闇", "🕯️🌑"),
    ("井の中の蛙", "🐸🌊"),
    ("灯台下暗し", "🗼🔦"),
    ("棚からぼた餅", "🍡⬇️"),
    ("時は金", "⏰💰"),
    ("雨降って", "🌧️🌱"),
    ("後悔先に立たず", "↩️⏳"),
    ("鬼の居ぬ間", "👹🧺"),
    ("飛んで火に入る", "🦋🔥"),
    ("口は禍", "💬⚠️"),
    ("寝耳に水", "🛏️💧"),
    ("猫の手", "🐈✋"),
    ("突拍子", "❗💡"),
    ("首を長く", "🦒⏳"),
    ("高をくくる", "📏😏"),
    ("頭を抱える", "🤦"),
    ("尻馬に乗る", "🐎👥"),
    ("鼻が高い", "👃✨"),
    ("腹が黒い", "🖤🎭"),
    ("耳を傾ける", "👂💬"),
    ("口を酸っぱく", "💬🍋"),
    ("気が利く", "💡🤲"),
    ("白羽の矢", "🏹🪶"),
    ("目を細める", "😊👁️"),
    ("胸に手", "✋💗"),
    ("一気呵成", "🌊⚡"),
    ("虎視眈眈", "🐅👁️"),
    ("初志貫徹", "🎯🛤️"),
    ("臥薪嘗胆", "🪵🔥"),
    ("適材適所", "🧩📍"),
    ("画竜点睛", "🐉🖌️"),
    ("言行一致", "💬✅"),
    ("百花繚乱", "🌸🌼"),
    ("捲土重来", "🌪️🌅"),
    ("栄枯盛衰", "🌸🍂"),
    ("不撓不屈", "⛰️🔥"),
    ("侃侃諤諤", "💬⚡"),
    ("一蓮托生", "🪷🤝"),
    ("天衣無縫", "👘✨"),
    ("大胆不敵", "🦁🔥"),
    ("案ずるより", "🤔👶"),
    ("類は友", "🧲👥"),
    ("三人寄れば", "👥💡"),
    ("光陰矢", "🏹⏳"),
    ("蛙の子", "🐸🐸"),
    ("習うより慣れろ", "🛠️🔄"),
    ("言わぬが花", "🤫🌸"),
    ("聞くは一時", "❓📚"),
    ("亀の甲", "🐢📜"),
    ("立つ鳥", "🐦✨"),
    ("住めば都", "🏠🏯"),
    ("終わり良ければ", "🏁✨"),
    ("固唾を呑む", "😮⏳"),
    ("肩の荷", "🎒⬇️"),
    ("兜を脱ぐ", "⛑️🙇"),
    ("釘をさす", "🔨📌"),
    ("口火を切る", "🔥💬"),
    ("火に油", "🔥🛢️"),
    ("のどから手", "✋✨"),
    ("腑に落ちない", "🧩❓"),
    ("長い目", "👁️🌅"),
    ("音を上げる", "🔊🏳️"),
    ("一肌脱ぐ", "💪🤝"),
    ("太鼓判", "🥁✅"),
    ("頭角を現す", "🦌✨"),
]


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def fit_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, minimum: int) -> ImageFont.FreeTypeFont:
    for size in range(start, minimum - 1, -2):
        candidate = font(FONT_SERIF, size)
        if draw.textbbox((0, 0), text, font=candidate)[2] <= max_width:
            return candidate
    return font(FONT_SERIF, minimum)


def split_phrase(draw: ImageDraw.ImageDraw, phrase: str, max_width: int) -> tuple[list[str], ImageFont.FreeTypeFont]:
    single = fit_text(draw, phrase, max_width, 66, 30)
    if draw.textbbox((0, 0), phrase, font=single)[2] <= max_width and len(phrase) <= 10:
        return [phrase], single

    middle = max(1, len(phrase) // 2)
    candidates = range(max(1, middle - 3), min(len(phrase), middle + 4))
    best = min(candidates, key=lambda pos: abs(pos - middle))
    lines = [phrase[:best], phrase[best:]]
    longest = max(lines, key=len)
    return lines, fit_text(draw, longest, max_width, 48, 28)


def choose_symbol(phrase: str, fallback: str) -> str:
    for needle, symbol in SYMBOL_RULES:
        if needle in phrase:
            return symbol
    return fallback


def add_card_variation(image: Image.Image, index: int, accent: tuple[int, int, int]) -> Image.Image:
    rng = random.Random(index * 7919)
    if index % 2:
        image = ImageOps.mirror(image)
    image = ImageEnhance.Color(image).enhance(0.92 + rng.random() * 0.14)
    image = ImageEnhance.Brightness(image).enhance(0.92 + rng.random() * 0.09)

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx = rng.randint(150, 490)
    gy = rng.randint(170, 450)
    for radius in range(210, 20, -10):
        alpha = int(2.1 * (210 - radius))
        alpha = min(alpha, 18)
        gd.ellipse((gx - radius, gy - radius, gx + radius, gy + radius), fill=(*accent, alpha))
    return Image.alpha_composite(image.convert("RGBA"), glow)


def draw_centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    *,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
    embedded_color: bool = False,
) -> None:
    x, y = xy
    box = draw.textbbox((0, 0), text, font=selected_font, stroke_width=stroke_width)
    width = box[2] - box[0]
    draw.text(
        (x - width / 2, y),
        text,
        font=selected_font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
        embedded_color=embedded_color,
    )


def make_card(index: int, phrase: str, phrase_type: str, background: Image.Image) -> Image.Image:
    config = TYPE_CONFIG[phrase_type]
    image = add_card_variation(background.copy(), index, config["accent"])

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((52, 96, 588, 560), radius=34, fill=(7, 12, 20, 168), outline=(*config["accent"], 120), width=2)
    od.rounded_rectangle((225, 34, 415, 84), radius=25, fill=(*config["badge"], 235), outline=(235, 203, 120, 190), width=2)
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    badge_font = font(FONT_SANS, 23)
    draw_centered(draw, (320, 43), phrase_type, badge_font, (255, 248, 225, 255))

    symbol = choose_symbol(phrase, config["fallback"])
    emoji_font = font(FONT_EMOJI, 112 if len(symbol) <= 2 else 88)
    try:
        draw_centered(draw, (320, 150), symbol, emoji_font, (255, 255, 255, 255), embedded_color=True)
    except (OSError, ValueError):
        fallback_font = font(FONT_SANS, 84)
        draw_centered(draw, (320, 160), "◆", fallback_font, (*config["accent"], 255))

    divider_y = 330
    draw.line((150, divider_y, 490, divider_y), fill=(*config["accent"], 190), width=2)
    draw.ellipse((312, divider_y - 4, 320, divider_y + 4), fill=(232, 196, 102, 230))

    lines, phrase_font = split_phrase(draw, phrase, 490)
    line_height = phrase_font.size + 10
    block_height = line_height * len(lines)
    start_y = 368 + max(0, (128 - block_height) // 2)
    for offset, line in enumerate(lines):
        draw_centered(
            draw,
            (320, start_y + offset * line_height),
            line,
            phrase_font,
            (250, 246, 235, 255),
            stroke_width=2,
            stroke_fill=(5, 8, 13, 210),
        )

    index_font = font(FONT_SANS, 18)
    index_text = f"{index:03d}"
    draw.text((76, 525), index_text, font=index_font, fill=(255, 255, 255, 120))
    return image.convert("RGB")


def main() -> None:
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open(encoding="utf-8") as handle:
        records = json.load(handle)

    backgrounds = {}
    for phrase_type, config in TYPE_CONFIG.items():
        source = Image.open(config["background"]).convert("RGB")
        backgrounds[phrase_type] = ImageOps.fit(source, (SIZE, SIZE), method=Image.Resampling.LANCZOS)

    manifest = []
    for index, record in enumerate(records, start=1):
        phrase, _reading, phrase_type, _meaning, _examples = record
        filename = f"{index:03d}.webp"
        destination = CARD_DIR / filename
        card = make_card(index, phrase, phrase_type, backgrounds[phrase_type])
        card.save(destination, "WEBP", quality=84, method=6)
        manifest.append({"phrase": phrase, "image": f"phrases/images/cards/{filename}"})

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Generated {len(manifest)} static phrase images in {CARD_DIR}")


if __name__ == "__main__":
    main()
