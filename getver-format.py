#!/usr/bin/env python3

__title__ = 'getver-format'
__version__ = '0.5.0'
__license__ = 'MIT'
__desc__ = (
    'Formatter for copying latest versions of Rust crates to a Cargo manifest, using "getver" crate version fetcher')
__url__ = 'https://github.com/sao-git/getver-format'


import subprocess
from os import environ
from sys import stderr, exit
import re
import argparse
from collections import OrderedDict
from typing import List, Tuple, Dict, Iterable, Any, Pattern, Optional, Sequence, Match


def parse_args() -> argparse.Namespace:
    """ Set up, and return the results of, the argument parser. """

    ver_string = f'%(prog)s {__version__}'
    desc = ver_string + '\nPrint a list of the latest Rust crate versions from crates.io'

    parser = argparse.ArgumentParser(add_help=True,
                                     prog=__title__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=desc)

    parser.add_argument('-V', '--version',
                        action='version',
                        version=ver_string,
                        help='print the program version')

    parser.add_argument('crates',
                        metavar='CRATE',
                        type=str,
                        nargs='+',
                        help='a list of Cargo crates')

    parser.add_argument('-g', '--getver-path',
                        metavar='PATH',
                        dest='getver_path',
                        default=None,
                        help='path to getver')

    parser.add_argument('-p', '--show-patch',
                        dest='show_patch',
                        action='store_true',
                        help='show semver patch versions')

    parser.add_argument('-n', '--no-missing-crates',
                        dest='hide_missing',
                        action='store_true',
                        help='do not show missing crates in the output')

    parser.add_argument('-a', '--sort-alphabet',
                        dest='sort_alpha',
                        action='store_true',
                        help='sort the list of crates alphabetically')


    return parser.parse_args()


