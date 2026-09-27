from __future__ import annotations

import argparse
import warnings
from pathlib import Path

from pet_ai.reproducibility.run_manifest import create_run_manifest, write_run_manifest


def optional_path(value: str | None) -> Path | None:
    return Path(value) if value else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a structured JSON run manifest.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    parser.add_argument("--dataset-manifest")
    parser.add_argument("--split-manifest")
    parser.add_argument("--config")
    parser.add_argument("--checkpoint")
    seed_group = parser.add_mutually_exclusive_group()
    seed_group.add_argument("--declared-seed", type=int)
    seed_group.add_argument("--seed", type=int, help="Deprecated alias for --declared-seed")
    parser.add_argument("--effective-seed", type=int)
    parser.add_argument("--seed-verification-status")
    parser.add_argument("--exit-status", type=int)
    parser.add_argument("--notes")
    parser.add_argument("command", nargs="*", help="Command being recorded")
    args = parser.parse_args()

    declared_seed = args.declared_seed
    if args.seed is not None:
        warnings.warn(
            "--seed is deprecated; it records a declaration only and does not prove trainer state",
            FutureWarning,
            stacklevel=1,
        )
        declared_seed = args.seed
    manifest = create_run_manifest(
        repo_root=args.repo_root,
        dataset_manifest=optional_path(args.dataset_manifest),
        split_manifest=optional_path(args.split_manifest),
        config=optional_path(args.config),
        checkpoint=optional_path(args.checkpoint),
        seed=None,
        declared_seed=declared_seed,
        effective_seed=args.effective_seed,
        seed_verification_status=args.seed_verification_status,
        command=args.command,
        exit_status=args.exit_status,
        notes=args.notes,
    )
    write_run_manifest(manifest, args.output)
    print(f"Wrote run manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
