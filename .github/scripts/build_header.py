"""Generate a seamless original AI-network animation for the profile README."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUTPUT = Path("assets/neural-pulse.gif")
W, H, SCALE, COUNT = 400, 210, 2, 20
CX, CY = W // 2, H // 2
TEAL = (47, 232, 206)
PURPLE = (159, 111, 250)
NODES = [
    (CX, 31), (CX + 93, 66), (CX + 93, 148),
    (CX, 182), (CX - 93, 148), (CX - 93, 66),
    (CX, CY),
]
EDGES = [(i, (i + 1) % 6) for i in range(6)]
EDGES += [(i, 6) for i in range(6)] + [(0, 3), (1, 4), (2, 5)]


def mix(a, b, strength):
    return tuple(round(p * (1 - strength) + q * strength) for p, q in zip(a, b))


def render(time):
    image = Image.new("RGB", (W * SCALE, H * SCALE))
    px = image.load()
    # Subtle charcoal/navy vignette; readable with either GitHub color theme.
    for y in range(H * SCALE):
        for x in range(W * SCALE):
            dx = (x / SCALE - CX) / CX
            dy = (y / SCALE - CY) / CY
            light = max(0, 1 - 0.65 * (dx * dx + dy * dy))
            px[x, y] = (round(8 + 5 * light), round(13 + 8 * light), round(22 + 12 * light))

    lines = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(lines, "RGBA")
    for y in range(12, H, 25):
        for x in range(12, W, 25):
            draw.ellipse((x * SCALE, y * SCALE, (x + .55) * SCALE, (y + .55) * SCALE),
                         fill=(91, 127, 158, 42))
    for i, j in EDGES:
        a, b = NODES[i], NODES[j]
        draw.line((a[0] * SCALE, a[1] * SCALE, b[0] * SCALE, b[1] * SCALE),
                  fill=(91, 126, 148, 86), width=2 * SCALE)

    halos = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow = ImageDraw.Draw(halos, "RGBA")
    colors = []
    for i, (x, y) in enumerate(NODES):
        distance = min((time - i / 6) % 1, (i / 6 - time) % 1) if i < 6 else .3
        intensity = math.exp(-((distance / .11) ** 2)) if i < 6 else .45
        tint = TEAL if i % 2 == 0 else PURPLE
        color = mix((71, 111, 131), tint, .46 + .54 * intensity)
        colors.append((color, intensity))
        for radius, opacity in [(20, 16 + 100 * intensity), (13, 22 + 115 * intensity),
                                (8, 40 + 130 * intensity)]:
            rr, xx, yy = radius * SCALE, x * SCALE, y * SCALE
            glow.ellipse((xx - rr, yy - rr, xx + rr, yy + rr),
                         fill=(*color, round(opacity)))

    halos = halos.filter(ImageFilter.GaussianBlur(8 * SCALE))
    composed = Image.alpha_composite(image.convert("RGBA"), halos)
    composed = Image.alpha_composite(composed, lines)
    pen = ImageDraw.Draw(composed, "RGBA")
    for (x, y), (color, intensity) in zip(NODES, colors):
        radius = 5.3 if (x, y) == (CX, CY) else 4.2 + 1.5 * intensity
        px, py, r = x * SCALE, y * SCALE, radius * SCALE
        pen.ellipse((px - r, py - r, px + r, py + r), fill=(*color, 255))
        rr = 1.2 * SCALE
        pen.ellipse((px - rr, py - rr, px + rr, py + rr),
                    fill=(237, 255, 252, round(95 + 95 * intensity)))
    return composed.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [render(i / COUNT).quantize(colors=96, method=Image.Quantize.MEDIANCUT)
              for i in range(COUNT)]
    for frame in frames:
        frame.info.clear()
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:],
                   duration=90, loop=0, optimize=True, disposal=2)
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes, {COUNT} frames)")


if __name__ == "__main__":
    main()
