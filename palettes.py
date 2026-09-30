"""Colour palettes and colour selection for the T-square fractal."""
import colorsys

PALETTES = {
    "Неон": ("#00f5d4", "#f72585", "#fee440", "#4361ee"),
    "Огонь": ("#ffbe0b", "#fb5607", "#ff006e", "#9d0208"),
    "Океан": ("#48cae4", "#0077b6", "#90e0ef", "#03045e"),
    "Лес": ("#95d5b2", "#40916c", "#d8f3dc", "#2d6a4f"),
}


def level_color(level, palette_name, rainbow, phase):
    if rainbow:
        hue = (level * 0.17 + phase) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.82, 1.0)
        return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    return PALETTES[palette_name][level % 4]
