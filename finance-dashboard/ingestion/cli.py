import argparse
import sys

from ingestion.csv_importer import import_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Finance Dashboard ingestion CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    import_parser = subparsers.add_parser("import-csv", help="Import CSV transactions")
    import_parser.add_argument("--provider", required=True, help="Source provider name")
    import_parser.add_argument("--account", required=True, help="Account name")
    import_parser.add_argument("--file", required=True, help="Path to CSV file")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "import-csv":
        import_csv(provider=args.provider, account_name=args.account, csv_path=args.file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
