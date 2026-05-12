from __future__ import annotations

import argparse
import logging
import logging.handlers
import sys

from startaste import __version__


def setup_logging(level: str = "INFO"):
    from startaste.paths import get_log_path, ensure_dirs
    ensure_dirs()

    log = logging.getLogger("startaste")
    log.setLevel(logging.DEBUG)

    format_string = "%(asctime)s | %(levelname)-8s | %(message)s"

    handler = logging.handlers.RotatingFileHandler(
        str(get_log_path()), maxBytes=12500000, backupCount=3, encoding="utf8"
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
    sync_parser = subparsers.add_parser("sync", help="Sync items from sources to local database")
    sync_parser.add_argument(
        "source",
        nargs="?",
        help="Source to sync (default: all configured sources)",
    )

    # export
    export_parser = subparsers.add_parser("export", help="Export items from local database")
    export_parser.add_argument(
        "--format",
        choices=["json"],
        default="json",
        help="Output format (default: json)",
    )
    export_parser.add_argument(
        "--source",
        help="Filter by source (e.g. hn, github)",
    )
    export_parser.add_argument(
        "--type",
        help="Filter by item type (e.g. story, comment, star)",
    )
    export_parser.add_argument(
        "-f", "--file",
        help="Output file path (default: stdout)",
    )

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start local dashboard web server")
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8421,
        help="Port to serve on (default: 8421)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    setup_logging()

    from startaste.db import init_database
    init_database()

    if args.command == "sync":
        from startaste.sync import run_sync
        run_sync(source_name=args.source)
    elif args.command == "export":
        from startaste.export import run_export
        run_export(format=args.format, source=args.source, type=args.type, file=args.file)
    elif args.command == "serve":
        from startaste.dashboard import create_app
        app = create_app()
        print(f"Starting dashboard at http://localhost:{args.port}")
        app.run(host="127.0.0.1", port=args.port)
