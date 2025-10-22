import argparse
import json
import os
import re
import shutil
from collections import Counter, defaultdict


def sanitize_folder_name(name: str) -> str:
    """
    Make a Windows-safe folder name:
    - Strip, collapse whitespace
    - Replace invalid characters <>:"/\|?* with '_'
    - Avoid reserved device names (CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9)
    """
    if not name:
        return "Others"
    name = str(name).strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[<>:\"/\\|?*]", "_", name)
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *{f"COM{i}" for i in range(1, 10)},
        *{f"LPT{i}" for i in range(1, 10)},
    }
    upper = name.upper()
    if upper in reserved:
        name = f"_{name}"
    # Trim overly long names for safety
    return name[:100]


def extract_labels(obj: dict) -> dict:
    """Return a dict with keys: primary (str or list), secondary (list[str])."""
    labels = obj.get("labels", obj)

    primary = labels.get("primary_label")
    if primary is None:
        primary = labels.get("primaryLabel")

    secondary = labels.get("secondary_labels")
    if secondary is None:
        secondary = labels.get("secondaryLabels")

    # Normalize types
    if isinstance(primary, list):
        prim_list = [str(x).strip() for x in primary if str(x).strip()]
    elif isinstance(primary, str):
        prim_list = [primary.strip()] if primary.strip() else []
    else:
        prim_list = []

    if isinstance(secondary, list):
        sec_list = [str(x).strip() for x in secondary if str(x).strip()]
    elif isinstance(secondary, str):
        sec_list = [secondary.strip()] if secondary.strip() else []
    else:
        sec_list = []

    return {"primary": prim_list, "secondary": sec_list}


def choose_category(prim_list, sec_list, others_label: str = "Others") -> str:
    # If multiple primaries, choose the first non-empty.
    if prim_list:
        return prim_list[0]
    # Fallback: first secondary if no primary present
    if sec_list:
        return sec_list[0]
    return others_label


def scan_and_plan(root: str, others_label: str, invalid_label: str):
    counts = Counter()
    per_file_plan = []  # (src_path, target_category, dst_path)
    errors = []  # (path, error)

    for entry in os.scandir(root):
        if not entry.is_file():
            continue
        if not entry.name.lower().endswith(".json"):
            continue

        src_path = entry.path
        try:
            with open(src_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            cat = invalid_label
            counts[cat] += 1
            per_file_plan.append((src_path, cat, None, "invalid"))
            errors.append((src_path, str(e)))
            continue

        labels = extract_labels(data)
        category = choose_category(labels["primary"], labels["secondary"], others_label)
        counts[category] += 1
        per_file_plan.append((src_path, category, None, "ok"))

    return counts, per_file_plan, errors


def move_files(root: str, plan, others_label: str, invalid_label: str, apply: bool):
    moved = 0
    skipped = 0
    for src_path, category, _dst, status in plan:
        parent = os.path.dirname(src_path)
        # Skip if already inside a category folder (i.e., not directly under root)
        # We only move files directly under root.
        if os.path.normpath(parent) != os.path.normpath(root):
            skipped += 1
            continue

        safe_category = sanitize_folder_name(category)
        dst_dir = os.path.join(root, safe_category)
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, os.path.basename(src_path))

        if os.path.normpath(src_path) == os.path.normpath(dst_path):
            skipped += 1
            continue

        if apply:
            shutil.move(src_path, dst_path)
        moved += 1

    return moved, skipped


def main():
    parser = argparse.ArgumentParser(description="Count MCP server categories and organize files by primary label.")
    parser.add_argument("--root", default="mcp_servers", help="Root folder containing MCP server JSON files.")
    parser.add_argument("--apply", action="store_true", help="Actually move files. Without this, runs a dry-run.")
    parser.add_argument("--others-label", default="Others", help="Folder name for unlabeled files.")
    parser.add_argument("--invalid-label", default="Invalid JSON", help="Folder name for invalid JSON files.")
    args = parser.parse_args()

    root = args.root
    if not os.path.isdir(root):
        print(f"Root folder not found: {root}")
        return 1

    counts, plan, errors = scan_and_plan(root, args.others_label, args.invalid_label)

    print("=== Category Counts (by primary, fallback to secondary) ===")
    for cat, cnt in counts.most_common():
        print(f"{cat}\t{cnt}")

    if errors:
        print("\n=== Invalid JSON Files ===")
        for p, err in errors[:50]:
            print(f"{p}: {err}")
        if len(errors) > 50:
            print(f"... and {len(errors) - 50} more")

    # Show a small sample of the move plan
    print("\n=== Sample Move Plan (first 30) ===")
    shown = 0
    for src_path, category, _dst, status in plan:
        if shown >= 30:
            break
        print(f"{os.path.basename(src_path)} -> {sanitize_folder_name(category)}")
        shown += 1

    if args.apply:
        moved, skipped = move_files(root, plan, args.others_label, args.invalid_label, apply=True)
        print(f"\nApplied moves. Moved: {moved}, Skipped: {skipped}")
    else:
        print("\nDry-run only. Re-run with --apply to move files.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

