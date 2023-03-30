# Copyright (c) 2022 - see the NOTICE file in root or repo


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
This module contains the Package class.
"""

import os
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from rospkg import list_by_path
from rospkg import RosPack
from rospkg.common import PACKAGE_FILE
from scancode.api import get_licenses

from ros_license_toolkit.common import is_license_text_file
from ros_license_toolkit.license_tag import LicenseTag
from ros_license_toolkit.repo import NotARepoError
from ros_license_toolkit.repo import Repo

# files we ignore in scan results
IGNORED_FILES = [
    "package.xml",
    "setup.py",
    "setup.cfg",
    "CMakeLists.txt"
]


def get_spdx_license_name(scan_results: Dict[str, Any]) -> Optional[str]:
    """Get the SPDX license name from scan results."""
    for _license in scan_results["licenses"]:
        if _license["score"] >= 99:
            return _license["spdx_license_key"]
    return None


class PackageException(Exception):
    """Exception raised when a package is invalid."""


class MoreThanOneLicenseWithoutSourceFilesTag(PackageException):
    """Exception raised when a package has more than one license tag without
    source files."""


class MoreThanOneLicenseWithoutLicenseTextFile(PackageException):
    """Exception raised when a package has more than one license tag without
    a license text file."""


class Package:
    """This represents a ros package, defined by its `path` (absolute) and
    results within it."""

    def __init__(self, path: str, repo: Optional[Repo] = None):
        # absolute path to this package
        self.abspath: str = path

        # relative path to the parent repo, if any
        self.repo: Optional[Repo] = repo

        # name of this package by its folder name
        self.name: str = os.path.basename(self.abspath)

        # Files found by scanner that contain license information
        # this is Optional, because it is only evaluated on the first call
        self._found_files_w_licenses: Optional[Dict[str, Any]] = None

        # Files that are found to contain license texts
        # this is Optional, because it is only evaluated on the first call
        self._found_license_texts: Optional[Dict[str, Any]] = None

        # The xml tree of the package.xml file
        # this is Optional, because it is only evaluated on the first call
        self._package_xml: Optional[ET.ElementTree] = None

        # The license tags found in the package.xml file
        # this is Optional, because it is only evaluated on the first call
        self._license_tags: Optional[Dict[str, LicenseTag]] = None

    def _get_path_relative_to_pkg(self, path: str) -> str:
        """Get path relative to pkg root"""
        return os.path.relpath(path, self.abspath)

    @property
    def found_files_w_licenses(self) -> Dict[str, Any]:
        """Get a dict of files in the package and their license scan results.
        Note that the code is only evaluated on the first call."""
        if self._found_files_w_licenses is None:
            self._run_scan_and_save_results()
        assert self._found_files_w_licenses is not None
        return self._found_files_w_licenses

    @property
    def found_license_texts(self) -> Dict[str, Any]:
        """Get a dict of files in the package and their license scan results.
        Note that the code is only evaluated on the first call."""
        if self._found_license_texts is None:
            self._run_scan_and_save_results()
        assert self._found_license_texts is not None
        return self._found_license_texts

    def _run_scan_and_save_results(self):
        """Get a dict of files in the package and their license scan results.
        Note that the code is only evaluated on the first call."""
        if not (self._found_files_w_licenses is None or (
                self._found_license_texts is None)):
            return self._found_files_w_licenses, self._found_license_texts
        self._found_files_w_licenses = {}
        self._found_license_texts = {}
        for (root, _, files) in os.walk(self.abspath):
            for fname in files:
                if fname in IGNORED_FILES:
                    continue
                # Path relative to cwd
                fpath = os.path.join(root, fname)
                # Path relative to package root
                fpath_rel_to_pkg = self._get_path_relative_to_pkg(fpath)
                scan_results = get_licenses(fpath)
                if is_license_text_file(scan_results):
                    self._found_license_texts[fpath_rel_to_pkg
                                              ] = scan_results
                else:
                    # not a license text file but also interesting
                    self._found_files_w_licenses[fpath_rel_to_pkg
                                                 ] = scan_results
        # look also in the repo for license text files
        if self.repo is not None:
            for path, res in self.repo.license_text_files.items():
                self._found_license_texts[
                    self._get_path_relative_to_pkg(path)] = res

    @property
    def package_xml(self):
        """Get xml of `package.xml` as `ElementTree` object."""
        if self._package_xml is None:
            self._package_xml = ET.parse(
                os.path.join(self.abspath, 'package.xml'))
        return self._package_xml

    @property
    def license_tags(self) -> Dict[str, LicenseTag]:
        """Get all license tags in the package.xml file."""
        if self._license_tags is not None:
            return self._license_tags
        self._license_tags = {}
        for license_tag in self.package_xml.iterfind('license'):
            tag = LicenseTag(license_tag, self.abspath)
            self._license_tags[tag.get_license_id()] = tag

        # One license tag can have no source-files attribute.
        # But there can be only one such tag.
        # This is then the main license.
        if len(list(filter(lambda x: not x.has_source_files(),
                           self._license_tags.values()))) > 1:
            raise MoreThanOneLicenseWithoutSourceFilesTag(
                "There must be at most one license tag without "
                "source-files.")
        for tag in self._license_tags.values():
            if not tag.has_source_files():
                tag.make_this_the_main_license(
                    list(self._license_tags.values()))
                break

        # One license tag can have no file attribute, but only one.
        # It may be associated to a license text file in the package or
        # the repo.
        if len(list(filter(lambda x: not x.has_license_text_file(),
                           self._license_tags.values()))) > 1:
            raise MoreThanOneLicenseWithoutLicenseTextFile(
                "There must be at most one license tag without "
                "a license text file.")
        for tag in self._license_tags.values():
            if not tag.has_license_text_file():
                license_texts = self.found_license_texts
                if len(license_texts) == 1:
                    tag.license_text_file = list(license_texts.keys())[0]
                else:
                    for license_text_file in license_texts:
                        if "LICENSE" in license_text_file:
                            tag.license_text_file = license_text_file
                            break
                break

        return self._license_tags

    def get_license_files(self) -> List[str]:
        """Get all license text files associated with license tags
        in the package.xml."""
        return [x.get_license_text_file() for x in
                self.license_tags.values()]


def get_packages_in_path(path: str) -> List[Package]:
    """Get all ROS packages in a given path."""
    packages = []
    try:
        repo: Optional[Repo] = Repo(os.path.abspath(path))
    except NotARepoError:
        repo = None
    for pkg in list_by_path(PACKAGE_FILE, path, {}):
        ros_pkg = RosPack([path]).get_path(pkg)
        packages.append(Package(ros_pkg, repo))
    return packages