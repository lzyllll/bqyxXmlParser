from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.post import post, postPro


def run(xml_dir: Path, output_dir: Path) -> None:
    post_out = output_dir / "post"
    post.run(xml_dir, post_out)
    postPro.run(xml_dir, post_out)

