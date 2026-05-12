from __future__ import annotations

import argparse
import logging
import logging.handlers
import sys

from startaste import __version__


def setup_logging(level: str = "INFO"):
    log = logging.getLogger("startaste")
    log.setLevel(logging.DEBUG)

    format_string = "%(asctime)s | %(levelname)-8s | %(message)s"

    handler = logging.handlers.RotatingFileHandler(
        "startaste.log", maxBytes=12500000, backupCount=3, encoding="utf8"
    )
    handler.setFormatter(logging.Formatter(format_string))
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))
    console.setLevel(level)
    log.addHandler(console)


def main():
    parser = argparse.ArgumentParser(
        prog="startaste",
        description="Own your stars, upvotes, and favorites.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # sync
    subparsers.add_parser("sync", help="Sync upvoted items from Hacker News to local database")

    # export
    export_parser = subparsers.add_parser("export", help="Export items from local database")
    export_parser.add_argument(
        "--format",
        choices=["json"],
        default="json",
        help="Output format (default: json)",
    )
    export_parser.add_argument(
        "-s", "--select",
        nargs="+",
        choices=["story", "comment"],
        default=["story", "comment"],
        help="Select which items to export (default: both)",
    )
    export_parser.add_argument(
        "-f", "--file",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    setup_logging()

    if args.command == "sync":
        from startaste.sync import run_sync
        run_sync()
    elif args.command == "export":
        from startaste.export import run_export
        run_export(format=args.format, select=args.select, file=args.file)
