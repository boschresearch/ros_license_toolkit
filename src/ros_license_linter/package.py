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

import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

import git
from rospkg import RosPack, list_by_path
from rospkg.common import PACKAGE_FILE
from scancode.api import get_licenses

from ros_license_linter.license_tag import LicenseTag

# files we ignore in scan results
IGNORED_FILES = [
    "package.xml",
    "setup.py",
    "setup.cfg",
    "CMakeLists.txt"
]

# how many folders up to search for a repo
REPO_SEARCH_DEPTH = 2


def is_git_repo(path: str) -> bool:
    """Check if a path is a git repo."""
    return os.path.isdir(os.path.join(path, ".git"))


def is_license_text_file(scan_results: Dict[str, Any]) -> bool:
    """Check if a file is a license text file."""
    for license in scan_results["licenses"]:
        if license["matched_rule"]["is_license_text"] and \
                license["score"] >= 99:
            return True
    return False


def get_spdx_license_name(scan_results: Dict[str, Any]) -> Optional[str]:
    """Get the SPDX license name from scan results."""
    for license in scan_results["licenses"]:
        if license["score"] >= 99:
            return license["spdx_license_key"]
    return None


class PackageException(Exception):
    """Exception raised when a package is invalid."""
    pass


class MoreThanOneLicenseWithoutSourceFilesTag(PackageException):
    """Exception raised when a package has more than one license tag without
    source files."""
    pass


class MoreThanOneLicenseWithoutLicenseTextFile(PackageException):
    """Exception raised when a package has more than one license tag without
    a license text file."""
    pass


class Package(object):
    """This represents a ros package, defined by its `path` (absolute) and
    results within it."""

    def __init__(self, path: str):
        # absolute path to this package
        self.abspath: str = path

        # relative path to the parent repo, if any
        self.repo: Optional[str] = None
        search_path = path
        for _ in range(REPO_SEARCH_DEPTH + 1):
            if is_git_repo(search_path):
                self.repo = os.path.relpath(search_path, self.abspath)
                break
            search_path = os.path.dirname(search_path)

        # (for logging purposes) the current git hash
        self.git_hash: Optional[str] = None
        if self.repo is not None:
            repo = git.Repo(os.path.join(self.abspath, self.repo))
            self.git_hash = repo.head.object.hexsha

        # name of this package by its folder name
        self.name: str = os.path.basename(self.abspath)

        # Files found by scanner that contain license information
        # this is Optional, because it is only evaluated on the first call
        self.found_files_w_licenses: Optional[Dict[str, Any]] = None

        # Files that are found to contain license texts
        # this is Optional, because it is only evaluated on the first call
        self.found_license_texts: Optional[Dict[str, Any]] = None

        # The xml tree of the package.xml file
        # this is Optional, because it is only evaluated on the first call
        self.package_xml: Optional[ET.ElementTree] = None

        # The license tags found in the package.xml file
        # this is Optional, because it is only evaluated on the first call
        self.license_tags: Optional[Dict[str, LicenseTag]] = None

    def _get_path_relative_to_pkg(self, p: str) -> str:
        """Get path relative to pkg root"""
        return os.path.relpath(p, self.abspath)

    def get_scan_results(self):
        """Get a dict of files in the package and their license scan results.
        Note that the code is only evaluated on the first call."""
        if (self.found_files_w_licenses is None or
                self.found_license_texts is None):
            self.found_files_w_licenses = {}
            self.found_license_texts = {}
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
                        self.found_license_texts[fpath_rel_to_pkg
                                                 ] = scan_results
                    else:
                        # not a license text file but also interesting
                        self.found_files_w_licenses[fpath_rel_to_pkg
                                                    ] = scan_results
            # look also in the repo for license text files
            if self.repo is not None:
                for file in os.listdir(os.path.join(self.abspath, self.repo)):
                    fpath = os.path.join(self.abspath, self.repo, file)
                    if not os.path.isfile(fpath):
                        continue
                    scan_results = get_licenses(fpath)
                    if is_license_text_file(scan_results):
                        self.found_license_texts[os.path.join(
                            self.repo, file)] = scan_results
            # pprint.pprint(self.licenses)
        return self.found_files_w_licenses, self.found_license_texts

    def _get_package_xml(self):
        """Get xml of `package.xml` as `ElementTree` object."""
        if self.package_xml is None:
            self.package_xml = ET.parse(
                os.path.join(self.abspath, 'package.xml'))
        return self.package_xml

    def get_license_tags(self) -> Dict[str, LicenseTag]:
        """Get all license tags in the package.xml file."""
        if self.license_tags is None:
            self.license_tags = {}
            for license_tag in self._get_package_xml().iterfind('license'):
                li = LicenseTag(license_tag, self.abspath)
                self.license_tags[li.get_license_id()] = li

            # One license tag can have no source-files attribute, but only one.
            # This is then the main license.
            if len(list(filter(lambda x: not x.has_source_files(),
                               self.license_tags.values()))) > 1:
                raise MoreThanOneLicenseWithoutSourceFilesTag(
                    "There must be at most one license tag without "
                    + "source-files.")
            for li in self.license_tags.values():
                if not li.has_source_files():
                    li.make_this_the_main_license(
                        list(self.license_tags.values()))
                    break

            # One license tag can have no file attribute, but only one.
            # It may be associated to a license text file in the package or
            # the repo.
            if len(list(filter(lambda x: not x.has_license_text_file(),
                               self.license_tags.values()))) > 1:
                raise MoreThanOneLicenseWithoutLicenseTextFile(
                    "There must be at most one license tag without "
                    + "a license text file.")
            for li in self.license_tags.values():
                if not li.has_license_text_file():
                    _, license_texts = self.get_scan_results()
                    if len(license_texts) == 1:
                        li.license_text_file = list(license_texts.keys())[0]
                    else:
                        for license_text_file in license_texts.keys():
                            if "LICENSE" in license_text_file:
                                li.license_text_file = license_text_file
                                break
                    break

        return self.license_tags

    def get_license_files(self) -> List[str]:
        """Get all license text files asosiated with license tags
        in the package.xml."""
        return list(map(
            lambda x: x.get_license_text_file(),
            self.get_license_tags().values()))


def get_packages_in_path(path: str) -> List[Package]:
    """Get all ROS packages in a given path."""
    packages = []
    for pkg in list_by_path(PACKAGE_FILE, path, {}):
        ros_pkg = RosPack([path]).get_path(pkg)
        packages.append(Package(ros_pkg))
    return packages
