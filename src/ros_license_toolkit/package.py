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

import fnmatch
import os
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from lxml import etree
from rospkg import RosPack, list_by_path
from rospkg.common import PACKAGE_FILE
from scancode.api import get_licenses

from ros_license_toolkit.common import get_ignored_content, get_spdx_license_name
from ros_license_toolkit.copyright import get_copyright_strings_per_pkg
from ros_license_toolkit.license_tag import LicenseTag
from ros_license_toolkit.repo import NotARepoError, Repo

INVALID = -1


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

    # pylint: disable=too-many-instance-attributes
    # Eight is reasonable in this case.

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

        # All ignored files and folders
        self._ignored_content: List[str] = get_ignored_content(self.abspath)

        # The package.xml file, parsed as etree
        self._parsed_package_xml: etree = None

        # The package.xml version as set in <package format="x">
        self._package_xml_format_ver: int = 0

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
        if (
            self._found_files_w_licenses is not None  # noqa: W504
            and self._found_license_texts is not None
        ):
            return
        self._found_files_w_licenses = {}
        self._found_license_texts = {}
        for root, _, files in os.walk(self.abspath):
            files_rel_to_pkg = [
                self._get_path_relative_to_pkg(os.path.join(root, f)) for f in files
            ]
            for pattern in self._ignored_content:
                matched = fnmatch.filter(files_rel_to_pkg, pattern)
                for m in matched:
                    files_rel_to_pkg.remove(m)
            for fname in files_rel_to_pkg:
                # Path relative to cwd
                fpath = os.path.join(self.abspath, fname)
                # Path relative to package root
                scan_results = get_licenses(fpath)
                if get_spdx_license_name(scan_results):
                    self._found_license_texts[fname] = scan_results
                else:
                    # not a license text file but also interesting
                    self._found_files_w_licenses[fname] = scan_results
        # look also in the repo for license text files
        if self.repo is not None:
            for path, res in self.repo.license_text_files.items():
                self._found_license_texts[self._get_path_relative_to_pkg(path)] = res

    @property
    def package_xml(self):
        """Get xml of `package.xml` as `ElementTree` object."""
        if self._package_xml is None:
            self._package_xml = ET.parse(os.path.join(self.abspath, "package.xml"))
        return self._package_xml

    def _check_single_license_tag_without_source_files(self):
        """One license tag can have no source-files attribute.
        But there can be only one such tag.
        This is then the main license."""
        if len(list(filter(lambda x: not x.has_source_files(), self._license_tags.values()))) > 1:
            raise MoreThanOneLicenseWithoutSourceFilesTag(
                "There must be at most one license tag without source-files."
            )
        for tag in self._license_tags.values():
            if not tag.has_source_files():
                tag.make_this_the_main_license(list(self._license_tags.values()))
                break

    def _check_single_license_tag_without_file_attribute(self):
        """One license tag can have no file attribute, but only one.
        It may be associated to a license text file in the package or
        the repo."""
        if (
            len(
                list(
                    filter(
                        lambda x: not x.has_license_text_file(),
                        self._license_tags.values(),
                    )
                )
            )
            > 1
        ):
            raise MoreThanOneLicenseWithoutLicenseTextFile(
                "There must be at most one license tag without a license text file."
            )
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
                # there was no license text found by content, but we can
                # look for some files by their name, e.g. LICENSE or COPYING
                potential_license_files = [
                    file
                    for file in os.listdir(self.abspath)
                    if "LICENSE" in file or "COPYING" in file
                ]
                # only if there is exactly one such file, we can use it
                if len(potential_license_files) == 1:
                    tag.license_text_file = potential_license_files[0]
                break

    def _check_for_single_tag_without_file(self):
        """Set the id_from_license_text if only one tag and one
        declaration exist."""
        if len(self._license_tags) == 1 and len(self.found_license_texts) == 1:
            license_tag_key = next(iter(self._license_tags.keys()))
            id_from_text = self._license_tags[license_tag_key].id_from_license_text
            if id_from_text is None:
                only_file_id = self.found_license_texts[next(iter(self.found_license_texts))][
                    "detected_license_expression_spdx"
                ]
                self._license_tags[license_tag_key].id_from_license_text = only_file_id

    @property
    def license_tags(self) -> Dict[str, LicenseTag]:
        """Get all license tags in the package.xml file."""
        if self._license_tags is not None:
            return self._license_tags
        self._license_tags = {}
        for license_tag in self.package_xml.iterfind("license"):
            license_file_scan_result = None
            if "file" in license_tag.attrib:
                license_file = license_tag.attrib["file"]
                if license_file in self.found_license_texts:
                    license_file_scan_result = self.found_license_texts[license_file]
                    license_file_scan_result["filename"] = license_file
            tag = LicenseTag(license_tag, self.abspath, license_file_scan_result)
            self._license_tags[tag.get_license_id()] = tag

        self._check_single_license_tag_without_source_files()
        self._check_single_license_tag_without_file_attribute()
        self._check_for_single_tag_without_file()

        return self._license_tags

    @property
    def package_xml_format_ver(self) -> int:
        """Returns version of package.xml format as seen in
        <package format="3">. If Version is not valid,
        INVALID (-1) is returned."""
        if self._package_xml_format_ver == 0:
            root = self.parsed_package_xml.getroot()
            if root.tag == "package":
                if "format" in root.attrib:
                    version = root.attrib["format"]
                    try:
                        self._package_xml_format_ver = int(version)
                    except ValueError:
                        self._package_xml_format_ver = INVALID
                    return self._package_xml_format_ver
            self._package_xml_format_ver = INVALID
        return self._package_xml_format_ver

    @property
    def parsed_package_xml(self) -> etree:
        """Returns the package.xml content parsed as etree."""
        if self._parsed_package_xml is None:
            path = self.abspath + "/package.xml"
            assert os.path.exists(path), f"Path {path} does not exist."
            self._parsed_package_xml = etree.parse(path)
        return self._parsed_package_xml

    @property
    def repo_url(self) -> Optional[str]:
        """Get the url of the repo this package is in if the package is in a
        git repo and this has an origin. Else return None."""
        if self.repo is None:
            return None
        return None if self.repo.remote_url is None else self.repo.remote_url

    def get_license_files(self) -> List[str]:
        """Get all license text files associated with license tags
        in the package.xml."""
        return [x.get_license_text_file() for x in self.license_tags.values()]

    def get_copyright_file_contents(self) -> str:
        """Get a string representation of the copyright notice."""
        pkg_copyright_strings = get_copyright_strings_per_pkg(self)
        cpr_str = "".join(
            (
                "Format: https://www.debian.org/doc/packaging-manuals/copyright",
                "-format/1.0/\n",
                f"Source: {self.repo_url}\n",
                f"Upstream-Name: {self.name}\n\n",
            )
        )
        for key, cprs in pkg_copyright_strings.items():
            source_files_str = self.license_tags[key].source_files_str
            cpr_str += f"Files:\n {source_files_str}\n"
            cpr_str += "Copyright: "
            cpr_str += "\n           ".join(cprs)
            pkg_license = self.license_tags[key]
            cpr_str += f"\nLicense: {pkg_license.id}\n"
            assert pkg_license.license_text_file, "License text file must be defined."
            license_path = os.path.join(self.abspath, pkg_license.license_text_file)
            if not os.path.exists(license_path):
                raise FileExistsError(
                    ("Cannot create copyright file." f"File {license_path} does not exist.")
                )
            with open(license_path, encoding="utf-8") as f:
                license_lines = f.readlines()
            for line in license_lines:
                out_line = f" {line}"
                # remove leading whitespace from empty lines
                if out_line == " \n":
                    out_line = "\n"
                cpr_str += out_line
            cpr_str += "\n"
        # remove double newlines at the end
        if cpr_str.endswith("\n\n"):
            cpr_str = cpr_str[:-1]
        return cpr_str

    def write_copyright_file(self, path: str):
        """Write the contents of the copyright notice to a file."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.get_copyright_file_contents())


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
