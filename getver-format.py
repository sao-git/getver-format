#!/usr/bin/env python3

__title__ = 'getver-format'
__version__ = '0.2.0'
__license__ = 'MIT'
__desc__ = (
    'Formatter for copying latest versions of Rust crates to a Cargo manifest, using "getver" crate version fetcher')
__url__ = 'https://github.com/sao-git/getver-format'


import subprocess
#import sys
import re
import argparse


def parse_args():
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(
        add_help=True, prog=__title__)
        #usage='%(prog)s [options] [logging] network|ALL')

    parser.add_argument('crates', metavar='CRATE', type=str, nargs='+',
                        help='a list of Cargo crates')
    parser.add_argument('-p', '--show-patch',
                        dest='show_patch',
                        action='store_true',
                        help='show semver patch versions')

    return parser.parse_args()


def get_crate_lists(output_clean):
    crates_list = output_clean.splitlines()
    crates_found = []
    crates_not_found = []

    for n in crates_list:
        if n.find("doesn't exist") != -1:
            crates_not_found.append(n)
        else:
            crates_found.append(n)

    crates_found = [s.split(': ') for s in crates_found]
    crates_not_found = [s.split("'")[1] for s in crates_not_found]

    return crates_found, crates_not_found


if __name__ == '__main__':
    args = parse_args()

    # Expects `getver` to be in $PATH or %PATH%
    # TODO:
    #       Add command line option to pass in path to `getver`
    command = ["getver"] + args.crates
    getver_proc = subprocess.run(args = command, capture_output = True, text = True)

    # Clean ANSI color codes from the input for easier formatting
    # https://stackoverflow.com/a/14693789
    ansi_color_match = r'\x1B\[[0-?]*[ -/]*[@-~]'
    output_clean = re.sub(ansi_color_match, '', getver_proc.stdout)

    # Parse the cleaned output into "found" and "not found" lists,
    # where "found" contains items of the format `['name', 'version']`
    # and "not found" contains items of the format `'name'`
    crates_found, crates_not_found = get_crate_lists(output_clean)

    # By default, remove the semver patch version number from the output
    if not args.show_patch:
        crates_found = [[name, '.'.join(version.split('.')[:2])] for name, version in crates_found]

    # Format found crates into a newline-separated string of
    # `name = "version"`
    crates_found_str = '\n'.join(f'{name} = "{version}"' for name, version in crates_found)
    crates_not_found_str = '\n'.join(crates_not_found)

    #print(output_format, end = '')

    print(f"{crates_found_str}\n\nThe following crates were not found:\n{crates_not_found_str}")
