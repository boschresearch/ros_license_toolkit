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

"""This Module contains LicenseFilesReferencedCheck, which implements Check"""

import os
from typing import Dict, List

from ros_license_toolkit.checks import Check
from ros_license_toolkit.package import Package


class LicenseFilesReferencedCheck(Check):
    """Check if all found License file have a reference in package.xml."""

    def __init__(self: "LicenseFilesReferencedCheck"):
        Check.__init__(self)
        self.not_covered_texts: Dict[str, str] = {}
        self.inofficial_covered_texts: Dict[str, List[str]] = {}

    def _check(self, package: Package):
        for filename, license_text in package.found_license_texts.items():
            # skipping all declarations above the package
            if not is_in_package(package, filename):
                continue
            self._handle_inofficial_licenses(package, filename, license_text)
        self._evaluate_results()

    def _handle_inofficial_licenses(self, package: Package, filename, license_text):
        if (
            "detected_license_expression_spdx" in license_text
            and license_text["detected_license_expression_spdx"] not in package.license_tags
        ):
            spdx_expression = license_text["detected_license_expression_spdx"]
            inofficial_licenses = {
                lic_tag.id_from_license_text: key
                for key, lic_tag in package.license_tags.items()
                if lic_tag.id_from_license_text != ""
            }
            if spdx_expression in inofficial_licenses:
                self.inofficial_covered_texts[filename] = [
                    spdx_expression,
                    inofficial_licenses[spdx_expression],
                ]
            else:
                self.not_covered_texts[filename] = spdx_expression

    def _evaluate_results(self):
        if self.not_covered_texts:
            info_str = ""
            info_str += (
                "The following license files are not"
                + " mentioned by any tag:\n"
                + "\n".join([f"  '{x[0]}' is of {x[1]}." for x in self.not_covered_texts.items()])
            )
            self._failed(info_str)
        elif self.inofficial_covered_texts:
            info_str = ""
            info_str += (
                "The following license files are not"
                + " mentioned by any tag:\n"
                + "\n".join(
                    [
                        f"  '{x[0]}' is of {x[1][0]} but its tag is {x[1][1]}."
                        for x in self.inofficial_covered_texts.items()
                    ]
                )
            )
            self._warning(info_str)
        else:
            self._success("All license declaration are referenced by a tag.")


def is_in_package(package: Package, file: str) -> bool:
    """Return TRUE if the file is underneath the absolute package path.
    Return FALSE if file is located above package."""
    parent = os.path.abspath(package.abspath)
    child = os.path.abspath(package.abspath + "/" + file)

    comm_parent = os.path.commonpath([parent])
    comm_child_parent = os.path.commonpath([parent, child])
    return comm_parent == comm_child_parent
