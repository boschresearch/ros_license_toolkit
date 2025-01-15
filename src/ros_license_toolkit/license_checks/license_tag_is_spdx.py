# Copyright (c) 2024 - for information on the respective copyright owner
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

"""This Module contains LicenseTagIsInSpdxListCheck, which implements Check."""

from ros_license_toolkit.checks import Check
from ros_license_toolkit.license_tag import is_license_name_in_spdx_list
from ros_license_toolkit.package import Package


class LicenseTagIsInSpdxListCheck(Check):
    """This ensures that the license tag is in the SPDX list of licenses."""

    def _check(self, package: Package):
        licenses_not_in_spdx_list = []
        for license_tag in package.license_tags.keys():
            if not is_license_name_in_spdx_list(license_tag):
                licenses_not_in_spdx_list.append(license_tag)
        if len(licenses_not_in_spdx_list) > 0:
            self._warning(
                f"Licenses {licenses_not_in_spdx_list} are "
                "not in SPDX list of licenses. "
                "Make sure to exactly match one of https://spdx.org/licenses/."
            )
        else:
            self._success("All license tags are in SPDX list of licenses.")
