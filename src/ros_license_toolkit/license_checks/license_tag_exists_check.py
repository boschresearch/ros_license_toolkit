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

"""This Module contains LicenseTagExistsCheck, which implements Check."""

from ros_license_toolkit.checks import Check
from ros_license_toolkit.package import Package
from ros_license_toolkit.ui_elements import red


class LicenseTagExistsCheck(Check):
    """This ensures that a tag defining the license exists."""

    def _check(self, package: Package):
        if len(package.license_tags) == 0:
            self._failed("No license tag defined.")
            self.verbose_output = red(str(package.package_xml))
        else:
            self._success(f"Found licenses {list(map(str, package.license_tags))}")
