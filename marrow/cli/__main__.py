#!/usr/bin/env python3

from marrow.environment import Environment

from .parser import CLIParser


def main() -> int:
    parser = CLIParser()
    namespace = parser.parse_args()
    environment = Environment.from_args(namespace)

    match namespace.command:
        case "compile":
            return environment.compile(namespace.source)
        case "run":
            return environment.run(namespace.source)
        case "help":
            parser.get_main_parser().print_help()
            return 0
        case _:
            environment.logger.error(f"unexpected command {namespace.command!r}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
