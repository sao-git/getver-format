#!/usr/bin/env python3

__title__ = 'getver-format'
__version__ = '0.3.0'
__license__ = 'MIT'
__desc__ = (
    'Formatter for copying latest versions of Rust crates to a Cargo manifest, using "getver" crate version fetcher')
__url__ = 'https://github.com/sao-git/getver-format'


import subprocess
from sys import stderr
import re
import argparse
from collections import OrderedDict


def parse_args():
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(add_help=True, prog=__title__)

    parser.add_argument('crates', metavar='CRATE', type=str, nargs='+',
                        help='a list of Cargo crates')
    parser.add_argument('-p', '--show-patch',
                        dest='show_patch',
                        action='store_true',
                        help='show semver patch versions')

    return parser.parse_args()


def get_crate_lists(input_list, output_clean, show_patch):
    raw_crates_list = output_clean.splitlines()
    split_crates_list = (s.split(': ') for s in raw_crates_list)

    crates_found = OrderedDict.fromkeys(input_list)
    crates_not_found = []

    for n in split_crates_list:
        potential_name = n[0]
        if potential_name.find("doesn't exist") != -1:
            name_not_found = potential_name.split("'")[1]
            crates_not_found.append(name_not_found)
            del crates_found[name_not_found]
        else:
            found_version = n[1]
            crates_found[potential_name] = found_version


    if not show_patch:
        crates_found = [(name, '.'.join(version.split('.')[:2]))
                for name, version in crates_found.items()]
    else:
        crates_found = [(name, version)
                for name, version in crates_found.items()]

    return crates_found, crates_not_found


if __name__ == '__main__':
    args = parse_args()

    # Expects `getver` to be in $PATH or %PATH%
    # TODO:
    #       Add command line option to pass in path to `getver`
    command = ["getver"] + args.crates
    getver_proc = subprocess.run(args = command,
                                 capture_output = True,
                                 text = True)

    # Clean ANSI color codes from the input for easier formatting
    # https://stackoverflow.com/a/14693789
    ansi_color_match = r'\x1B\[[0-?]*[ -/]*[@-~]'
    output_clean = re.sub(ansi_color_match, '', getver_proc.stdout)

    # Parse the cleaned output into "found" and "not found" lists,
    # where "found" contains items of the format `['name', 'version']`
    # and "not found" contains items of the format `'name'`
    crates_found, crates_not_found = get_crate_lists(args.crates,
                                                     output_clean,
                                                     args.show_patch)

    found_len = len(crates_found)
    not_found_len = len(crates_not_found)

    if found_len != 0:
        # By default, remove the semver patch version number from the output

        # Format "found" crates into a newline-separated string of
        # `name = "version"`
        crates_found_str = '\n'.join(f'{name} = "{version}"' for name, version in crates_found)
        print(crates_found_str)

    # Print a list of "not found" crates in alphabetical order
    if not_found_len != 0:
        crates_not_found.sort()
        crates_not_found_str = '\n'.join(crates_not_found)
        if found_len != 0:
            sep = '\n'
        else:
            sep = ''
        print(f"{sep}The following crates were not found:\n{crates_not_found_str}", file=stderr)
