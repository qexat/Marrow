#!/usr/bin/env python3

from marrow.environment import Environment

from .parser import CLIParser


def main() -> int:
    namespace = CLIParser().parse_args()
    environment = Environment.from_args(namespace)

    match namespace.command:
        case "compile":
            return environment.compile()
        case "run":
            return environment.run()
        case _:
            environment.logger.error(f"unexpected command {namespace.command!r}")
            return 1


if __name__ == "__main__":
    raise SystemExit(main())
