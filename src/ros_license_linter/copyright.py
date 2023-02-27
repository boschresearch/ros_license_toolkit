# Copyright (c) 2023 - for information on the respective copyright owner
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

"""Assemble copyright notices for a package."""

import os
import re
from typing import Any, Dict, List, Set, Tuple, Union

from scancode.api import get_copyrights

from ros_license_linter.license_tag import LicenseTag
from ros_license_linter.package import Package


def _get_copyright_strs_from_results(
        scan_results: Dict[str, Any]) -> List[str]:
    """Get copyright strings from scan results."""
    cprs = []
    for cpr in scan_results['copyrights']:
        cprs.append(cpr['copyright'])
    return cprs


def _get_year_from_copyright_str(cpr_str: str) -> Union[int, Tuple[int, int]]:
    """Get the year from a copyright string."""
    finds = re.findall(r"\d{4}", cpr_str)
    if len(finds) == 1:
        return int(finds[0])
    elif len(finds) == 2:
        return (int(finds[0]), int(finds[1]))
    else:
        raise ValueError("Unexpected number of digits in year")


class CopyrightPerFile:
    """A copyright notice for a single file."""

    def __init__(self, file_path: str, copyright_text: str):
        self.file_path = file_path
        self.copyright_text = copyright_text


class Copyright:

    def __init__(self, pkg: Package):
        self.pkg = pkg
        # one section per license tag
        # each section is a list of unique copyright lines
        self.copyright_sections: Dict[str, Set[CopyrightPerFile]] = {}
        for license_tag in self.pkg.license_tags.values():  # type: LicenseTag
            self.copyright_sections[license_tag.source_files_str] = set()
            for source_file in license_tag.source_files:
                fpath = os.path.join(self.pkg.abspath, source_file)
                res = get_copyrights(fpath)
                if len(res) == 0:
                    continue
                for cpr in _get_copyright_strs_from_results(res):
                    self.copyright_sections[license_tag.source_files_str].add(
                        CopyrightPerFile(source_file, cpr))

    def __str__(self):
        """Get a string representation of the copyright notice."""
        cpr_str = ""
        for files_str, cprs in self.copyright_sections.items():
            cpr_str += f"{files_str}:\n"
            for cpr in cprs:
                cpr_str += f"  {cpr.copyright_text}\n"
        return cpr_str
