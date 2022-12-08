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

import os
import shutil
import subprocess
import unittest

import git


class TestLicensePerRepoBsd3(unittest.TestCase):
    """Test that the license per repo is detected correctly.
    Here a repo folder has a license text with subfolders that are packages
    using that license."""

    def test_license_text_in_repo_bsd3(self):
        # make actual git repo
        r = git.Repo.init("test/test_repo_bsd3")
        r.index.add(["LICENSE"])
        r.index.commit("initial commit")
        # test
        process = subprocess.Popen(
            ["bin/ros_license_linter", "test/test_repo_bsd3"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertEqual(b'', stderr)
        self.assertIn(b'BSD-3-Clause', stdout)
        self.assertIn(b'pkg_with_bsd3_a', stdout)
        self.assertIn(b'pkg_with_bsd3_b', stdout)
        # clean up
        shutil.rmtree("test/test_repo_bsd3/.git")


if __name__ == '__main__':
    unittest.main()
