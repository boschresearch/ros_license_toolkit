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

"""This module contains the checks for the linter."""

import os
from enum import IntEnum
from typing import Any, Dict, Optional

from ros_license_toolkit.common import get_spdx_license_name
from ros_license_toolkit.license_tag import (LicenseTag,
                                             is_license_name_in_spdx_list)
from ros_license_toolkit.package import Package, PackageException
from ros_license_toolkit.ui_elements import NO_REASON_STR, green, red, yellow


class Status(IntEnum):
    """Levels of success or failure for the output"""
    SUCCESS = 0
    WARNING = 1
    FAILURE = 2


class Check:
    """Base class for checks."""

    def __init__(self: 'Check'):
        """Initialize a check."""
        # overall success of this check
        self.status: Status = Status.FAILURE

        # explanation for success or failure for normal output
        self.reason: str = NO_REASON_STR

        # string with additional information for verbose output
        self.verbose_output: str = ''

    def _failed(self, reason: str):
        """Set this check as failed for `reason`."""
        self.status = Status.FAILURE
        self.reason = reason

    def _warning(self, reason: str):
        """Set this check as passed but display a warning for reason `r`."""
        self.status = Status.WARNING
        self.reason = reason

    def _success(self, reason: str):
        """Set this check as successful for reason `r`."""
        self.status = Status.SUCCESS
        if self.reason == NO_REASON_STR:
            self.reason = ''
        else:
            self.reason += "\n "
        self.reason += reason

    def __str__(self) -> str:
        """Return formatted string for normal output."""
        info: str = str(type(self).__name__) + "\n"
        if self.status == Status.SUCCESS:
            info += green(f" SUCCESS {self.reason}")
        elif self.status == Status.WARNING:
            info += yellow(f" WARNING {self.reason}")
        else:
            info += red(f" FAILURE {self.reason}")
        return info

    def verbose(self) -> str:
        """Return string with additional information for verbose output."""
        return self.verbose_output

    def __bool__(self) -> bool:
        """Evaluate success of check as bool. Warning is treated as success"""
        return self.status != Status.FAILURE

    def get_status(self) -> Status:
        """Get the level of success to also consider possible warnings"""
        return self.status

    def check(self, package: Package):
        """
        Check `package` and set success and reason.

        Calls `_check` internally. If they raise an exception, this is
        caught and the check is set to failed.
        """
        try:
            self._check(package)
        except PackageException as ex:
            self._failed(f"PackageException: {ex}")
            return
        except AssertionError as ex:
            self._failed(f"AssertionError: {ex}")
            return

    def _check(self, package: Package):
        """Check `package`. To be overwritten by subclasses."""
        raise NotImplementedError("Overwrite this")


class LicenseTagExistsCheck(Check):
    """This ensures that a tag defining the license exists."""

    def _check(self, package: Package):
        if len(package.license_tags) == 0:
            self._failed("No license tag defined.")
            self.verbose_output = red(str(package.package_xml))
        else:
            self._success(
                f"Found licenses {list(map(str, package.license_tags))}")


class LicenseTagIsInSpdxListCheck(Check):
    """This ensures that the license tag is in the SPDX list of licenses."""

    def _check(self, package: Package):
        licenses_not_in_spdx_list = []
        for license_tag in package.license_tags.keys():
            if not is_license_name_in_spdx_list(
                    license_tag):
                licenses_not_in_spdx_list.append(license_tag)
        if len(licenses_not_in_spdx_list) > 0:
            self._warning(
                f"Licenses {licenses_not_in_spdx_list} are "
                "not in SPDX list of licenses. "
                "Make sure to exactly match one of https://spdx.org/licenses/."
            )
        else:
            self._success("All license tags are in SPDX list of licenses.")


class LicenseTextExistsCheck(Check):
    """This ensures that the license text file referenced by the tag exists."""

    def __init__(self: 'LicenseTextExistsCheck'):
        Check.__init__(self)
        self.license_tags_without_license_text: Dict[LicenseTag, str] = {}
        self.missing_license_texts_status: Dict[LicenseTag, Status] = {}
        self.files_with_wrong_tags: Dict[LicenseTag, Dict[str, str]] = {}
        self.found_license_texts: Dict[str, Any] = {}

    def _check(self, package: Package):
        if len(package.license_tags) == 0:
            self._failed("No license tag defined.")
            return

        self._check_licenses(package)
        self._evaluate_results()

    def _check_licenses(self, package: Package) -> None:
        '''checks each license tag for the corresponding license text. Also
        detects inofficial licenses when tag is not in the SPDX license list'''
        self.found_license_texts = package.found_license_texts
        for license_tag in package.license_tags.values():
            if not license_tag.has_license_text_file():
                self.license_tags_without_license_text[
                    license_tag] = "No license text file defined."
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            license_text_file = license_tag.get_license_text_file()
            if not os.path.exists(
                    os.path.join(package.abspath, license_text_file)):
                self.license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' does not exist."
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if license_text_file not in self.found_license_texts:
                self.license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' not included" +\
                    " in scan results."
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if not get_spdx_license_name(
                    self.found_license_texts[license_text_file]):
                self.license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' is not " +\
                    "recognized as license text."
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            actual_license: Optional[str] = get_spdx_license_name(
                self.found_license_texts[license_text_file])
            if actual_license is None:
                self.license_tags_without_license_text[
                    license_tag
                ] = f"License text file '{license_text_file}'" +\
                    " is not recognized as license text."
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if actual_license != license_tag.get_license_id():
                self.license_tags_without_license_text[license_tag] =\
                    f"License text file '{license_text_file}' is " +\
                    f"of license {actual_license} but tag is " +\
                    f"{license_tag.get_license_id()}."
                # If Tag and File both are in SPDX but don't match -> Error
                if is_license_name_in_spdx_list(license_tag.get_license_id()):
                    self.missing_license_texts_status[license_tag] =\
                        Status.FAILURE
                else:
                    self.missing_license_texts_status[license_tag] =\
                        Status.WARNING
                self.files_with_wrong_tags[license_tag] = \
                    {'actual_license': actual_license,
                        'license_tag': license_tag.get_license_id()}
                continue

    def _evaluate_results(self):
        if len(self.license_tags_without_license_text) > 0:
            if max(self.missing_license_texts_status.values()) \
               == Status.WARNING:
                self._warning(
                    "Since they are not in the SPDX list, "
                    "we can not check if these tags have the correct "
                    "license text:\n" + "\n".join(
                        [f"  '{x[0]}': {x[1]}" for x in
                            self.license_tags_without_license_text.items()]))
            else:
                self._failed(
                    "The following license tags do not "
                    "have a valid license text "
                    "file:\n" + "\n".join(
                        [f"  '{x[0]}': {x[1]}" for x in
                            self.license_tags_without_license_text.items()]))
            self.verbose_output = red(
                "\n".join([f"  '{x[0]}': {x[1]}" for x in
                           self.found_license_texts.items()]))
        else:
            self._success("All license tags have a valid license text file.")
