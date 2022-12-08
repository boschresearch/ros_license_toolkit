# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/boschresearch/ros_license_linter

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys
import timeit
from typing import Optional, Sequence

from ros_license_linter.checks import (LicensesInCodeCheck,
                                       LicenseTagExistsCheck,
                                       LicenseTagIsInSpdxListCheck,
                                       LicenseTextExistsCheck)
from ros_license_linter.package import get_packages_in_path
from ros_license_linter.ui_elements import (FAILURE_STR, SUCCESS_STR,
                                            Verbosity, green, major_sep,
                                            minor_sep, red, rll_print_factory)


def main(args: Sequence[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description='Checks ROS packages for correct license declaration.')
    parser.add_argument(
        'path',
        default='.',
        help='path to ROS2 package or repo containing packages')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        default=False, help='enable verbose output')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        default=False, help='disable most output')
    parsed_args = parser.parse_args(args)

    # Determine the verbosity level
    if parsed_args.quiet:
        verbosity = Verbosity.QUIET
    elif parsed_args.verbose:
        verbosity = Verbosity.VERBOSE
    else:
        verbosity = Verbosity.NORMAL
    rll_print = rll_print_factory(verbosity)

    # Sanity check the path
    assert isinstance(parsed_args.path, str)
    assert os.path.exists(
        parsed_args.path), f'Path {parsed_args.path} does not exist.'

    # Get the packages in the path
    packages = get_packages_in_path(parsed_args.path)
    if not packages:
        rll_print(f'No packages found in {parsed_args.path}', Verbosity.QUIET)
        return os.EX_USAGE
    rll_print(
        f'Found {len(packages)} packages in {parsed_args.path}',
        Verbosity.QUIET)
    rll_print(
        f' Packages: {", ".join([p.name for p in packages])}',
        Verbosity.VERBOSE)
    rll_print(major_sep())

    # lets time the execution
    start = timeit.default_timer()

    # Check the packages
    results_per_package = {}
    for package in packages:
        rll_print(f'[{package.name}]')
        rll_print(f'git hash of ({package.repo}): {package.git_hash}')
        checks_to_perform = [
            LicenseTagExistsCheck(),
            LicenseTagIsInSpdxListCheck(),
            LicenseTextExistsCheck(),
            LicensesInCodeCheck()]

        for check in checks_to_perform:
            check.check(package)
            rll_print(check)
            rll_print(check.verbose(), Verbosity.VERBOSE)

        if all(checks_to_perform):
            rll_print(minor_sep())
            rll_print(f"[{package.name}] Overall:"+green(f"\n {SUCCESS_STR}"))
            rll_print(major_sep())
            results_per_package[package.abspath] = True
        else:
            rll_print(minor_sep())
            rll_print(f"[{package.name}] Overall:"+red(f"\n {FAILURE_STR}"))
            rll_print(major_sep())
            results_per_package[package.abspath] = False

    stop = timeit.default_timer()
    rll_print(f'Execution time: {stop - start:.2f} seconds', Verbosity.QUIET)

    # Print the overall results
    if all(results_per_package.values()):
        rll_print("All packages:"+green(f"\n {SUCCESS_STR}"), Verbosity.QUIET)
        return os.EX_OK
    else:
        rll_print("All packages:"+red(f"\n {FAILURE_STR}"), Verbosity.QUIET)
        return os.EX_DATAERR
