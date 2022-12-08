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

import unittest
from xml.etree import ElementTree as ET

from ros_license_linter.license_tag import (LicenseTag,
                                            is_license_name_in_spdx_list)


class TestChecks(unittest.TestCase):

    def test_is_license_name_in_spdx_list(self):
        self.assertTrue(is_license_name_in_spdx_list("Apache-2.0"))
        self.assertFalse(is_license_name_in_spdx_list("Apache-2.0-foo"))

    def test_init(self):
        by_spdx_tag = LicenseTag(ET.fromstring(
            "<license>Apache-2.0</license>"), "")
        self.assertEqual(by_spdx_tag.license_id, "Apache-2.0")
        by_spdx_name = LicenseTag(ET.fromstring(
            "<license>Apache License 2.0</license>"), "")
        self.assertEqual(by_spdx_name.license_id, "Apache-2.0")


if __name__ == '__main__':
    unittest.main()
