import io
import os
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_og_png_bytes(
    title: str = "Oyun Hata Kodları ve FPS Çözümleri",
    game_name: str = "OyunÇöz Teknik Rehber",
    error_code: str = "ADIM ADIM ÇÖZÜM",
    subtitle: str = "Windows 10 / 11 Oyun Çökme (Crash), Anti-Cheat ve Performans Rehberi",
) -> bytes:
    width, height = 1200, 630
    img = Image.new("RGB", (width, height), (20, 25, 35))
    draw = ImageDraw.Draw(img)

    # Subtle background gradient bands & grid lines
    for y in range(0, height, 6):
        ratio = y / float(height)
        r = int(20 + 8 * (1 - ratio))
        g = int(25 + 14 * (1 - ratio))
        b = int(35 + 20 * (1 - ratio))
        draw.rectangle([0, y, width, y + 6], fill=(r, g, b))

    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(30, 39, 53), width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(30, 39, 53), width=1)

    # Top and left accent bars (#5e9c88 / #88c0a8)
    draw.rectangle([0, 0, width, 10], fill=(94, 156, 136))
    draw.rectangle([0, 0, 12, height], fill=(136, 192, 168))

    # Card frame
    draw.rounded_rectangle([54, 48, 1146, 582], radius=28, fill=(26, 34, 48), outline=(72, 112, 102), width=2)

    font_brand = _get_font(34, bold=True)
    font_pill = _get_font(22, bold=True)
    font_title = _get_font(46, bold=True)
    font_sub = _get_font(25, bold=False)
    font_footer = _get_font(21, bold=True)

    # Brand header badge
    draw.rounded_rectangle([92, 86, 164, 158], radius=18, fill=(32, 46, 62), outline=(136, 192, 168), width=2)
    draw.text((108, 102), "OÇ", font=font_brand, fill=(136, 192, 168))
    draw.text((182, 92), "OyunÇöz", font=font_brand, fill=(235, 242, 250))
    draw.text((182, 132), "oyuncoz.com • Oyun Hata Kodları ve FPS Çözümleri", font=_get_font(20, False), fill=(154, 172, 194))

    # Game & Error Code pills
    clean_game = (game_name or "OyunÇöz").strip()[:34]
    clean_code = (error_code or "TEKNİK REHBER").strip()[:32]
    draw.rounded_rectangle([92, 194, 92 + max(180, len(clean_game) * 15 + 44), 244], radius=12, fill=(94, 156, 136))
    draw.text((112, 206), clean_game.upper(), font=font_pill, fill=(255, 255, 255))

    code_x = 92 + max(180, len(clean_game) * 15 + 44) + 18
    draw.rounded_rectangle([code_x, 194, min(1100, code_x + max(170, len(clean_code) * 14 + 44)), 244], radius=12, fill=(38, 49, 68), outline=(217, 195, 130), width=2)
    draw.text((code_x + 20, 206), clean_code, font=font_pill, fill=(217, 195, 130))

    # Word-wrap title (up to 3 lines)
    words = (title or "Oyun Hata Kodları ve FPS Çözümleri").split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) <= 38:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
        if len(lines) == 3:
            break
    if cur and len(lines) < 3:
        lines.append(cur)

    y_cursor = 276
    for line in lines[:3]:
        draw.text((92, y_cursor), line, font=font_title, fill=(240, 245, 252))
        y_cursor += 58

    # Subtitle
    clean_sub = (subtitle or "")[:88]
    draw.text((92, max(452, y_cursor + 12)), clean_sub, font=font_sub, fill=(168, 186, 208))

    # Bottom bar inside card
    draw.line([(92, 516), (1108, 516)], fill=(48, 62, 82), width=2)
    draw.text((92, 532), "Adım Adım Çözüm Rehberi • Sistem Güvenliği Notları • Topluluk & Editör Kontrolü", font=font_footer, fill=(136, 192, 168))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
