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
from typing import Any, Dict, List

from scancode.api import get_copyrights


def _get_copyright_strs_from_results(
        scan_results: Dict[str, Any]) -> List[str]:
    """Get copyright strings from scan results."""
    return [cpr['copyright'] for cpr in scan_results['copyrights']]


def _clean_copyright_text(copyright_text: str):
    for prefix_to_remove in [
        'copyright (c) ',
        'copyright (c)',
        'copyright ',
        'copyright',
    ]:
        if copyright_text.lower().startswith(prefix_to_remove):
            copyright_text = copyright_text[len(prefix_to_remove):]
            break
    return copyright_text


def get_copyright_strings_per_pkg(pkg) -> Dict[str, List[str]]:
    """Get a dictionary of license keys and their respective notices."""
    copyright_strings: Dict[str, List[str]] = {}
    for key, license_tag in pkg.license_tags.items():
        cprs = set()
        for source_file in license_tag.source_files:
            fpath = os.path.join(pkg.abspath, source_file)
            res = get_copyrights(fpath)
            if len(res) == 0:
                continue
            for cpr in _get_copyright_strs_from_results(res):
                cprs.add(_clean_copyright_text(cpr))
        copyright_strings[key] = sorted(list(cprs))
    return copyright_strings
