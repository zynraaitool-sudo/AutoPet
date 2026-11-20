from pathlib import Path
from urllib.parse import urlparse
import json
import re
import subprocess

ROOT = Path(r"D:\AutoPet")
PRODUCT_DIR = ROOT / "src" / "content" / "products"
REVIEW_DIR = ROOT / "src" / "content" / "reviews"


def split_frontmatter(text):
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return text, ""
    return text[: end + 4], text[end + 4:].lstrip("\r\n")


def scalar(frontmatter, key):
    lines = frontmatter.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(key + ":"):
            inline = line.split(":", 1)[1].strip()
            if inline:
                inline = inline.strip("\"'")
                i += 1
                continuation = []
                while i < len(lines) and lines[i].startswith("  ") and ":" not in lines[i]:
                    continuation.append(lines[i].strip())
                    i += 1
                return " ".join([inline] + continuation).strip()
            i += 1
            continuation = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                continuation.append(lines[i].strip())
                i += 1
            return " ".join(continuation).strip()
    return ""


# Repair multiline overview text where the bulk transform used only the first description line.
fixed_descriptions = 0
for path in sorted(PRODUCT_DIR.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    description = scalar(fm, "description")
    if description and "<!-- autopet-master-optimized -->" in body:
        body = re.sub(
            r"(<!-- autopet-master-optimized -->\n## Overview\n)(.*?)(\n\n## Listed features)",
            lambda m: m.group(1) + description + m.group(3),
            body,
            count=1,
        )
        path.write_text(fm + "\n\n" + body, encoding="utf-8")
        fixed_descriptions += 1

# Correct article affiliate flags only when a URL exactly matches an existing affiliateUrl.
affiliate_map = {}
for path in sorted(PRODUCT_DIR.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)
    url = scalar(fm, "affiliateUrl")
    if url:
        affiliate_map[url] = True

affiliate_flags_fixed = 0
for path in sorted(REVIEW_DIR.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if not affiliate_map:
        break
    changed = False
    for url in affiliate_map:
        if url in text:
            for line_match in re.finditer(r"(?m)^(\s+)(affiliate:)\s*false\s*$", fm):
                before = fm[: line_match.start()]
                after = fm[line_match.end():]
                fm = before + line_match.group(1) + "affiliate: true" + after
                changed = True
                affiliate_flags_fixed += 1
                break
    if changed:
        path.write_text(fm + "\n\n" + body, encoding="utf-8")

# Snapshot validation: file counts, slugs, frontmatter status, affiliate values, local images.
product_paths = sorted(PRODUCT_DIR.glob("*.md"))
review_paths = sorted(REVIEW_DIR.glob("*.md"))
errors = []

if len(product_paths) != 100:
    errors.append(f"Product count changed: {len(product_paths)}")
if len(review_paths) != 98:
    errors.append(f"Review count changed: {len(review_paths)}")

slugs = {p.stem for p in product_paths + review_paths}

for path in product_paths + review_paths:
    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    if not fm.startswith("---") or not fm.endswith("---"):
        errors.append(f"Malformed frontmatter: {path.relative_to(ROOT)}")
    draft = scalar(fm, "draft")
    if draft not in ("true", "false"):
        errors.append(f"Invalid draft status: {path.relative_to(ROOT)}")

for path in product_paths:
    fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
    for key in ("productUrl", "affiliateUrl"):
        url = scalar(fm, key)
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                errors.append(f"Invalid {key}: {path.relative_to(ROOT)}")
    image = scalar(fm, "image")
    if image:
        local = ROOT / "public" / image.lstrip("/")
        if not local.exists():
            errors.append(f"Missing image: {path.relative_to(ROOT)} -> {image}")

for path in review_paths:
    fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
    image = scalar(fm, "image")
    if image:
        local = ROOT / "public" / image.lstrip("/")
        if not local.exists():
            errors.append(f"Missing image: {path.relative_to(ROOT)} -> {image}")
    for destination in re.findall(r"\]\((/[^)#]+/)", body):
        if destination.startswith("/products/"):
            slug = destination.strip("/").split("/")[-1]
            if slug not in {p.stem for p in product_paths}:
                errors.append(f"Broken product link: {path.relative_to(ROOT)} -> {destination}")
        elif destination.startswith("/reviews/"):
            slug = destination.strip("/").split("/")[-1]
            if slug not in {p.stem for p in review_paths}:
                errors.append(f"Broken review link: {path.relative_to(ROOT)} -> {destination}")
        elif destination.startswith("/category/"):
            pass

print(json.dumps({
    "fixed_descriptions": fixed_descriptions,
    "affiliate_flags_fixed": affiliate_flags_fixed,
    "product_count": len(product_paths),
    "review_count": len(review_paths),
    "errors": errors,
}, indent=2))

if errors:
    raise SystemExit(1)
