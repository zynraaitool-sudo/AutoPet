from pathlib import Path
import json
import re
import subprocess

ROOT = Path(r"D:\AutoPet")
TAG = "pre-autopet-master-optimization"


def frontmatter(text):
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[: end + 4] if end >= 0 else ""


def field(text, key):
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip().strip("\"'") if match else None


errors = []
for kind in ("products", "reviews"):
    directory = ROOT / "src" / "content" / kind
    for path in sorted(directory.glob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        current = path.read_text(encoding="utf-8")
        try:
            baseline = subprocess.check_output(
                ["git", "show", f"{TAG}:{rel}"],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
            )
        except subprocess.CalledProcessError:
            errors.append(f"Missing baseline file: {rel}")
            continue

        base_fm = frontmatter(baseline)
        current_fm = frontmatter(current)
        for key in ("draft", "productUrl", "affiliateUrl", "image", "relatedArticle", "catalogVisible"):
            base_value = field(base_fm, key)
            current_value = field(current_fm, key)
            if base_value != current_value:
                errors.append(f"{rel}: {key} changed from {base_value!r} to {current_value!r}")

print(json.dumps({"error_count": len(errors), "errors": errors}, indent=2))
raise SystemExit(1 if errors else 0)
