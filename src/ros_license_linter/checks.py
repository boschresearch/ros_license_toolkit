# Copyright (c) 2022 - for information on the respective copyright owner
# see the NOTICE file and/or the repository https://github.com/boschresearch/ros_license_linter

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import xml.etree.ElementTree as ET
from pprint import pformat
from typing import Dict, List, Optional

from spdx.config import LICENSE_MAP

from ros_license_linter.license_tag import LicenseTag
from ros_license_linter.package import (Package, PackageException,
                                        get_spdx_license_name,
                                        is_license_text_file)
from ros_license_linter.ui_elements import NO_REASON_STR, green, red


def is_license_name_in_spdx_list(license_name: str) -> bool:
    """Check if a license name is in the SPDX list of licenses."""
    return license_name in LICENSE_MAP


class Check(object):
    def __init__(self):
        # overall success of this check
        self.success: bool = False

        # explanation for success or failure for normal output
        self.reason: str = NO_REASON_STR

        # string with additional information for verbose output
        self.verbose_output: str = ""

    def _failed(self, r: str):
        """Set this check as failed for reason `r`."""
        self.success = False
        self.reason = r

    def _success(self, r: str):
        """Set this check as successful for reason `r`."""
        self.success = True
        if self.reason == NO_REASON_STR:
            self.reason = ""
        else:
            self.reason += "\n "
        self.reason += r

    def __str__(self) -> str:
        """Return formatted string for normal output."""
        if self.success:
            return str(
                type(self).__name__) + "\n" + \
                green(f" SUCCESS {self.reason}")
        else:
            return str(
                type(self).__name__) + "\n" + \
                red(f" FAILURE {self.reason}")

    def verbose(self) -> str:
        """Return string with additional information for verbose output."""
        return self.verbose_output

    def __bool__(self) -> bool:
        """Evaluate success of check as bool"""
        return self.success

    def check(self, package: Package):
        """Check `package` and set success and reason."""
        try:
            self._check(package)
        except PackageException as e:
            self._failed(f"Exception: {e}")
            return

    def _check(self, package: Package):
        """Check `package`."""
        raise NotImplementedError("Overwrite this")


class LicenseTagExistsCheck(Check):
    """This check ensures that the xml tag defining the license exists in the
    package.xml."""

    def _check(self, package: Package):
        if len(package.get_license_tags()) == 0:
            self._failed("No license tag defined.")
            self.verbose_output = red(str(package.package_xml))
            return
        else:
            self._success(
                f"Found licenses {list(map(str, package.get_license_tags()))}")


class LicenseTagIsInSpdxListCheck(Check):
    """This check ensures that the license tag is in the SPDX list of
    licenses."""

    def _check(self, package: Package):
        licenses_not_in_spdx_list = []
        for license_tag in package.get_license_tags().keys():
            if not is_license_name_in_spdx_list(
                    license_tag):
                licenses_not_in_spdx_list.append(license_tag)
        if len(licenses_not_in_spdx_list) > 0:
            self._failed(
                f"Licenses {licenses_not_in_spdx_list} are "
                "not in SPDX list of licenses."
            )
        else:
            self._success("All license tags are in SPDX list of licenses.")


class LicenseTextExistsCheck(Check):
    """This check ensures that the license text file that the license tag
    references exists."""

    def _check(self, package: Package):
        if len(package.get_license_tags()) == 0:
            self._failed("No license tag defined.")
            return
        license_tags_without_license_text: Dict[LicenseTag, str] = {}
        _, found_license_texts = package.get_scan_results()
        for license_tag in package.get_license_tags().values():
            if not license_tag.has_license_text_file():
                license_tags_without_license_text[
                    license_tag] = "No license text file defined."
                continue
            license_text_file = license_tag.get_license_text_file()
            if not os.path.exists(
                    os.path.join(package.abspath, license_text_file)):
                license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' does not exist."
                continue
            if license_text_file not in found_license_texts:
                license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' not included" +\
                    " in scan results."
                continue
            if not is_license_text_file(
                    found_license_texts[license_text_file]):
                license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' is not " +\
                    "recognized as license text."
                continue
            actual_license: Optional[str] = get_spdx_license_name(
                found_license_texts[license_text_file])
            if actual_license is None:
                license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}'" +\
                    " is not recognized as license text."
                continue
            if actual_license != license_tag.get_license_id():
                license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' is" +\
                    "of license {actual_license} but should be" +\
                    f"{license_tag.get_license_id()}."
                continue
        if len(license_tags_without_license_text) > 0:
            self._failed(
                "The following license tags do not have a valid license text "
                "file:\n" + "\n".join(
                    map(lambda x: f"  '{x[0]}': {x[1]}",
                        license_tags_without_license_text.items())))
            self.verbose_output = red(
                "\n".join(map(lambda x: f"  '{x[0]}': {x[1]}",
                              found_license_texts.items())))

        else:
            self._success("All license tags have a valid license text file.")


class LicensesInCodeCheck(Check):
    """This checks if all licenses found in the code are covered by a license
    declaration in the package.xml."""

    def _check(self, package: Package):
        if len(package.get_license_tags()) == 0:
            self._failed("No license tag defined.")
            return
        declared_licenses = package.get_license_tags()
        files_with_uncovered_licenses: Dict[str, List[str]] = {}
        files_not_matched_by_any_license_tag: Dict[str, List[str]] = {}

        found_files_w_licenses, _ = package.get_scan_results()
        for fname, found_licenses in found_files_w_licenses.items():
            if fname in package.get_license_files():
                # the actual license text files are not relevant for this
                continue
            for found_license in found_licenses['licenses']:
                found_license_str = found_license['spdx_license_key']
                if found_license_str not in declared_licenses:
                    # this license is not declared by any license tag
                    if fname not in files_with_uncovered_licenses:
                        files_with_uncovered_licenses[fname] = []
                    files_with_uncovered_licenses[fname].append(
                        found_license_str)
                    continue
                elif fname not in declared_licenses[
                        found_license_str].get_source_files():
                    # this license is declared by a license tag but the file
                    # is not listed in the source files of the license tag
                    if fname not in files_not_matched_by_any_license_tag:
                        files_not_matched_by_any_license_tag[fname] = []
                    files_not_matched_by_any_license_tag[fname].append(
                        found_license_str)
                    continue
        if len(files_with_uncovered_licenses) > 0 or \
                len(files_not_matched_by_any_license_tag) > 0:
            info_str = ""
            if len(files_with_uncovered_licenses) > 0:
                info_str += "\nThe following files contain licenses that " +\
                    "are not covered by any license tag:\n" + "\n".join(
                        map(lambda x: f"  '{x[0]}': {x[1]}",
                            files_with_uncovered_licenses.items()))
            elif len(files_not_matched_by_any_license_tag) > 0:
                info_str += "\nThe following files contain licenses that " +\
                    "are covered by a license tag but are not listed in the" +\
                    "a source files of the license tag:\n" + "\n".join(
                        map(lambda x: f"  '{x[0]}': {x[1]}",
                            files_not_matched_by_any_license_tag.items()))
            assert info_str != ""
            self._failed(info_str)
            self.verbose_output = red(
                "\n  Relevant scan results:\n" +
                pformat(list(filter(
                    lambda x: x[0] in files_with_uncovered_licenses
                    or x[0] in files_not_matched_by_any_license_tag,
                    found_files_w_licenses.items()))))

        else:
            self._success("All licenses found in the code are covered by a "
                          "license declaration.")
