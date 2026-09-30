"""Raster renderer for the recursive T-square fractal."""
import base64

BACKGROUND = (8, 11, 24)


def _subtree_size(level):
    return (4 ** (level + 1) - 1) // 3


def render_fractal(width, height, x, y, side, depth, color_for_level,
                   reveal_progress=0.0, max_depth=7):
    """Return (base64 PPM frame, square count), clipping off-screen branches."""
    pixels = bytearray(BACKGROUND * (width * height))
    rgb_by_level = {}
    for level in range(-1, depth + 1):
        value = color_for_level(level).lstrip("#")
        rgb_by_level[level] = bytes.fromhex(value)

    def paint(cx, cy, square_side, rgb):
        half = square_side / 2
        left = max(0, int(cx - half))
        right = min(width, int(cx + half + 1))
        top = max(0, int(cy - half))
        bottom = min(height, int(cy + half + 1))
        if left >= right or top >= bottom:
            return
        row = rgb * (right - left)
        start = (top * width + left) * 3
        end = (top * width + right) * 3
        for _ in range(top, bottom):
            pixels[start:end] = row
            start += width * 3
            end += width * 3

    def visit(cx, cy, square_side, level):
        # Descendants can reach almost one parent-side from their center.
        margin = square_side
        if (cx + margin < 0 or cy + margin < 0 or
                cx - margin >= width or cy - margin >= height):
            total = _subtree_size(level)
            if depth < max_depth and reveal_progress > 0:
                total += 4 ** (level + 1)
            return total

        paint(cx, cy, square_side, rgb_by_level[level])
        if level > 0:
            child_side = square_side / 2
            offset = square_side / 2
            count = 1
            for dx, dy in ((-offset, -offset), (offset, -offset),
                           (-offset, offset), (offset, offset)):
                count += visit(cx + dx, cy + dy, child_side, level - 1)
            return count

        count = 1
        if depth < max_depth and reveal_progress > 0:
            child_side = square_side / 2 * reveal_progress
            offset = square_side / 2
            child_color = rgb_by_level[-1]
            for dx, dy in ((-offset, -offset), (offset, -offset),
                           (-offset, offset), (offset, offset)):
                paint(cx + dx, cy + dy, child_side, child_color)
                count += 1
        return count

    count = visit(x, y, side, depth)
    ppm = f"P6\n{width} {height}\n255\n".encode("ascii") + pixels
    return base64.b64encode(ppm).decode("ascii"), count
