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

"""This Module contains LicenseTextExistsCheck, which implements Check."""

import os
from typing import Any, Dict, Optional

from ros_license_toolkit.checks import Check, Status
from ros_license_toolkit.common import get_spdx_license_name
from ros_license_toolkit.license_tag import LicenseTag, is_license_name_in_spdx_list
from ros_license_toolkit.package import Package
from ros_license_toolkit.ui_elements import red


class LicenseTextExistsCheck(Check):
    """This ensures that the license text file referenced by the tag exists."""

    def __init__(self: "LicenseTextExistsCheck"):
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
        """checks each license tag for the corresponding license text. Also
        detects unofficial licenses when tag is not in the SPDX license list"""
        self.found_license_texts = package.found_license_texts
        for license_tag in package.license_tags.values():
            if not license_tag.has_license_text_file():
                self.license_tags_without_license_text[license_tag] = (
                    "No license text file defined."
                )
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            license_text_file = license_tag.get_license_text_file()
            if not os.path.exists(os.path.join(package.abspath, license_text_file)):
                self.license_tags_without_license_text[license_tag] = (
                    f"License text file '{license_text_file}' does not exist."
                )
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if license_text_file not in self.found_license_texts:
                self.license_tags_without_license_text[license_tag] = (
                    f"License text file '{license_text_file}' not included" + " in scan results."
                )
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if not get_spdx_license_name(self.found_license_texts[license_text_file]):
                self.license_tags_without_license_text[license_tag] = (
                    f"License text file '{license_text_file}' is not "
                    + "recognized as license text."
                )
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            actual_license: Optional[str] = get_spdx_license_name(
                self.found_license_texts[license_text_file]
            )
            if actual_license is None:
                self.license_tags_without_license_text[license_tag] = (
                    f"License text file '{license_text_file}'"
                    + " is not recognized as license text."
                )
                self.missing_license_texts_status[license_tag] = Status.FAILURE
                continue
            if actual_license != license_tag.get_license_id():
                self.license_tags_without_license_text[license_tag] = (
                    f"License text file '{license_text_file}' is "
                    + f"of license {actual_license} but tag is "
                    + f"{license_tag.get_license_id()}."
                )
                # If Tag and File both are in SPDX but don't match -> Error
                if is_license_name_in_spdx_list(license_tag.get_license_id()):
                    self.missing_license_texts_status[license_tag] = Status.FAILURE
                else:
                    self.missing_license_texts_status[license_tag] = Status.WARNING
                self.files_with_wrong_tags[license_tag] = {
                    "actual_license": actual_license,
                    "license_tag": license_tag.get_license_id(),
                }
                continue

    def _evaluate_results(self):
        if len(self.license_tags_without_license_text) > 0:
            if max(self.missing_license_texts_status.values()) == Status.WARNING:
                self._warning(
                    "Since they are not in the SPDX list, "
                    "we can not check if these tags have the correct "
                    "license text:\n"
                    + "\n".join(
                        [
                            f"  '{x[0]}': {x[1]}"
                            for x in self.license_tags_without_license_text.items()
                        ]
                    )
                )
            else:
                self._failed(
                    "The following license tags do not "
                    "have a valid license text "
                    "file:\n"
                    + "\n".join(
                        [
                            f"  '{x[0]}': {x[1]}"
                            for x in self.license_tags_without_license_text.items()
                        ]
                    )
                )
            self.verbose_output = red(
                "\n".join([f"  '{x[0]}': {x[1]}" for x in self.found_license_texts.items()])
            )
        else:
            self._success("All license tags have a valid license text file.")
