from __future__ import annotations

import argparse
import logging
import logging.handlers
import sys

from dotenv import find_dotenv, load_dotenv

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
    # Load .env before anything reads configuration: path overrides, logging
    # setup and source credentials all go through os.getenv. usecwd anchors the
    # search at the working directory, so an installed build finds the user's
    # .env instead of searching next to its own package files.
    load_dotenv(find_dotenv(usecwd=True))

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
        "--host",
        default="127.0.0.1",
        help="Address to bind (default: 127.0.0.1). The dashboard has no "
             "authentication — only widen this on a trusted network.",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8421,
        help="Port to serve on (default: 8421)",
    )

    # mcp
    mcp_parser = subparsers.add_parser("mcp", help="Serve the MCP endpoint for Claude clients")
    mcp_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Address to bind (default: 127.0.0.1). TLS terminates upstream.",
    )
    mcp_parser.add_argument(
        "--port",
        type=int,
        default=8766,
        help="Port to serve on (default: 8766)",
    )
    mcp_parser.add_argument(
        "--tokens-file",
        required=True,
        help="Path to the JSON file of hashed bearer-token records",
    )
    mcp_parser.add_argument(
        "--allowed-host",
        action="append",
        default=[],
        metavar="HOST",
        help=(
            "Public hostname this server is reached by, e.g. taste.example.com. "
            "Repeatable. Required when an HTTPS reverse proxy fronts the server: "
            "the transport checks the Host header against an allow-list, and a "
            "forwarded public hostname is otherwise refused with 421. Loopback "
            "and the bound address are always allowed."
        ),
    )

    # mcp-token
    subparsers.add_parser(
        "mcp-token",
        help="Mint a bearer token and print the record to add to the tokens file",
    ).add_argument("--name", default="default", help="Name for the token record")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    setup_logging()

    # Minting a token touches no data, so it must not create a database.
    if args.command == "mcp-token":
        from startaste.mcp.auth import generate_token, hash_token
        token = generate_token()
        print(f"token (shown once, store it now):\n  {token}\n")
        print("record to add to the tokens file:")
        print(f'  {{"name": "{args.name}", "hash": "{hash_token(token)}", "scopes": ["read"]}}')
        return

    # The MCP server opens the database read-only and never creates one.
    if args.command == "mcp":
        from startaste.mcp.server import serve
        serve(
            host=args.host,
            port=args.port,
            tokens_file=args.tokens_file,
            allowed_hosts=args.allowed_host,
        )
        return

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
        print(f"Starting dashboard at http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port)
