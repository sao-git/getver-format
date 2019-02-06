# getver-format

A wrapper around **[getver][getver]**, an excellent tool for [Rust][rust-lang], to format its output for use in a [Cargo manifest][cargo-dependencies]. Written in Python.

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

A name can be listed with either an underscore or a hyphen. The output will use the canonical name on [crates.io][crates-io]. The order of the output will match the list given unless you specify a sorting option.

The output is ready to copy and paste into your `Cargo.toml`:

```
toml = "0.4"
fomat-macros = "0.2"
chrono = "0.4"
cached = "0.8"
rayon = "1.0"
error-chain = "0.12"
```

### Sort alphabetically

The output can be sorted alphabetically by adding `-a` or `--sort-alphabet`:

```
$ python getver-format.py -a toml fomat_macros chrono cached rayon error-chain
cached = "0.8"
chrono = "0.4"
error-chain = "0.12"
fomat-macros = "0.2"
rayon = "1.0"
toml = "0.4"
```

### Showing patch version

If you want the **[SemVer][semver]** [patch version][semver-patch] (as in `MAJOR.MINOR.PATCH`) in the output, add `-p` or `--show-patch`:

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

Names that cannot be found on crates.io are printed to *standard error* in alphabetical order:

```
$ python getver-format.py bob num alice
num = "0.2"

The following crates were not found:
alice
bob
```

### Hide missing crates

Missing crates can be hidden by adding `-n` or `--no-missing-crates`:

```
$ python getver-format.py -n bob num alice
num = "0.2"
```

## Help

### Print help on the console

Add `-h` or `--help`:

```
$ python getver-format.py -h
usage: getver-format [-h] [-V] [-g PATH] [-p] [-n] [-a] CRATE [CRATE ...]

getver-format 0.5.0
Print a list of the latest Rust crate versions from crates.io

positional arguments:
  CRATE                 a list of Cargo crates

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         print the program version
  -g PATH, --getver-path PATH
                        path to getver
  -p, --show-patch      show semver patch versions
  -n, --no-missing-crates
                        do not show missing crates in the output
  -a, --sort-alphabet   sort the list of crates alphabetically
```

### `getver` is not in the PATH environment variable

These must include the full path to getver, *including* the executable name.

#### Set the `GETVER_PATH` environment variable

```
$ GETVER_PATH="/path/to/getver" python getver-format.py
```

or

```
$ export GETVER_PATH="/path/to/getver"
$ python getver-format.py
```

#### Specify on the command line

Add `-g` or `--getver-path`. If there are any spaces in the path, they must be escaped with `\`, or the full path must be `"quoted"`.

This will **override** the `GETVER_PATH` variable.

### At least one crate name must be given

```
$ python getver-format.py
usage: getver-format [-h] [-V] [-g PATH] [-p] [-n] [-a] CRATE [CRATE ...]
getver-format: error: the following arguments are required: CRATE
```

## Future

### Planned additions:

 * Optional sorting by version number
 * Add a `--show-debug-output` switch for printing debugging information
 * Proper changelog as a Markdown file linked from this README
 * **Testing on Windows:** This program is currently not being tested on Windows, though it *should* run as long as you've built and installed `getver` and it can be found in your `Path`. Specifying the path with `-g` *may* fail because of OS differences.

### Known bugs:

 * If a crate name is given with an underscore and the canonical name on crates.io uses a hyphen, a `KeyError` exception will occur. Likewise, if a crate name is given with a hyphen and the canonical name uses an underscore, the final order may not match the input order.

## License

Released under the MIT license.

[getver]: https://github.com/phynalle/getver "getver by phynalle on GitHub"
[rust-lang]: https://www.rust-lang.org/ "Rust programming language"
[cargo-dependencies]: https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html#specifying-dependencies-from-cratesio "The Cargo Book: Specifying dependencies from crates.io"
[semver]: https://semver.org/ "Semantic Versioning"
[semver-patch]: https://semver.org/#spec-item-6 "Semantic Versioning Specification, item 6: Patch version"
[crates-io]: https://crates.io/ "crates.io: The Rust community’s crate registry"
