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
System tests to make sure that the license per repo is detected correctly.
"""

import os
import subprocess
import unittest
from test.systemtest._test_helpers import make_repo, remove_repo


class TestLicensePerRepoBsd3(unittest.TestCase):
    """Test that the license per repo is detected correctly.
    Here a repo folder has a license text with subfolders that are packages
    using that license."""

    def _test_repo(self, repo_name, pkg_names, license_name):
        """Test that the license per repo is detected correctly.

        :param repo_name: name of the test repo folder
        :type repo_name: str
        :param pkg_names: list of package names to expect in the folder
        :type pkg_names: List[str]
        :param license_name: name of the license to expect
        :type license_name: str
        """
        # make actual git repo
        repo_path = os.path.join("test", "_test_data", repo_name)
        make_repo(repo_path)
        # test
        with subprocess.Popen(
            ["ros_license_toolkit", repo_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            stdout, stderr = process.communicate()
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertEqual(b'', stderr)
        self.assertIn(license_name.encode(), stdout)
        for pkg_name in pkg_names:
            self.assertIn(pkg_name.encode(), stdout)
        # clean up
        remove_repo(repo_path)

    def test_license_text_in_repo_bsd3(self):
        """Testing with BSD-3-Clause license text."""
        self._test_repo(
            "test_repo_bsd3",
            ["pkg_with_bsd3_a", "pkg_with_bsd3_b"],
            "BSD-3-Clause"
        )

    def test_license_text_in_repo_mit(self):
        """Testing with MIT license text."""
        self._test_repo(
            "test_repo_mit",
            ["pkg_with_mit_a", "pkg_with_mit_b"],
            "MIT"
        )


if __name__ == '__main__':
    unittest.main()
