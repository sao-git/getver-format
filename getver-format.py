#!/usr/bin/env python3
import subprocess
import sys
import re

# Expects `getver` to be in $PATH or %PATH%
# TODO:
#       Add command line option to pass in path to `getver`
command = ["getver"] + sys.argv[1:]
getver_proc = subprocess.run(args = command, capture_output = True, text = True)

#print(sys.argv)
#print(getver_proc)

# Clean ANSI color codes from the input for easier formatting
# https://stackoverflow.com/a/14693789
output_clean = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', getver_proc.stdout)

# Change from 'crate: version' to 'crate = "version"' for use in `Cargo.toml`
output_format = re.sub(r': (?P<rest>.*)\n', r' = "\g<rest>"\n', output_clean)
print(output_format, end = '')
