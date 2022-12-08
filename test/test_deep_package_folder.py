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
import subprocess
import unittest

from ros_license_linter.main import main


class TestAllPackages(unittest.TestCase):

    def test_failure(self):
        """Call the linter on directories in two levels.
        Check that it has found the package that was two levels deep.
        """
        for call_path in "test", "test/test_deep_package_folder":
            process = subprocess.Popen(
                ["bin/ros_license_linter", call_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate()
            self.assertEqual(os.EX_DATAERR, process.returncode)
            self.assertIn(
                b"test_pkg_deep", stdout)


if __name__ == '__main__':
    unittest.main()
