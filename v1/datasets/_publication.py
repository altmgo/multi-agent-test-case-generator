"""Publish normalized dataset artifacts without replacing existing files."""

import fcntl
import os
from pathlib import Path
from tempfile import TemporaryDirectory


def publish(output: Path, artifacts: dict[Path, bytes], dataset: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    # Lock the directory so cooperating writers preflight and publish together.
    directory_fd = os.open(output, os.O_RDONLY)
    try:
        fcntl.flock(directory_fd, fcntl.LOCK_EX)
        missing = []
        # Check the provenance manifest first. Publication below restores the
        # original order so a missing manifest is published last.
        for path, content in reversed(artifacts.items()):
            target = output / path
            try:
                existing = target.read_bytes()
            except FileNotFoundError:
                missing.append(path)
                continue
            if existing != content:
                raise ValueError(
                    f"{dataset} publication conflict at {target}: existing artifact differs. "
                    "Use a separate output directory for a different source or taxonomy version."
                )
        if not missing:
            return

        with TemporaryDirectory(dir=output) as staging:
            paths = list(reversed(missing))
            for path in paths:
                staged = Path(staging) / path
                staged.parent.mkdir(parents=True, exist_ok=True)
                staged.write_bytes(artifacts[path])

            published = []
            try:
                for path in paths:
                    target = output / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.hardlink_to(Path(staging) / path)
                    published.append(target)
            except BaseException:
                for target in reversed(published):
                    target.unlink()
                raise
    finally:
        os.close(directory_fd)
