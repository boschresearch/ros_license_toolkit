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

"""
Module containing the LicenseTag class and related functions to handle
license tags in package.xml files.
"""

import os
import xml.etree.ElementTree as ET
from glob import glob
from typing import List, Optional

from spdx.config import LICENSE_MAP


def is_license_name_in_spdx_list(license_name: str) -> bool:
    """Check if a license name is in the SPDX list of licenses."""
    return license_name in LICENSE_MAP or \
        license_name in LICENSE_MAP.values()


def to_spdx_license_tag(license_name: str) -> str:
    """Convert a license name to a SPDX license tag
    (assuming it is shorter than the name).
    This is because the dict from spdx.config.LICENSE_MAP
    contains both pairings (tag, name) and (name, tag).
    """
    for tag, name in LICENSE_MAP.items():
        if license_name in [tag, name]:
            if len(tag) < len(name):
                return tag
            # else
            return name
    raise ValueError("License name not in SPDX list.")


class LicenseTag:
    """A license tag found in a package.xml file."""

    def __init__(self, element: ET.Element, pkg_path: str):
        """Initialize a license tag from an XML element."""
        self.element = element
        assert self.element.text is not None, "License tag must have text."

        raw_license_name: str = str(self.element.text)
        # Name of the license (in SPDX tag format for comparability)
        try:
            self.license_id = to_spdx_license_tag(raw_license_name)
        except ValueError:
            # If the license name is not in the SPDX list,
            # we assume it is a custom license and use the name as-is.
            # This will be detected in `LicenseTagIsInSpdxListCheck`.
            self.license_id = raw_license_name

        # Path to the file containing the license text
        # (relative to package root)
        self.license_text_file: Optional[str] = element.attrib.get(
            "file", None)

        # Paths to the source files that are licensed under this license
        self.source_files: Optional[List[str]] = None
        self.source_files_str = element.attrib.get("source-files", None)
        if self.source_files_str == "*" or self.source_files_str is None:
            # We will handle this case later (see `make_this_the_main_license`)
            self.source_files_str = None
        if self.source_files_str is not None:
            self.source_files = []
            for src_glob in self.source_files_str.split(" "):
                _source_files = glob(os.path.join(
                    pkg_path, src_glob), recursive=True)
                for _source_file in _source_files:
                    self.source_files.append(
                        os.path.relpath(_source_file, pkg_path))

        # Path of package file this is in
        self.package_path: str = pkg_path

    def __str__(self) -> str:
        """Return a string representation of this license tag."""
        assert self.license_id is not None, "License must have a name."
        return self.license_id

    def has_license_text_file(self) -> bool:
        """Return whether this license tag has a file attribute."""
        return self.license_text_file is not None

    def has_source_files(self) -> bool:
        """Return whether this license tag has a source-files attribute."""
        return self.source_files is not None

    def get_license_id(self) -> str:
        """Return the license name."""
        assert self.license_id is not None, "License tag must have an id."
        return self.license_id

    def get_license_text_file(self) -> str:
        """Return the file attribute."""
        assert self.license_text_file is not None, \
            "License tag must have file attribute."
        return self.license_text_file

    def get_source_files(self) -> List[str]:
        """Return the source-files attribute."""
        assert self.source_files is not None, \
            "License tag must have source-files attribute."
        return self.source_files

    def make_this_the_main_license(self, other_licenses: List["LicenseTag"]):
        """Make this the main license for the package."""
        assert not self.has_source_files(), \
            "This must not have a source-files, yet."
        source_files = set(
            map(lambda x: os.path.relpath(x, self.package_path), glob(
                os.path.join(self.package_path, "**"), recursive=True)))
        for other_license in other_licenses:
            if other_license == self:
                continue
            source_files -= set(other_license.get_source_files())
        self.source_files = list(source_files)
