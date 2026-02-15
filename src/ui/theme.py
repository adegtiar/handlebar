"""Centralized theme module for Playa Nickname Booth.

Desert sunset palette with neon playa accents, gradient utilities,
and pyfiglet configuration for the terminal UI.
"""

from rich.rule import Rule
from rich.text import Text


# ---------------------------------------------------------------------------
# Color palette  (desert sunset + neon playa accents)
# ---------------------------------------------------------------------------

# Primary warm colors
DEEP_ORANGE = "rgb(255,111,0)"
GOLD = "rgb(255,191,0)"
CORAL = "rgb(255,85,85)"
HOT_PINK = "rgb(230,50,130)"

# Accent neon colors
ELECTRIC_TEAL = "rgb(0,255,204)"
PLAYA_PURPLE = "rgb(180,100,255)"
NIGHT_BLUE = "rgb(80,160,255)"

# Neutral tones
WARM_SAND = "rgb(210,180,140)"
MUTED_SAND = "rgb(140,120,95)"

# ---------------------------------------------------------------------------
# Named styles  (Rich markup strings)
# ---------------------------------------------------------------------------

STYLE_TITLE = f"bold {DEEP_ORANGE}"
STYLE_HINT = f"italic {WARM_SAND}"
STYLE_QUESTION = "bold white"
STYLE_PROGRESS = f"bold {ELECTRIC_TEAL}"
STYLE_SUCCESS = f"bold {ELECTRIC_TEAL}"
STYLE_ERROR = f"bold {CORAL}"
STYLE_DIM = f"{MUTED_SAND}"
STYLE_KEY_BRACKET = f"bold {ELECTRIC_TEAL}"
STYLE_KEY_NAME = f"bold {GOLD}"
STYLE_KEY_DESC = MUTED_SAND

# ---------------------------------------------------------------------------
# Gradient definitions  (lists of (R, G, B) stops)
# ---------------------------------------------------------------------------

GRADIENT_SUNSET = [
    (255, 85, 85),    # coral
    (255, 111, 0),    # deep orange
    (255, 191, 0),    # gold
    (255, 111, 0),    # deep orange
    (230, 50, 130),   # hot pink
]

GRADIENT_NEON = [
    (0, 255, 204),    # electric teal
    (80, 160, 255),   # night blue
    (180, 100, 255),  # playa purple
    (255, 85, 85),    # coral
]

GRADIENT_FIRE = [
    (255, 80, 20),    # red-orange
    (255, 111, 0),    # orange
    (255, 191, 0),    # gold
    (255, 111, 0),    # orange
    (255, 80, 20),    # red-orange
]

# ---------------------------------------------------------------------------
# Pyfiglet configuration
# ---------------------------------------------------------------------------

FIGLET_FONT_TITLE = "slant"
FIGLET_FONT_TITLE_NARROW = "small_slant"
FIGLET_FONT_NICKNAME = "big"

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def _lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linearly interpolate between two RGB colors."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _gradient_color_at(gradient: list[tuple[int, int, int]], t: float) -> tuple[int, int, int]:
    """Get the interpolated color at position *t* (0..1) along a gradient."""
    if t <= 0:
        return gradient[0]
    if t >= 1:
        return gradient[-1]
    scaled = t * (len(gradient) - 1)
    idx = int(scaled)
    frac = scaled - idx
    if idx >= len(gradient) - 1:
        return gradient[-1]
    return _lerp_color(gradient[idx], gradient[idx + 1], frac)


def make_gradient_text(
    text: str,
    gradient: list[tuple[int, int, int]],
    bold: bool = False,
) -> Text:
    """Apply per-character RGB gradient across *text*.

    Works with multi-line strings (e.g. pyfiglet output) by treating
    only visible characters for position calculation while preserving
    newlines and spaces.
    """
    result = Text()
    # Collect all visible (non-whitespace) character positions
    visible_chars: list[tuple[int, str]] = []
    all_chars: list[str] = list(text)

    for i, ch in enumerate(all_chars):
        if ch not in ("\n", " "):
            visible_chars.append((i, ch))

    total_visible = len(visible_chars)
    if total_visible == 0:
        result.append(text)
        return result

    # Build a mapping: char_index -> gradient position
    vis_positions: dict[int, float] = {}
    for vi, (ci, _) in enumerate(visible_chars):
        vis_positions[ci] = vi / max(total_visible - 1, 1)

    for i, ch in enumerate(all_chars):
        if i in vis_positions:
            r, g, b = _gradient_color_at(gradient, vis_positions[i])
            style = f"rgb({r},{g},{b})"
            if bold:
                style = f"bold {style}"
            result.append(ch, style=style)
        else:
            result.append(ch)

    return result


def styled_rule(title: str = "") -> Rule:
    """Return a ``~``-character Rule in orange (desert heat shimmer)."""
    return Rule(title=title, characters="~", style=DEEP_ORANGE)
