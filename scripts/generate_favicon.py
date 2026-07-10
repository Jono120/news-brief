"""Generate favicon PNG/ICO assets from the Brief APAC brand colours."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCENT = (11, 91, 73, 255)
INK = (255, 255, 255, 255)

TARGETS = [
    ROOT / "design" / "favicon.png",
    ROOT / "design" / "favicon.ico",
    ROOT / "web" / "public" / "public" / "favicon.ico",
    ROOT / "web" / "review" / "public" / "favicon.ico",
    ROOT / "brief" / "static" / "public" / "favicon.ico",
]


def _rounded_mask(size: int, radius: int) -> list[list[bool]]:
    mask = [[False] * size for _ in range(size)]
    for y in range(size):
        for x in range(size):
            inside = True
            corners = (
                (x, y, radius, radius),
                (x, y, size - radius, radius),
                (x, y, radius, size - radius),
                (x, y, size - radius, size - radius),
            )
            for px, py, cx, cy in corners:
                if (px < radius and py < radius) or (px >= size - radius and py < radius) or (
                    px < radius and py >= size - radius
                ) or (px >= size - radius and py >= size - radius):
                    if (px - cx) ** 2 + (py - cy) ** 2 > radius**2:
                        inside = False
            mask[y][x] = inside
    return mask


def _draw_b(size: int) -> list[tuple[int, int, int]]:
    """Return RGB pixels for a simple B mark on accent background."""
    mask = _rounded_mask(size, max(2, size // 4))
    pixels: list[tuple[int, int, int]] = []
    for y in range(size):
        for x in range(size):
            pixels.append(ACCENT[:3] if mask[y][x] else (0, 0, 0))

    def set_px(x: int, y: int) -> None:
        if 0 <= x < size and 0 <= y < size:
            pixels[y * size + x] = INK[:3]

    scale = size / 32
    for y in range(int(8 * scale), int(25 * scale)):
        for x in range(int(10 * scale), int(13 * scale)):
            set_px(x, y)
    for y in range(int(8 * scale), int(16 * scale)):
        for x in range(int(10 * scale), int(21 * scale)):
            if y < int(11 * scale) or x < int(18 * scale):
                set_px(x, y)
    for y in range(int(15 * scale), int(25 * scale)):
        for x in range(int(10 * scale), int(22 * scale)):
            if y > int(21 * scale) or x < int(19 * scale):
                set_px(x, y)

    return pixels


def _write_png(path: Path, size: int, pixels: list[tuple[int, int, int]]) -> None:
    raw = b"".join(
        b"\x00" + bytes(pixels[y * size + x]) for y in range(size) for x in range(size)
    )
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.write_bytes(png)


def _write_ico(path: Path, sizes: list[int]) -> None:
    images: list[bytes] = []
    for size in sizes:
        pixels = _draw_b(size)
        raw = b"".join(bytes((*pixels[y * size + x], 0)) for y in range(size) for x in range(size))
        bmp_header = struct.pack("<IIIHHIIIIII", 40, size, size * 2, 1, 32, 0, len(raw), 0, 0, 0, 0)
        images.append(bmp_header + raw + b"\x00" * (size * 4))

    offset = 6 + 16 * len(images)
    header = struct.pack("<HHH", 0, 1, len(images))
    entries = b""
    for idx, size in enumerate(sizes):
        entries += struct.pack(
            "<BBBBHHII",
            size if size < 256 else 0,
            size if size < 256 else 0,
            0,
            0,
            1,
            32,
            len(images[idx]),
            offset,
        )
        offset += len(images[idx])

    path.write_bytes(header + entries + b"".join(images))


def main() -> None:
    png_path = ROOT / "design" / "favicon.png"
    _write_png(png_path, 32, _draw_b(32))
    ico_bytes_path = ROOT / "design" / "favicon.ico"
    _write_ico(ico_bytes_path, [16, 32])

    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(ico_bytes_path.read_bytes())
        print(f"Wrote {target.relative_to(ROOT)}")

    svg_targets = [
        ROOT / "web" / "public" / "public" / "favicon.svg",
        ROOT / "web" / "review" / "public" / "favicon.svg",
    ]
    svg_source = (ROOT / "design" / "favicon.svg").read_text(encoding="utf-8")
    for target in svg_targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg_source, encoding="utf-8")
        print(f"Wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
