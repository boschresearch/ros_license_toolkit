
import os
import xml.etree.ElementTree as ET
from glob import glob
from typing import List, Optional


class LicenseTag(object):
    """A license tag found in a package.xml file."""

    def __init__(self, element: ET.Element, pkg_path: str):
        """Initialize a license tag from an XML element."""
        self.element = element
        assert self.element.text is not None, "License tag must have text."

        # Name of the license (presumably in SPDX format)
        self.license_id = element.text  # TODO: make sure this is SPDX

        # Path to the file containing the license text (relative to package root)
        self.license_text_file: Optional[str] = element.attrib.get(
            "file", None)

        # Paths to the source files that are licensed under this license
        self.source_files: Optional[List[str]] = None
        source_files_str = element.attrib.get("source-files", None)
        if source_files_str == "*":
            # We will handle this case later (see `make_this_the_main_license`)
            source_files_str = None
        if source_files_str is not None:
            self.source_files = []
            for src_glob in source_files_str.split(" "):
                _source_files = glob(os.path.join(
                    pkg_path, src_glob), recursive=True)
                for sf in _source_files:
                    self.source_files.append(os.path.relpath(sf, pkg_path))

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
