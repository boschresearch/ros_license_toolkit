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

"""This module tests different test packages."""

import os
import subprocess
from test.systemtest._test_helpers import make_repo
from test.systemtest._test_helpers import remove_repo
import unittest

from ros_license_linter.main import main


class TestPkgs(unittest.TestCase):
    """Test different test packages."""

    def test_deep_package_folder(self):
        """Call the linter on directories in three levels.
        Check that it has found the package that is multiple levels deep."""
        repo_path = "test/_test_data/test_deep_package_folder"
        make_repo(repo_path)
        for call_path in [
                "test/_test_data/test_deep_package_folder",
                "test/_test_data/test_deep_package_folder/deeper",
                "test/_test_data/test_deep_package_folder/deeper/test_pkg_deep"
        ]:
            with subprocess.Popen(
                ["bin/ros_license_linter", call_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process:
                stdout, _ = process.communicate()
            self.assertEqual(os.EX_DATAERR, process.returncode)
            self.assertIn(
                b"test_pkg_deep", stdout)
        remove_repo(repo_path)

    def test_pkg_has_code_disjoint(self):
        """Test on a package with two disjoint sets of source files under
        a license different from the package main license."""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/test_pkg_has_code_disjoint"]))

    def test_pkg_has_code_of_different_license(self):
        """Test on a package with source files under a license different
        from the package main license (here LGPL). It should fail, because
        the additional license is not declared in the package.xml."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_has_code_of_different_license"]))

    def test_pkg_has_code_of_different_license_and_tag(self):
        """Test on a package with source files under a license different
        from the package main license, but the additional license is declared
        in the package.xml."""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/"
                "test_pkg_has_code_of_different_license_and_tag"]))

    def test_pkg_has_code_of_different_license_and_wrong_tag(self):
        """Test on a package with source files under a license different
        from the package main license, but the additional license is declared
        in the package.xml, but with the wrong name."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/"
             "test_pkg_has_code_of_different_license_and_wrong_tag"]))

    def test_pkg_no_license(self):
        """Test on a package with no license declared in the package.xml."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_no_license"]))

    def test_pkg_no_license_file(self):
        """Test on a package with no license text file."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_no_license_file"]))

    def test_pkg_spdx_name(self):
        """Test on a package with a license declared in the package.xml
        with the SPDX name."""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/test_pkg_spdx_name"]))

    def test_pkg_spdx_tag(self):
        """Test on a package with a license declared in the package.xml
        with the SPDX tag."""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/test_pkg_spdx_tag"]))

    def test_pkg_unknown_license(self):
        """Test on a package with an unknown license declared in the
        package.xml."""
        # using subprocess.Popen instead of main() to capture stdout
        with subprocess.Popen(
            ["bin/ros_license_linter",
             "test/_test_data/test_pkg_unknown_license"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            stdout, _ = process.communicate()
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertIn(b'not in SPDX list of licenses', stdout)
        self.assertIn(b'my own fancy license 1.0', stdout)

    def test_pkg_with_license_and_file(self):
        """Test on a package with a license declared in the package.xml
        and a matching license text file."""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/test_pkg_with_license_and_file"]))

    def test_pkg_with_multiple_licenses_no_source_files_tag(self):
        """Test on a package with multiple licenses declared in the
        package.xml, none of which have source file tags."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/"
             "test_pkg_with_multiple_licenses_no_source_files_tag"]))

    def test_pkg_wrong_license_file(self):
        """Test on a package with a license text file that does not match
        the license declared in the package.xml."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_wrong_license_file"]))


if __name__ == '__main__':
    unittest.main()
