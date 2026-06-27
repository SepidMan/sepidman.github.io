from __future__ import annotations

import argparse
import sys

from .errors import ResumePipelineError
from .pipeline import build_resume_pdf, generate_rendercv_yaml, validate_resume_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resume-pipeline",
        description="Validate, convert, and build the resume PDF pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate resume data and pipeline config.")

    convert_parser = subparsers.add_parser(
        "convert",
        help="Generate the intermediate RenderCV YAML for a variant.",
    )
    convert_parser.add_argument("--variant", default="default", help="Variant name to convert.")
    convert_parser.add_argument("--output", help="Optional path for the generated YAML file.")

    build_parser = subparsers.add_parser(
        "build",
        help="Build one or more PDF variants through RenderCV.",
    )
    build_parser.add_argument("--variant", default="default", help="Variant name to build.")
    build_parser.add_argument("--all", action="store_true", help="Build all configured variants.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            validate_resume_pipeline()
            print("Resume source, schema, profiles, and RenderCV variant config are valid.")
            return 0

        if args.command == "convert":
            result = generate_rendercv_yaml(variant=args.variant, output=args.output)
            print(f'Generated RenderCV input for variant "{args.variant}" at {result["output_path"]}')
            return 0

        if args.command == "build":
            outputs = build_resume_pdf(variant=args.variant, build_all=args.all)
            for output in outputs:
                print(f"Built RenderCV PDF: {output}")
            return 0

        parser.error(f"Unknown command: {args.command}")
    except ResumePipelineError as error:
        print(error, file=sys.stderr)
        return 1
    except Exception as error:  # pragma: no cover - CLI safety net
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
