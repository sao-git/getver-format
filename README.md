# getver-format

A wrapper around the excellent Rust tool **[getver](https://github.com/phynalle/getver)** to format output for use in a `Cargo.toml` crate manifest. Written in Python.

`getver` will always pull the latest version number available, so this is most useful when adding a new dependency to a crate.

## Requirements

 * Python 3.5+
 * `getver` must be installed. Follow the [README](https://github.com/phynalle/getver/blob/master/README.md) for instructions
 * The folder containing `getver` **must be** in your `PATH` environment variable

## Usage

Give a list of crate names on the command line, just like `getver`:

```
$ python getver-format.py toml fomat_macros chrono cached rayon
```

The output is ready to copy and paste into your `Cargo.toml`:

```
toml = "0.4.10"
cached = "0.8.0"
rayon = "1.0.3"
chrono = "0.4.6"
fomat-macros = "0.2.1"
```

`getver` will alert you if a crate cannot be found:

```
$ python3 getver-format.py alice bob num
the crate 'bob' doesn't exist
num = "0.2.0"
the crate 'alice' doesn't exist
```

Note that the output order is not necessarily the same as the input order, as `getver` returns a version number for each crate as soon as it can.

## Future

Planned additions include:
 * Support for specifying the folder or full path to `getver` on the command line
 * Optional matching output order to input
 * Optional alphabetical sorting
 * Listing missing crates separately
 * Suppressing missing crate warnings if desired
 * Add option for suppressing the **[semver][semver]** [patch version][semver-patch] (as in `MAJOR.MINOR.PATCH`) in the output
     + Alternatively, and more likely, make this the default behavior and have the option for *showing* the patch number

[semver]: https://semver.org/ "Semantic Versioning"
[semver-patch]: https://semver.org/#spec-item-6 "Semantic Versioning Specification, item 6: Patch version"

## License

Released under the MIT license.
