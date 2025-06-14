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
Module containing the LicenseTag class and related functions to handle
license tags in package.xml files.
"""

import json
import os
import xml.etree.ElementTree as ET
from glob import glob
from typing import Any, Dict, List, Optional, Set

import requests  # type: ignore[import-untyped]


def is_license_name_in_spdx_list(license_name: str) -> bool:
    """Check if a license name is in the SPDX list of licenses."""
    cache_dir: str = os.path.expanduser("~/.cache/ros_license_toolkit")
    os.makedirs(cache_dir, exist_ok=True)
    license_file = os.path.join(cache_dir, "spdx_list.txt")

    if not os.path.exists(license_file):
        url = "https://spdx.org/licenses/licenses.json"
        response = requests.get(url, timeout=100)
        if response is not None and response.status_code == 200:
            parsed_response = response.json()
            spdx_list = [
                x["licenseId"]
                for x in parsed_response["licenses"]
                if x["isDeprecatedLicenseId"] is False
            ]
            with open(license_file, "w", encoding="utf-8") as f:
                json.dump(spdx_list, f)
    else:
        with open(license_file, "r", encoding="utf-8") as f:
            spdx_list = json.load(f)
    return license_name in spdx_list


def _eval_glob(glob_str: str, pkg_path: str) -> Set[str]:
    """Evaluate a glob string and return a set of matching relative paths."""
    return {
        os.path.relpath(fpath, pkg_path)
        for fpath in glob(os.path.join(pkg_path, glob_str), recursive=True)
        if os.path.isfile(fpath)
    }


class LicenseTag:
    """A license tag found in a package.xml file."""

    def __init__(
        self,
        element: ET.Element,
        pkg_path: str,
        license_file_scan_results: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a license tag from an XML element."""
        self.element = element
        assert self.element.text is not None, "License tag must have text."

        # Name of the license (in SPDX tag format for comparability)
        raw_license_name: str = str(self.element.text)

        # If the tag is wrong (like BSD) but the actual license can
        # be found out through declaration, this field contains the tag
        self.id_from_license_text: Optional[str] = None

        # If the license name is not in the SPDX list,
        # we assume it is a custom license and use the name as-is.
        # This will be detected in `LicenseTagIsInSpdxListCheck`.
        self.id = raw_license_name
        # If a file is linked to the tag, set its id for internal checks
        if license_file_scan_results:
            self.id_from_license_text = get_id_from_license_text(license_file_scan_results)

        # Path to the file containing the license text
        # (relative to package root)
        self.license_text_file: Optional[str] = element.attrib.get("file", None)

        # Paths to the source files that are licensed under this license
        self._source_files: Optional[Set[str]] = None
        self.source_files_str: str = element.attrib.get("source-files", "")
        if not self.source_files_str:
            # If no source-files attribute is given, assume all files
            # are licensed under this license.
            self.source_files_str = "**"
        else:
            self._source_files = set()
            for src_glob in self.source_files_str.split(" "):
                self._source_files.update(_eval_glob(src_glob, pkg_path))

        # Path of package file this is in
        self.package_path: str = pkg_path

    def __str__(self) -> str:
        """Return a string representation of this license tag."""
        assert self.id is not None, "License must have a name."
        return self.id

    def has_license_text_file(self) -> bool:
        """Return whether this license tag has a file attribute."""
        return self.license_text_file is not None

    def has_source_files(self) -> bool:
        """Return whether this license tag has a source-files attribute."""
        return self._source_files is not None

    def get_license_id(self) -> str:
        """Return the license name."""
        assert self.id is not None, "License tag must have an id."
        return self.id

    def get_license_text_file(self) -> str:
        """Return the file attribute."""
        assert self.license_text_file is not None, "License tag must have file attribute."
        return self.license_text_file

    @property
    def source_files(self) -> Set[str]:
        """Return the source-files attribute."""
        assert self._source_files is not None, "License tag must have source-files attribute."
        return self._source_files

    def make_this_the_main_license(self, other_licenses: List["LicenseTag"]):
        """Make this the main license for the package."""
        assert not self.has_source_files(), "This must not have a source-files, yet."
        assert self.source_files_str == "**", "This must have a source-files attribute of '**'."
        source_files = _eval_glob(self.source_files_str, self.package_path)
        for other_license in other_licenses:
            if other_license == self:
                continue
            source_files -= other_license.source_files
        self._source_files = source_files


def get_id_from_license_text(license_file_scan_result: Dict[str, Any]) -> str:
    """Return the detected license id from the license declaration"""
    if "detected_license_expression_spdx" in license_file_scan_result:
        return license_file_scan_result["detected_license_expression_spdx"]
    return ""
