"""
Generate lightweight demo product images for local development.

The original demo product images (frontend/public/assets) are ~135 MB and are
excluded from git to keep the repository source-only. Running this script creates
simple category-colored placeholder images so the frontend renders correctly.
"""
import os
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise ImportError("请先安装 Pillow: pip install Pillow")

ROOT = Path(__file__).parent.parent
PRODUCTS_PATH = ROOT / "backend" / "app" / "knowledge_base" / "products.json"
ASSETS_DIR = ROOT / "frontend" / "public" / "assets"

CATEGORY_COLORS = {
    "手机数码": (102, 126, 234),
    "电脑办公": (118, 75, 162),
    "家用电器": (240, 147, 251),
    "摄影摄像": (79, 172, 254),
    "智能穿戴": (0, 242, 254),
    "影音娱乐": (245, 87, 108),
    "游戏设备": (255, 159, 67),
    "默认": (149, 165, 166),
}


def get_font(size: int):
    # Try common Chinese fonts on Windows; fall back to default
    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def generate_image(product: dict, size=(400, 300)) -> Image.Image:
    category = product.get("category", "默认")
    color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["默认"])
    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)

    # Semi-transparent overlay (simulated by darker rectangle)
    draw.rectangle([0, size[1] * 2 // 3, size[0], size[1]], fill=(40, 40, 40, 180))

    name_font = get_font(24)
    price_font = get_font(20)
    id_font = get_font(16)

    name = product.get("name", "Demo Product")
    price = f"¥{product.get('price', 0):.2f}"
    pid = product.get("id", "")

    # Wrap long names roughly
    draw.text((20, 20), category, font=id_font, fill=(255, 255, 255))
    draw.text((20, size[1] * 2 // 3 + 20), name, font=name_font, fill=(255, 255, 255))
    draw.text((20, size[1] * 2 // 3 + 60), price, font=price_font, fill=(255, 200, 100))
    draw.text((size[0] - 120, size[1] - 40), pid, font=id_font, fill=(200, 200, 200))

    return img


def main():
    if not PRODUCTS_PATH.exists():
        raise FileNotFoundError(f"找不到商品数据: {PRODUCTS_PATH}")

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    products = json.loads(PRODUCTS_PATH.read_text(encoding="utf-8"))

    generated = 0
    for p in products:
        image_url = p.get("image_url", "")
        if not image_url:
            continue
        filename = Path(image_url).name
        out_path = ASSETS_DIR / filename
        img = generate_image(p)
        img.save(out_path, "JPEG", quality=85)
        generated += 1
        print(f"生成 {out_path}")

    print(f"\n共生成 {generated} 张演示图片到 {ASSETS_DIR}")


if __name__ == "__main__":
    main()
