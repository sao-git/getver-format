#!/usr/bin/env python3

__title__ = 'getver-format'
__version__ = '0.4.0'
__license__ = 'MIT'
__desc__ = (
    'Formatter for copying latest versions of Rust crates to a Cargo manifest, using "getver" crate version fetcher')
__url__ = 'https://github.com/sao-git/getver-format'


import subprocess
from sys import stderr, exit
import re
import argparse
from collections import OrderedDict
from typing import List, Tuple, Dict, Iterable, Any, Pattern, Optional, Sequence, Match


def parse_args() -> argparse.Namespace:
    """ Set up, and return the results of, the argument parser. """
    parser = argparse.ArgumentParser(add_help=True, prog=__title__)

    parser.add_argument('crates', metavar='CRATE', type=str, nargs='+',
                        help='a list of Cargo crates')

    parser.add_argument('-p', '--show-patch',
                        dest='show_patch',
                        action='store_true',
                        help='show semver patch versions')

    parser.add_argument('-g', '--getver-path',
                        dest='getver_path',
                        default='getver',
                        help='show semver patch versions')

    return parser.parse_args()


def get_crate_lists(input_clean: Dict[str, Any],
                    output_clean: str,
                    show_patch: bool) -> Tuple[List, List]:
    """
    Parses the output of `getver` into a tuple of two lists:

        The first list contains the found crates, of type `List[Tuple[str, str]]`.
        The first element in the tuple is the name of the crate,
        the second element is the latest version number in crates.io
        This list is sorted according to the input list.

        The second list contains the missing crates, of type `List[str]`.
        This list is sorted alphabetically.
    """

    raw_crates: List[str] = output_clean.splitlines()

    split_crates: Iterable[List[str]]
    split_crates = (s.split(': ') for s in raw_crates)

    crates_not_found: List[str] = []

    for n in split_crates:
        potential_name: str = n[0]
        if potential_name.find("doesn't exist") != -1:
            name_not_found: str = potential_name.split("'")[1]
            crates_not_found.append(name_not_found)
            del input_clean[name_not_found]
        else:
            found_version: str = n[1]
            input_clean[potential_name] = found_version


    crates_found_out: List[Tuple[str, str]]
    if not show_patch:
        crates_found_out = [(name, '.'.join(version.split('.')[:2]))
                for name, version in input_clean.items()]
    else:
        crates_found_out = [(name, version)
                for name, version in input_clean.items()]


    return crates_found_out, crates_not_found


def check_version(path: List[str], ansi_pattern: Pattern[str]) -> str:
    not_found_error = "Can't find getver at the provided path"
    version_error = "Requires getver version >= 0.1.0"

    path.append('--help')
    getver_version: subprocess.CompletedProcess
    getver_version = subprocess.run(args = path,
                                    capture_output = True,
                                    text = True)
    del path[-1]

    potentially: Iterable[str]
    potentially = ansi_pattern.sub('', getver_version.stdout).splitlines()
    potentially = (s.strip() for s in potentially if s.find('getver') != -1)

    getverver: Optional[str] = next(potentially, None)
    version_string: str
    if getverver is None:
        raise ValueError(not_found_error)
    else:
        try:
            version_string = getverver.split(' ')[1]
        except IndexError:
            raise ValueError(not_found_error)


    # https://regexr.com/39s32
    #
    # Capture group indices:
    # 0. The whole version string
    # 1. MAJOR.MINOR.PATCH-PRE_RELEASE (what you should be evaluating for precendence)
    # 2. MAJOR
    # 3. MINOR
    # 4. PATCH
    # 5. PRERELEASE
    # 6. BUILD_METADATA
    semver_match: Optional[Match[str]]
    semver_groups: Sequence[str]
    semver_match = re.match(r'^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$', version_string)
    if semver_match is None:
        raise ValueError(not_found_error)
    else:
        semver_groups = semver_match.groups()

    major, minor, patch = (int(s) for s in semver_groups[2:5])
    if major >= 0 and minor >= 1 and patch >= 0:
        return semver_groups[1]
    else:
        raise ValueError()


if __name__ == '__main__':
    args: argparse.Namespace = parse_args()

    # https://stackoverflow.com/a/14693789
    ansi_color_match: Pattern[str]
    ansi_color_match = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    # Check if `getver` is in PATH or the path provided by -g
    gv_path = args.getver_path.split(' ')
    gv_version: str
    try:
        gv_version = check_version(gv_path, ansi_color_match)
    except ValueError as e:
        print(f'Error: {e}', file=stderr)
        exit(1)

    # Replace underscores (U+005F) in the input list with hyphens (U+002D),
    # then remove duplicate names from the list.
    #
    # `input_clean` will be mutated in `get_crate_lists()`, which will delete
    # missing crates from the dict and append version numbers to the found keys.
    # This is safe because `input_clean` will not be used after the final
    # lists are created.
    input_clean: Dict[str, Any]
    input_clean = OrderedDict.fromkeys(s.replace('_', '-') for s in args.crates)

    # Run `getver` with the cleaned input list
    run_command: List[str]
    run_command = gv_path + list(input_clean.keys())

    getver_proc: subprocess.CompletedProcess
    getver_proc = subprocess.run(args = run_command,
                                 capture_output = True,
                                 text = True)

    # Clean ANSI color codes from the input for easier formatting
    output_clean: str = ansi_color_match.sub('', getver_proc.stdout)


    # Parse the cleaned output into "found" and "not found" lists,
    # where "found" contains items of the format `('name', 'version')`
    # and "not found" contains items of the format `'name'`
    crates_found: List[Tuple[str, str]]
    crates_not_found: List[str]
    crates_found, crates_not_found = get_crate_lists(input_clean,
                                                     output_clean,
                                                     args.show_patch)

    found_len: int = len(crates_found)
    not_found_len: int = len(crates_not_found)

    if found_len != 0:
        # By default, remove the semver patch version number from the output

        # Format "found" crates into a newline-separated string of
        # `name = "version"`
        found_formatted: str = '\n'.join(f'{name} = "{version}"'
                for name, version in crates_found)

        print(found_formatted)

    # Print a list of "not found" crates in alphabetical order
    if not_found_len != 0:
        crates_not_found.sort()
        not_found_formatted: str = '\n'.join(crates_not_found)

        if found_len != 0:
            sep = '\n'
        else:
            sep = ''

        print(f"{sep}These were not found on crates.io:\n{not_found_formatted}", file=stderr)
