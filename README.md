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

See [tree.txt](./tree.txt).

Command used to generate the tree:

```sh
tree --gitignore -I "__pycache__" -I "__init__.py" marrow/
```