def get_crate_lists(input_clean: Dict[str, Any],
                    output_clean: str,
                    sort_alpha: bool,
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

    # Make a list out of the cleaned input, one item for each line
    raw_crates: Iterable[str] = output_clean.splitlines()

    # Separate found crate strings `'name: version'` into lists `['name', 'version']`
    # Missing crate strings will not be affected
    split_crates: Iterable[List[str]]
    split_crates = (s.split(': ') for s in raw_crates)

    # For each item in `split_crates`, attempt to find missing crate strings
    # of the form `"the crate 'crate-not-found' doesn't exist"`, splitting by `'`
    #
    # If the split succeeds, add the name (index 1 of the `split()` list) to the
    # "not found" list and remove the name from the input dictionary
    #
    # If it doesn't, assume the crate was found and has a corresponding version
    # number and add the number to the corresponding dictionary entry
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


    # Create the "found" output list and format according to user preferences
    #
    # The default is to remove the SemVer patch version number from the output
    # and keep the output in the same order as the input
    crates_found_out: List[Tuple[str, str]]
    if not show_patch:
        crates_found_out = [(name, '.'.join(version.split('.')[:2]))
                for name, version in input_clean.items()]
    else:
        crates_found_out = [(name, version)
                for name, version in input_clean.items()]

    if sort_alpha:
        crates_found_out.sort(key=lambda crate: crate[0])


    return crates_found_out, crates_not_found


def check_version(path: List[str], ansi_pattern: Pattern[str]) -> str:
    """ Check for a valid version of `getver`. """

    # Strings to supply to the ValueError exception
    not_found_error = "Can't find getver at the provided path"
    version_error = "Requires getver version >= 0.1.0"

    # Pass `--help` to `getver` to get the version number
    #
    # This mutates the provided path list, so remove `--help` once the
    # subprocess exits
    path.append('--help')
    getver_version: subprocess.CompletedProcess
    getver_version = subprocess.run(args = path,
                                    capture_output = True,
                                    text = True)
    del path[-1]

    # Remove ANSI escape codes from the subprocess output, split the output
    # by lines and attempt to find the string `'getver'` in the resulting list
    potentially: Iterable[str]
    potentially = ansi_pattern.sub('', getver_version.stdout).splitlines()
    potentially = (s.strip() for s in potentially if s.find('getver') != -1)

    # If the generator is empty (meaning the string was not found in the list)
    # calling `next()` should return `None`. If not, it should return the string
    # containing `'getver'` and the version number
    getverver: Optional[str] = next(potentially, None)

    # If no string was returned (the `None` variant of the `Optional` type),
    # then abort with the Not Found error.
    #
    # Else, split the string by spaces and get the second element (index 1)
    # which should be the semantic version string. If this fails, also abort
    # with the Not Found error.
    version_string: str
    if getverver is None:
        raise ValueError(not_found_error)
    else:
        try:
            version_string = getverver.split(' ')[1]
        except IndexError:
            raise ValueError(not_found_error)


    # Match the version string against the SemVer regex from https://regexr.com/39s32
    #
    # The capture group indices are:
    #
    # 0. The whole version string
    # 1. MAJOR.MINOR.PATCH-PRE_RELEASE (what you should be evaluating for precendence)
    # 2. MAJOR
    # 3. MINOR
    # 4. PATCH
    # 5. PRERELEASE
    # 6. BUILD_METADATA
    #
    # If the match fails, it should return `None`, so abort with the Not Found error
    semver_match: Optional[Match[str]]
    semver_groups: Sequence[str]
    semver_match = re.match(r'^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$', version_string)
    if semver_match is None:
        raise ValueError(not_found_error)
    else:
        semver_groups = semver_match.groups()

    # A final `try` in case the indexing fails
    try:
        major, minor, patch = (int(s) for s in semver_groups[2:5])
    except IndexError:
        raise ValueError(not_found_error)

    # Check the version match groups for >= 0.1.0
    # If this succeeds, return the version string
    # If this fails, abort with the Wrong Version error
    #
    # Note: This is a simple check for now. It should not be interpreted
    # as a caret requirement (as in ^0.1.0)
    if major >= 0 and minor >= 1 and patch >= 0:
        return semver_groups[1]
    else:
        raise ValueError(version_error)


def get_path(args_path: Optional[str]) -> str:
    """ Determine the path to `getver` by priority. """

    # Highest priority is given to a path provided on the command line
    if args_path is not None:
        return args_path

    # Next priority is given to the `GETVER_PATH` environment variable
    environ_path: Optional[str]
    environ_path = environ.get('GETVER_PATH')
    if environ_path is not None:
        return environ_path

    # If neither are present, return the bare name. Another function
    # will test to see if it can be found in the `PATH` environment variable
    return 'getver'


if __name__ == '__main__':
    args: argparse.Namespace = parse_args()
    #print(args)

    # ANSI escape sequence regex from https://stackoverflow.com/a/14693789
    ansi_color_match: Pattern[str]
    ansi_color_match = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    # Get a path to the `getver` executable
    gv_path: str = get_path(args.getver_path)

    # Check if `getver` is in PATH or the path provided by -g
    gv_path_list: List[str] = gv_path.split(' ')
    gv_version: str
    try:
        gv_version = check_version(gv_path_list, ansi_color_match)
    except ValueError as e:
        print(f'getver-format: error: {e}', file=stderr)
        exit(1)

    # Replace underscores (U+005F) in the input list with hyphens (U+002D),
    # then remove duplicate names from the list and keep the resulting order.
    #
    # `input_clean` will be mutated in `get_crate_lists()`, which will delete
    # missing crates from the dict and append version numbers to the found keys.
    # This is safe because `input_clean` will not be used after the final
    # lists are created.
    input_clean: Dict[str, Any]
    input_clean = OrderedDict.fromkeys(s.replace('_', '-') for s in args.crates)

    # Run `getver` with the cleaned input list and capture the output
    run_command: List[str]
    run_command = gv_path_list + list(input_clean.keys())

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
                                                     args.sort_alpha,
                                                     args.show_patch)

    # These will be used to determine what to output
    found: bool = len(crates_found) != 0
    not_found: bool = len(crates_not_found) != 0

    # Print the list of "found" crates
    if found:
        # Format "found" crates into a newline-separated string of
        # `name = "version"`
        found_formatted: str = '\n'.join(f'{name} = "{version}"'
                for name, version in crates_found)

        print(found_formatted)

    # Print the list of "not found" crates to stderr in alphabetical order
    if not args.hide_missing and not_found:
        crates_not_found.sort()
        not_found_formatted: str = '\n'.join(crates_not_found)

        if found:
            sep = '\n'
        else:
            sep = ''

        print(f"{sep}These were not found on crates.io:\n{not_found_formatted}", file=stderr)
