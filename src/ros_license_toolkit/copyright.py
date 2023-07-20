# Copyright (c) 2023 - for information on the respective copyright owner
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

"""Assemble copyright notices for a package."""

import os
import re
from typing import Any, Dict, List, Tuple, Union

from scancode.api import get_copyrights


def _get_copyright_strs_from_results(
        scan_results: Dict[str, Any]) -> List[str]:
    """Get copyright strings from scan results."""
    return [cpr['copyright'] for cpr in scan_results['copyrights']]


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
        for prefix_to_remove in [
            'copyright',
            'Copyright (c) ',
            'Copyright ',
            'Copyright'
        ]:
            if copyright_text.startswith(prefix_to_remove):
                copyright_text = copyright_text[len(prefix_to_remove):]
                break
        self.copyright_text = copyright_text

    def __str__(self):
        return self.copyright_text


class CopyrightPerPkg:
    def __init__(self, pkg):
        self.pkg = pkg
        # one section per license tag
        # each section is a list of unique copyright lines
        self.copyright_strings: Dict[str, List[str]] = {}
        for key, license_tag in self.pkg.license_tags.items():
            cprs = set()
            for source_file in license_tag.source_files:
                fpath = os.path.join(self.pkg.abspath, source_file)
                res = get_copyrights(fpath)
                if len(res) == 0:
                    continue
                for cpr in _get_copyright_strs_from_results(res):
                    cprs.add(CopyrightPerFile(source_file, cpr))
            self.copyright_strings[key] = sorted(
                {cpr.copyright_text for cpr in cprs})

    def __str__(self):
        return " ".join(" ".join(copyrights)
                        for copyrights in self.copyright_strings.values())
