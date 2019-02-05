# getver-format

A wrapper around the excellent Rust tool **[getver](https://github.com/phynalle/getver)** to format output for use in a `Cargo.toml` crate manifest. Written in Python.

`getver` will always pull the latest version number of a crate from [crates.io][crates-io], so this is most useful when adding a new dependency to a project or upgrading a prior dependency.

## Requirements

 * Python 3.5+
 * `getver` must be installed. See the [README](https://github.com/phynalle/getver/blob/master/README.md) for instructions

## Usage

### Basic usage

Give a list of crate names on the command line, just like `getver`:

```
$ python getver-format.py toml fomat_macros chrono cached rayon error-chain
```

A name can be listed with either an underscore or a hyphen, and the output will always use hyphens. The order of the output will match the list given.

The output is ready to copy and paste into your `Cargo.toml`:

```
toml = "0.4"
fomat-macros = "0.2"
chrono = "0.4"
cached = "0.8"
rayon = "1.0"
error-chain = "0.12"
```

### Showing patch version

If you want to show the **[semver][semver]** [patch version][semver-patch] (as in `MAJOR.MINOR.PATCH`) in the output, add `-p` or `--show-patch`:

```
$ python getver-format.py -p toml fomat_macros chrono cached rayon error-chain
toml = "0.4.10"
fomat-macros = "0.2.1"
chrono = "0.4.6"
cached = "0.8.0"
rayon = "1.0.3"
error-chain = "0.12.0"
```

### Missing crates

Names that cannot be found on [crates.io][crates-io] are printed to *standard error* in alphabetical order:

```
$ python getver-format.py bob num alice
num = "0.2"

The following crates were not found:
alice
bob
```

## Help

### Print help on the console

Add `-h` or `--help`:

```
$ python getver-format.py -h
usage: getver-format [-h] [-p] CRATE [CRATE ...]

positional arguments:
  CRATE             a list of Cargo crates

optional arguments:
  -h, --help        show this help message and exit
  -p, --show-patch  show semver patch versions
```

### At least one crate name must be given

```
$ python getver-format.py
usage: getver-format [-h] [-p] CRATE [CRATE ...]
getver-format: error: the following arguments are required: CRATE
```

## Future

Planned additions include:
 * Optional alphabetical sorting for the output
 * Suppressing missing crate warnings if desired
 * Proper changelog as a Markdown file linked from this README 

## License

Released under the MIT license.

[semver]: https://semver.org/ "Semantic Versioning"
[semver-patch]: https://semver.org/#spec-item-6 "Semantic Versioning Specification, item 6: Patch version"
[crates-io]: https://crates.io/ "crates.io: The Rust community’s crate registry"
