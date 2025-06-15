from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Collect all markdown files across the repository into docs/merged_markdown."""

    help = "Collect *.md files into docs/merged_markdown for assistant training"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print paths instead of copying",
        )
        parser.add_argument(
            "--include-dotfiles",
            action="store_true",
            help="Include hidden markdown files",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing files in the destination",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        include_dot = options.get("include_dotfiles", False)
        overwrite = options.get("overwrite", False)

        repo_root = settings.BASE_DIR.parent
        dest_root = repo_root / "docs" / "merged_markdown"
        dest_root.mkdir(parents=True, exist_ok=True)

        copied = skipped = matched = 0
        seen_hashes: dict[str, Path] = {}
        duplicates: list[tuple[Path, Path]] = []

        for path in repo_root.rglob("*.md"):
            if not include_dot and path.name.startswith("."):
                continue
            if dest_root in path.parents:
                continue

            rel = path.relative_to(repo_root)
            flat_name = str(rel).replace("/", "__")
            dest_path = dest_root / flat_name

            file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if file_hash in seen_hashes:
                duplicates.append((path, seen_hashes[file_hash]))
                skipped += 1
                continue

            if dest_path.exists():
                existing_hash = hashlib.sha256(dest_path.read_bytes()).hexdigest()
                if existing_hash == file_hash:
                    matched += 1
                    seen_hashes[file_hash] = path
                    continue
                if not overwrite:
                    self.stdout.write(
                        f"Skipping {path} (destination exists with different contents)"
                    )
                    skipped += 1
                    continue

            if dry_run:
                self.stdout.write(f"Would copy {path} -> {dest_path}")
            else:
                shutil.copy2(path, dest_path)
            copied += 1
            seen_hashes[file_hash] = path

        self.stdout.write(
            self.style.SUCCESS(
                f"Copied: {copied} | Skipped: {skipped} | Matched: {matched}"
            )
        )

        if duplicates:
            self.stdout.write("Duplicate files (same hash):")
            for dup, original in duplicates:
                self.stdout.write(f"  {dup} -> {original}")
