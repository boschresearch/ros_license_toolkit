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

from typing import Any, Dict


def is_license_text_file(scan_results: Dict[str, Any]) -> bool:
    """Check if a file is a license text file."""
    for _license in scan_results["licenses"]:
        if _license["matched_rule"]["is_license_text"] and \
                _license["score"] >= 99:
            return True
    return False
