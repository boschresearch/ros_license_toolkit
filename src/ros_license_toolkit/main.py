# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository
# https://github.com/boschresearch/ros_license_toolkit

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module containing the entry point for the ros_license_toolkit CLI.
"""

import argparse
import os
import sys
import timeit
from typing import Optional, Sequence

from ros_license_toolkit.checks import Status
from ros_license_toolkit.license_checks.license_file_referenced_check import \
    LicenseFilesReferencedCheck
from ros_license_toolkit.license_checks.license_in_code_check import \
    LicensesInCodeCheck
from ros_license_toolkit.license_checks.license_tag_exists_check import \
    LicenseTagExistsCheck
from ros_license_toolkit.license_checks.license_tag_is_spdx import \
    LicenseTagIsInSpdxListCheck
from ros_license_toolkit.license_checks.license_text_exists_check import \
    LicenseTextExistsCheck
from ros_license_toolkit.license_checks.schema_check import SchemaCheck
from ros_license_toolkit.package import get_packages_in_path
from ros_license_toolkit.ui_elements import (FAILURE_STR, SUCCESS_STR,
                                             WARNING_STR, Verbosity, major_sep,
                                             minor_sep, red, rll_print_factory)


def main(args: Optional[Sequence[str]] = None) -> int:
    """Main entry point for the ros_license_toolkit CLI.

    :param args: the command line arguments, defaults to sys.argv[1:]
    :type args: Sequence[str], optional
    :return: the exit code, `os.EX_OK` if all checks passed, `os.EX_USAGE` if
        no packages were found, `os.EX_DATAERR` if any check failed
    :rtype: int
    """
    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description='Checks ROS packages for correct license declaration.')
    parser.add_argument(
        'path', default='.',
        help='path to ROS2 package or repo containing packages')
    parser.add_argument(
        '-c', '--generate_copyright_file', action='store_true',
        default=False, help='generate a copyright file')
    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        default=False, help='enable verbose output')
    parser.add_argument(
        '-q', '--quiet', dest='quiet', action='store_true',
        default=False, help='disable most output')
    parser.add_argument(
        '-e', '--continue_on_error', action='store_true',
        default=False, help='treats all errors as warnings, i.e. will give'
        + 'returncode 0 even on errors')
    parser.add_argument(
        '-w', '--warnings_as_error', action='store_true',
        default=False, help='treats all warnings as errors')
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
        results_per_package.update(
            process_one_pkg(rll_print, package))

    if parsed_args.generate_copyright_file:
        if max(results_per_package.values()) != Status.FAILURE:
            generate_copyright_file(packages, rll_print)
        else:
            rll_print(red(
                "Copyright file will not be generated "
                + "because there were linter errors."),
                Verbosity.QUIET)

    stop = timeit.default_timer()
    rll_print(f'Execution time: {stop - start:.2f} seconds', Verbosity.QUIET)

    # Print the overall results
    return print_results(results_per_package, rll_print, parsed_args)


def generate_copyright_file(packages, rll_print):
    """Generate copyright file. In case more than one package
    is provided, display error message."""
    if len(packages) == 1:
        package = packages[0]
        try:
            package.write_copyright_file(
                os.path.join(os.getcwd(), 'copyright'))
        except AssertionError as error:
            rll_print(red(str(error)))
    else:
        rll_print(red(
            "Can only generate copyright file for single package"),
            Verbosity.QUIET)


def print_results(result, rll_print, args):
    """Printing the result of package"""
    if max(result.values()) == Status.SUCCESS:
        rll_print(f"All packages:\n {SUCCESS_STR}", Verbosity.QUIET)
        return os.EX_OK

    if max(result.values()) == Status.WARNING:
        if args.warnings_as_error:
            rll_print(f"All packages:\n {FAILURE_STR} "
                      + "(Treating warnings as failure)", Verbosity.QUIET)
            return os.EX_DATAERR
        rll_print(f"All packages:\n {WARNING_STR}", Verbosity.QUIET)
        return os.EX_OK

    if args.continue_on_error:  # Error is Warning, still displayed red
        rll_print(f"All packages:\n {WARNING_STR} "
                  + "(Treating errors as warnings)", Verbosity.QUIET)
        return os.EX_OK
    rll_print(f"All packages:\n {FAILURE_STR}", Verbosity.QUIET)
    return os.EX_DATAERR


def process_one_pkg(rll_print, package):
    """Perform checks on one package, print results and return them."""
    results_per_package = {}
    rll_print(f'[{package.name}]')
    assert package.repo is not None, 'Package must be in a git repo.'
    rll_print(
        f'git hash of ({package.repo.get_path()}):'
        f' {package.repo.get_hash()}')
    checks_to_perform = [
        SchemaCheck(),
        LicenseTagExistsCheck(),
        LicenseTagIsInSpdxListCheck(),
        LicenseTextExistsCheck(),
        LicensesInCodeCheck(),
        LicenseFilesReferencedCheck()]

    for check in checks_to_perform:
        check.check(package)
        rll_print(check)
        rll_print(check.verbose(), Verbosity.VERBOSE)

    rll_print(minor_sep())
    # Every check is successful, no warning
    if max(check.status for check in checks_to_perform) == Status.SUCCESS:
        rll_print(f"[{package.name}] Overall:\n {SUCCESS_STR}")
        results_per_package[package.abspath] = Status.SUCCESS
    # Either every check is successful or contains a warning
    elif max(check.status for check in checks_to_perform) == Status.WARNING:
        rll_print(f"[{package.name}] Overall:\n {WARNING_STR}")
        results_per_package[package.abspath] = Status.WARNING
    # At least one check contains an error
    else:
        rll_print(f"[{package.name}] Overall:\n {FAILURE_STR}")
        results_per_package[package.abspath] = Status.FAILURE
    rll_print(major_sep())
    return results_per_package


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
