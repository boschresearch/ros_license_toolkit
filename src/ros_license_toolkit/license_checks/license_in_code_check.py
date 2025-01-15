# Copyright (c) 2024 - for information on the respective copyright owner
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

"""This Module contains LicensesInCodeCheck, which implements Check"""

from pprint import pformat
from typing import Dict, List

from ros_license_toolkit.checks import Check
from ros_license_toolkit.license_tag import LicenseTag
from ros_license_toolkit.package import Package
from ros_license_toolkit.ui_elements import red


class LicensesInCodeCheck(Check):
    """Check if all found licenses have a declaration in the package.xml."""

    def __init__(self: "LicensesInCodeCheck"):
        Check.__init__(self)
        self.declared_licenses: Dict[str, LicenseTag] = {}
        self.files_with_uncovered_licenses: Dict[str, List[str]] = {}
        self.files_not_matched_by_any_license_tag: Dict[str, List[str]] = {}
        self.files_with_unofficial_tag: Dict[str, List[str]] = {}

    def _check(self, package: Package):
        if len(package.license_tags) == 0:
            self._failed("No license tag defined.")
            return
        self.declared_licenses = package.license_tags
        self._check_license_files(package)
        self._evaluate_result(package)

    def _check_license_files(self, package: Package) -> None:
        for fname, found_licenses in package.found_files_w_licenses.items():
            if fname in package.get_license_files():
                # the actual license text files are not relevant for this
                continue
            found_licenses_str = found_licenses["detected_license_expression_spdx"]
            if not found_licenses_str:
                continue
            licenses = found_licenses_str.split(" AND ")
            for license_str in licenses:
                if license_str not in self.declared_licenses:
                    # this license has an unofficial tag
                    unofficial_licenses = {
                        lic_tag.id_from_license_text: key
                        for key, lic_tag in package.license_tags.items()
                        if lic_tag.id_from_license_text != ""
                    }
                    if license_str in unofficial_licenses.keys():
                        if fname not in self.files_with_unofficial_tag:
                            self.files_with_unofficial_tag[fname] = []
                        self.files_with_unofficial_tag[fname].append(license_str)
                        self.files_with_unofficial_tag[fname].append(
                            unofficial_licenses[license_str]
                        )
                        continue
                    # this license is not declared by any license tag
                    if fname not in self.files_with_uncovered_licenses:
                        self.files_with_uncovered_licenses[fname] = []
                    self.files_with_uncovered_licenses[fname].append(license_str)
                    continue
                if fname not in self.declared_licenses[license_str].source_files:
                    # this license is declared by a license tag but the file
                    # is not listed in the source files of the license tag
                    if fname not in self.files_not_matched_by_any_license_tag:
                        self.files_not_matched_by_any_license_tag[fname] = []
                    self.files_not_matched_by_any_license_tag[fname].append(license_str)
                    continue

    def _evaluate_result(self, package: Package) -> None:
        if self.files_with_uncovered_licenses:
            info_str = ""
            info_str += (
                "\nThe following files contain licenses that "
                + "are not covered by any license tag:\n"
                + "\n".join(
                    [f"  '{x[0]}': {x[1]}" for x in self.files_with_uncovered_licenses.items()]
                )
            )
            self._print_info(
                info_str,
                self.files_with_uncovered_licenses,
                self.files_not_matched_by_any_license_tag,
                package,
            )
        elif self.files_with_unofficial_tag:
            info_str = ""
            info_str += (
                "For the following files, please change the "
                + "License Tag in the package file to SPDX format:\n"
                + "\n".join(
                    [
                        f"  '{x[0]}' is of {x[1][0]} but its Tag is {x[1][1]}."
                        for x in self.files_with_unofficial_tag.items()
                    ]
                )
            )
            self._warning(info_str)
        elif len(self.files_not_matched_by_any_license_tag) > 0:
            info_str = ""
            info_str += (
                "\nThe following files contain licenses that "
                + "are covered by a license tag but are not listed in "
                + "the source files of the license tag:\n"
                + "\n".join(
                    [
                        f"  '{x[0]}': {x[1]}"
                        for x in self.files_not_matched_by_any_license_tag.items()
                    ]
                )
            )
            self._print_info(
                info_str,
                self.files_with_uncovered_licenses,
                self.files_not_matched_by_any_license_tag,
                package,
            )
        else:
            self._success("All licenses found in the code are covered by a license declaration.")

    def _print_info(
        self,
        info_str,
        files_with_uncovered_licenses,
        files_not_matched_by_any_license_tag,
        package,
    ):
        assert info_str != ""
        self._failed(info_str)
        self.verbose_output = red(
            "\n  Relevant scan results:\n"
            + pformat(
                list(
                    filter(
                        lambda x: x[0] in files_with_uncovered_licenses
                        or (x[0] in files_not_matched_by_any_license_tag),
                        package.found_files_w_licenses.items(),
                    )
                )
            )
        )
