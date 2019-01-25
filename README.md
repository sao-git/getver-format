# getver-format

A wrapper around the excellent Rust tool [getver](https://github.com/phynalle/getver) to format output for use in a `Cargo.toml` crate manifest. Written in Python.

## Requirements

 * Python 3.5+
 * `getver` must be installed. Follow the [README](https://github.com/phynalle/getver/blob/master/README.md) for instructions
 * The folder containing `getver` must be in your `PATH` environment variable
   + A future version will have support for specifying the folder on the command line

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

Note that the output order is not necessarily the same as the input order, as `getver` returns a version number for each crate as soon as it can. A future version may support output order matching input, as well as alphabetical sorting.

## License

Released under the MIT license.
