# brain-audio — Shared TTS Text Normalizer

Shared Python package that normalizes text for TTS consumption using
domain-specific profiles. Lives at `C:\Dev\shared\brain-audio\` and is
installed editably into multiple project venvs so all consumers stay in sync.

---

## Usage

```python
from brain_audio import normalize

text = normalize(raw_text, profile="soccer")
text = normalize(raw_text, profile="construction")
text = normalize(raw_text, profile="default")   # markdown cleanup + common abbreviations
```

`profile` defaults to `"default"` if omitted. Unknown profile names fall back
to `default` with a console warning.

---

## Package Layout

```
brain_audio/
    __init__.py          # exports: normalize, load_profile
    converter.py         # normalize() + load_profile() + _build_flags()
    profiles/
        default.json     # markdown cleanup + abbreviation expansion
        soccer.json      # BDF / football domain
        construction.json
```

---

## Profile Format

Profiles are JSON files in `brain_audio/profiles/`. Two formats are supported:

### New format (list of rule objects) — use this for all new profiles

```json
{
  "replacements": [
    {"pattern": "\\bxG\\b",    "replacement": "Expected Goals"},
    {"pattern": "^#{1,6}\\s+(.+)$", "replacement": "Section: \\1", "flags": ["MULTILINE"]},
    {"pattern": "```\\w*\\n(.*?)```", "replacement": "[Code block] \\1", "flags": ["DOTALL"]}
  ]
}
```

Supported flags: `IGNORECASE`, `MULTILINE`, `DOTALL`.
Default when `flags` is omitted: `["IGNORECASE"]`.

Rules are applied **in order** — put more specific patterns before general ones.

### Legacy format (flat dict) — backward compat only, each rule gets IGNORECASE

```json
{
  "replacements": {
    "\\bxG\\b": "Expected Goals"
  }
}
```

---

## Adding a New Profile

1. Create `brain_audio/profiles/<name>.json` using the list format above.
2. No code changes needed — `load_profile("<name>")` resolves by filename.
3. Test: `from brain_audio import normalize; normalize("...", profile="<name>")`

---

## Installed Venvs

| Project | Venv path | Install command used |
|---|---|---|
| BDF Soccer Content Generator | `C:\Dev\Projects\soccer-content-generator\venv\` | `pip install -e C:\Dev\shared\brain-audio` |
| CA (Custom Agent) | `C:\Knowledge\CA\venv\` | `pip install -e C:\Dev\shared\brain-audio` |
| Read-Along App | `C:\Users\titit\Projects\read-along-app\backend\venv\` | `pip install -e C:\Dev\shared\brain-audio` |

Editable install means changes to `converter.py` or any profile JSON take
effect immediately in all venvs — no reinstall needed.

---

## Re-installing After a Venv Rebuild

```powershell
& "<venv>\Scripts\python.exe" -m pip install -e C:\Dev\shared\brain-audio
```
