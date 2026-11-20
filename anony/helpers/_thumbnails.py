# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# Custom ZeboraX music-player artwork.

import os
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from anony import config
from anony.helpers import Track


class Thumbnail:
    def __init__(self):
        self.size = (1280, 720)
        self.session: aiohttp.ClientSession | None = None
        self.title_font = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 36)
        self.artist_font = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 29)
        self.small_font = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 22)
        self.brand_font = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 25)

    async def start(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with self.session.get(url) as resp:
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(await resp.read())
        return output_path

    def _fit_text(self, draw, text, font, max_width):
        text = str(text or "Unknown")
        while text and draw.textbbox((0, 0), text + "…", font=font)[2] > max_width:
            text = text[:-1]
        return text + ("…" if len(text) < len(str(text or "")) else "")

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            os.makedirs("cache", exist_ok=True)
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            temp = f"cache/temp_{song.id}.jpg"
            await self.save_thumb(temp, song.thumbnail)
            source = Image.open(temp).convert("RGB")
            bg = ImageOps.fit(source, self.size, method=Image.Resampling.LANCZOS)
            bg = bg.filter(ImageFilter.GaussianBlur(34))
            bg = ImageEnhance.Brightness(bg).enhance(0.28).convert("RGBA")

            # Deep translucent overlay keeps the player card readable.
            shade = Image.new("RGBA", self.size, (2, 13, 18, 125))
            bg = Image.alpha_composite(bg, shade)
            draw = ImageDraw.Draw(bg)

            # Main glass-like panel and artwork.
            draw.rounded_rectangle((42, 38, 1238, 682), radius=38,
                                   fill=(4, 24, 28, 218), outline=(36, 210, 143, 150), width=3)
            art = ImageOps.fit(source, (470, 470), method=Image.Resampling.LANCZOS)
            art = art.convert("RGBA")
            mask = Image.new("L", art.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 469, 469), radius=28, fill=255)
            bg.paste(art, (82, 125), mask)

            # Brand and live-state indicator.
            draw.text((610, 92), "ZEBORAX  X  MUSIC", font=self.brand_font,
                      fill=(75, 245, 176, 255))
            draw.ellipse((1112, 100, 1130, 118), fill=(63, 242, 151, 255))
            draw.text((1142, 94), "LIVE", font=self.small_font, fill=(225, 255, 241, 255))

            title = str(song.title or "Unknown Track")
            artist = str(getattr(song, "channel_name", None) or "YouTube")
            while title and draw.textlength(title, font=self.title_font) > 555:
                title = title[:-2].rstrip() + "…"
            while artist and draw.textlength(artist, font=self.artist_font) > 555:
                artist = artist[:-2].rstrip() + "…"
            draw.text((610, 220), "NOW PLAYING", font=self.small_font,
                      fill=(120, 230, 190, 255))
            draw.text((606, 275), title, font=self.title_font,
                      fill=(255, 255, 255, 255))
            draw.text((610, 350), artist, font=self.artist_font,
                      fill=(190, 215, 211, 255))

            # Decorative equalizer bars.
            heights = [34, 62, 46, 88, 56, 104, 42, 72, 50, 92, 38, 66, 48, 82]
            x = 612
            for h in heights:
                draw.rounded_rectangle((x, 455 - h // 2, x + 12, 455 + h // 2),
                                       radius=6, fill=(43, 220, 151, 230))
                x += 25

            # Timeline and duration.
            draw.rounded_rectangle((610, 555, 1170, 565), radius=5, fill=(83, 115, 110, 220))
            draw.rounded_rectangle((610, 555, 635, 565), radius=5, fill=(49, 239, 158, 255))
            draw.text((610, 585), "00:01", font=self.small_font, fill=(220, 238, 232, 255))
            draw.text((1080, 585), str(song.duration or ""), font=self.small_font,
                      fill=(220, 238, 232, 255))
            draw.text((82, 625), "♪  MUSIC FOR YOUR MOMENT", font=self.small_font,
                      fill=(160, 208, 193, 255))

            bg.convert("RGB").save(output, quality=94)
            try:
                os.remove(temp)
            except OSError:
                pass
            return output
        except Exception:
            return config.DEFAULT_THUMB
