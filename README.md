# startaste

**Your stars are your taste.**

Startaste is a self-hostable tool for owning your stars, upvotes, and favorites across the web. Platforms like Hacker News and GitHub don't let you easily access or export your own curation data. Startaste works around that — it logs in, dumps your data, and gives it back to you.

## Vision

```
  Sources             Store            Outputs

  HN upvotes ──┐
                ├──▶  SQLite  ──▶  REST API
  GitHub stars ─┘     (yours)      AT Proto feed
  ...more                          JSON export
```

Right now, startaste syncs your Hacker News upvotes to JSON. The roadmap:

- **Now:** HN upvotes → JSON export
- **Next:** GitHub stars, unified data model, CLI with subcommands
- **Later:** Self-hosted REST API, AT Protocol integration (publish your taste as a feed)

## How to use

Set your Hacker News credentials:

```sh
# in .env file or as environment variables
HN_COMMENTS_ACCT=your_username
HN_COMMENTS_PW=your_password
```

Run:

```sh
python hn2json.py -n [pages] -f [output.json]
```

Options:

- `-n` / `--number` — pages to grab (default: 1, use a high number to get everything)
- `-f` / `--file` — output file path (default: stdout)
- `-s` / `--select` — `story`, `comment`, or both (default: both)
- `-l` / `--log` — log level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)

Example — download all upvoted stories:

```sh
python hn2json.py -n 200 -f ./startaste.json -s story
```

## History

Originally developed on iPad by Luciano Fiandesio with Pythonista, modified for JSON output by John David Pressman, rewritten by Kraktus, and continued by Pim Snel as startaste.

## License

BSD 3-Clause — see [LICENSE](LICENSE).
