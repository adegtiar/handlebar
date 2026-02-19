"""Style mode definitions for nickname generation."""

STYLES = {
    "m": {
        "name": "mixed",
        "description": "A blend of all styles - playful, mystical, and grounded",
        "prompt_modifier": "Mix playful, mystical, and cozy elements. Be creative and unexpected.",
    },
    "y": {
        "name": "mystic",
        "description": "Spiritual, cosmic, woo-woo vibes",
        "prompt_modifier": "Channel spiritual and cosmic energy. Think third-eye openers, astral wanderers, crystal healers, and sacred geometry. Names should feel like they belong to someone who reads your aura at sunrise.",
    },
    "c": {
        "name": "chaotic",
        "description": "Wild, unpredictable, absurdist",
        "prompt_modifier": "Be chaotic, absurd, and unexpected. Embrace weirdness and surprise.",
    },
    "z": {
        "name": "cozy",
        "description": "Warm, comforting, gentle",
        "prompt_modifier": "Use warm, gentle, and comforting language. Think soft blankets and warm drinks.",
    },
    "w": {
        "name": "whimsical",
        "description": "whimsical, playful, unexpected",
        "prompt_modifier": "Be whimsical, playful, and unexpected. Embrace weirdness and surprise. Think playa names.",
    },
}

DEFAULT_STYLE = "w"
