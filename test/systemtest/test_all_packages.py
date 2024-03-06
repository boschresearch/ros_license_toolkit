# Copyright (c) 2022 - for information on the respective copyright owner
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

"""
This module tests the linter on all packages in the test directory.
"""

import os
import subprocess
import unittest


class TestAllPackages(unittest.TestCase):
    """Test the linter on all packages in the test directory."""

    def test_all(self):
        """Call the linter on the whole test directory.
        Check that the output contains all package names.
        """
        with subprocess.Popen(
            ["ros_license_toolkit", "test/_test_data"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            stdout, stderr = process.communicate()
        self.assertNotEqual(os.EX_OK, process.returncode)
        print(stdout)
        print(stderr)
        self.assertIn(b"test_pkg_deep", stdout)
        self.assertIn(b"test_pkg_both_tags_not_spdx", stdout)
        self.assertIn(b"test_pkg_has_code_disjoint", stdout)
        self.assertIn(b"test_pkg_has_code_of_different", stdout)
        self.assertIn(b"test_pkg_has_code_of_different_license", stdout)
        self.assertIn(
            b"test_pkg_has_code_of_different_license_and_tag", stdout)
        self.assertIn(
            b"test_pkg_has_code_of_different_license_and_wrong_tag", stdout)
        self.assertIn(b"test_pkg_name_not_in_spdx", stdout)
        self.assertIn(b"test_pkg_no_file_attribute", stdout)
        self.assertIn(b"test_pkg_no_license", stdout)
        self.assertIn(b"test_pkg_no_license_file", stdout)
        self.assertIn(b"test_pkg_one_correct_one_license_file_missing", stdout)
        self.assertIn(b"test_pkg_spdx_name", stdout)
        self.assertIn(b"test_pkg_spdx_tag", stdout)
        self.assertIn(b"test_pkg_unknown_license", stdout)
        self.assertIn(b"test_pkg_unknown_license_missing_file", stdout)
        self.assertIn(b"test_pkg_with_license_and_file", stdout)
        self.assertIn(
            b"test_pkg_with_multiple_licenses_no_source_files_tag", stdout)
        self.assertIn(
            b"test_pkg_with_multiple_licenses_one_referenced_incorrect",
            stdout)
        self.assertIn(b"test_pkg_wrong_license_file", stdout)
        self.assertIn(b"pkg_with_bsd3_a", stdout)
        self.assertIn(b"pkg_with_bsd3_b", stdout)
        self.assertIn(b"pkg_with_mit_a", stdout)
        self.assertIn(b"pkg_with_mit_b", stdout)


if __name__ == '__main__':
    unittest.main()
