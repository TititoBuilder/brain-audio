import json
import re
from pathlib import Path

PROFILES_DIR = Path(__file__).parent / "profiles"


def load_profile(name: str) -> dict:
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        print(f"[brain-audio] Profile '{name}' not found, falling back to default.")
        path = PROFILES_DIR / "default.json"
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str, profile: str = "default") -> str:
    """
    Normalize text for TTS consumption using a named domain profile.

    Args:
        text:    Raw input text (markdown, plain text, etc.)
        profile: Domain profile name — 'soccer', 'construction', 'default'

    Returns:
        TTS-ready string with domain-specific expansions applied.

    Example:
        >>> normalize('xG: 2.3 in the 90+4 minute', profile='soccer')
        'Expected Goals: 2.3 in the ninety fourth minute'
    """
    rules = load_profile(profile)
    for pattern, replacement in rules.get("replacements", {}).items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
