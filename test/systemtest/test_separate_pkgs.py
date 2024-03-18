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

"""This module tests different test packages."""

import os
import subprocess
import unittest
from test.systemtest._test_helpers import make_repo, remove_repo

from ros_license_toolkit.main import main


class TestPkgs(unittest.TestCase):
    """Test different test packages."""
    # pylint: disable=too-many-public-methods
    # Here it make sense to keep all tests in one place

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
                ["ros_license_toolkit", call_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            ) as process:
                stdout, _ = process.communicate()
            self.assertEqual(os.EX_OK, process.returncode)
            self.assertIn(
                b"test_pkg_deep", stdout)
        remove_repo(repo_path)

    def test_pkg_both_tags_not_spdx(self):
        """ Test on a package that has two different Licenses that both
        have a not SPDX conform Tag. License files and source files
        are SPDX conform"""
        self.assertEqual(os.EX_OK, main([
            "test/_test_data/test_pkg_both_tags_not_spdx"
        ]))

    def test_pkg_both_tags_not_spdx_one_file_own(self):
        """Test on a package that has two licenses. One is self-defined, other
        one with not SPDX tag but therefore code and license file in SPDX"""
        self.assertEqual(os.EX_DATAERR, main([
            "test/_test_data/test_pkg_both_tags_not_spdx_one_file_own"
        ]))

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

    def test_pkg_name_not_in_spdx(self):
        """Test on a package that has valid License file with BSD-3-Clause
        but its license tag BSD is not in SPDX format"""
        process, stdout = open_subprocess("test_pkg_name_not_in_spdx")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertIn(b"WARNING", stdout)

    def test_pkg_no_file_attribute(self):
        """Test on a package with License file that is not referenced in
        package.xml"""
        self.assertEqual(os.EX_OK, main(
            ["test/_test_data/test_pkg_no_file_attribute"]))

    def test_pkg_no_license(self):
        """Test on a package with no license declared in the package.xml."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_no_license"]))

    def test_pkg_no_license_file(self):
        """Test on a package with no license text file."""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_no_license_file"]))

    def test_pkg_one_correct_one_license_file_missing(self):
        """Test on a package that has one correct license with file
        and code, but also one not known license tag without file"""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_one_correct_one_license_file_missing"]))

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

    def test_pkg_too_many_license_files(self):
        """"Test on a package with multiple License files that are not
        declared by any tag and could therefore be removed."""
        process, stdout = open_subprocess("test_pkg_too_many_license_files")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertIn(b"WARNING", stdout)
        self.assertIn(b"bsd.LICENSE", stdout)
        self.assertIn(b"apl.LICENSE", stdout)
        self.assertNotIn(b"../../../LICENSE", stdout)

    def test_pkg_tag_not_spdx(self):
        """Test on a package that has one linked declaration, one code file
        but not in SPDX tag. Tag must be gotten from declaration."""
        process, stdout = open_subprocess("test_pkg_tag_not_spdx")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertIn(b"WARNING", stdout)
        self.assertIn(b"'code_with_afl.py' is of AFL-2.0 but its Tag is AFL.",
                      stdout)

    def test_pkg_unknown_license(self):
        """Test on a package with an unknown license declared in the
        package.xml."""
        # using subprocess.Popen instead of main() to capture stdout
        with subprocess.Popen(
            ["ros_license_toolkit",
             "test/_test_data/test_pkg_unknown_license"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ) as process:
            stdout, _ = process.communicate()
        self.assertNotEqual(os.EX_OK, process.returncode)
        self.assertIn(b'not in SPDX list of licenses', stdout)
        self.assertIn(b'my own fancy license 1.0', stdout)

    def test_pkg_unknown_license_missing_file(self):
        """Test on a package that has an unknown license
        without a license file"""
        self.assertEqual(os.EX_DATAERR, main(
            ["test/_test_data/test_pkg_unknown_license_missing_file"]))

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

    def test_pkg_with_multiple_licenses_one_referenced_incorrect(self):
        """Test on a package with multiple licenses declared in the
        package.xml. First has tag not in SPDX list with correct source file,
        second is in SPDX."""
        process, stdout = open_subprocess(
            "test_pkg_with_multiple_licenses_one_referenced_incorrect")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertIn(b"WARNING Licenses ['BSD'] are not in SPDX list", stdout)

    def test_pkg_wrong_license_file(self):
        """Test on a package with a license text file that does not match
        the license declared in the package.xml."""
        process, stdout = open_subprocess("test_pkg_wrong_license_file")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertIn(b"WARNING", stdout)


def open_subprocess(test_data_name: str):
    """Open a subprocess to also gather cl output"""
    with subprocess.Popen(
            ["ros_license_toolkit",
             "test/_test_data/" + test_data_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
    ) as process:
        stdout, _ = process.communicate()
    return process, stdout


if __name__ == '__main__':
    unittest.main()
