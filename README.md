# Marrow

> [!WARNING]
> This project [license](./LICENSE) is NOT open-source. Read carefully the conditions.

Project to try and test various things. Purposefully not usable.
Very unstable and likely to change a lot.

## Installation

After cloning the repository:

```sh
pip install -e .
```

## Usage

Run a marrow file:

```sh
marrow run <path>
```

Marrow programs can also be compiled without running. The `compile` command offers the same interface as `run`.

> [!NOTE]
> The marrow compiler does not produce any artefact. The `compile` command is only useful with `--verbose` and `--debug` flags enabled.

### Global flags

- `--debug`/`-d`: enable debug information, including parse tree printing, memory dump (section 0 only), basic benchmarking and register use info.
- `--verbose`/`-vb`: make marrow log what it is currently doing

## Project structure

```txt
marrow/
├── cli
│   ├── __main__.py
│   └── parser.py
├── compiler
│   ├── backend
│   │   ├── generator.py
│   │   └── macroop.py
│   ├── common.py
│   ├── compiler.py
│   ├── components.py
│   ├── frontend
│   │   ├── ast
│   │   │   └── expr.py
│   │   ├── parser
│   │   │   ├── base.py
│   │   │   ├── parser.py
│   │   │   ├── precedence.py
│   │   │   └── subparsers
│   │   │       ├── atomexpr.py
│   │   │       ├── nonprefixexpr.py
│   │   │       └── prefixexpr.py
│   │   ├── ptsc.py
│   │   ├── tokenizer.py
│   │   ├── token.py
│   │   └── token_type.py
│   ├── middleend
│   │   └── SSAIR
│   │       ├── generator.py
│   │       ├── instruction.py
│   │       └── rvalue.py
│   ├── renderers
│   │   ├── bytecode.py
│   │   ├── parse_tree.py
│   │   ├── rvalue.py
│   │   └── util.py
│   └── resources.py
├── environment.py
├── logger.py
├── runtime
│   ├── constants.py
│   ├── machine.py
│   └── rat.py
└── types.py

12 directories, 32 files
```

Command used to generate the tree:

```sh
tree --gitignore -I "__pycache__" -I "__init__.py" marrow/
```
