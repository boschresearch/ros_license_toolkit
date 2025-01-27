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

"""Common utility functions."""

import os
from typing import Any, Dict, List, Optional

REQUIRED_PERCENTAGE_OF_LICENSE_TEXT = 90.0

# files we ignore in scan results
IGNORED = [
    "CHANGELOG.rst",
    ".scanignore",
    "package.xml",
    "setup.py",
    "setup.cfg",
    "CMakeLists.txt",
    ".git/*",
]


def get_spdx_license_name(scan_results: Dict[str, Any]) -> Optional[str]:
    """Get the SPDX license name from scan results."""
    if scan_results["percentage_of_license_text"] >= REQUIRED_PERCENTAGE_OF_LICENSE_TEXT:
        return scan_results["detected_license_expression_spdx"]
    return None


def get_ignored_content(pkg_abspath: str) -> List[str]:
    """Return all ignored patterns from '.scanignore'
    and local IGNORED definition."""
    ignored_content: List[str] = []
    scanignore_path = pkg_abspath + "/.scanignore"
    if os.path.exists(scanignore_path):
        with open(scanignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line_contents = line.split("#")
                ignore_pattern = line_contents[0].rstrip()
                if len(ignore_pattern) > 0:
                    ignored_content.append(ignore_pattern)
            f.close()
    for pattern in IGNORED:
        if pattern not in ignored_content:
            ignored_content.append(pattern)
    return ignored_content
