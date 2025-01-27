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
from typing import Optional

from ros_license_toolkit.checks import Status

SUCCESS = Status.SUCCESS
WARNING = Status.WARNING
FAILURE = Status.FAILURE


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
            "test/_test_data/test_deep_package_folder/deeper/test_pkg_deep",
        ]:
            with subprocess.Popen(
                ["ros_license_toolkit", call_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            ) as process:
                stdout, _ = process.communicate()
            self.assertEqual(os.EX_OK, process.returncode)
            self.assertIn(b"test_pkg_deep", stdout)
        remove_repo(repo_path)

    def test_pkg_both_tags_not_spdx(self):
        """Test on a package that has two different Licenses that both
        have a not SPDX conform Tag. License files and source files
        are SPDX conform"""
        process, stdout = open_subprocess("test_pkg_both_tags_not_spdx")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(
            check_output_status(stdout, WARNING, SUCCESS, WARNING, WARNING, WARNING, WARNING)
        )

    def test_pkg_both_tags_not_spdx_one_file_own(self):
        """Test on a package that has two licenses. One is self-defined, other
        one with not SPDX tag but therefore code and license file in SPDX"""
        process, stdout = open_subprocess("test_pkg_both_tags_not_spdx_one_file_own")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(stdout, WARNING, SUCCESS, WARNING, FAILURE, WARNING, WARNING)
        )

    def test_pkg_code_has_no_license(self):
        """Test on a package that has a correct package.xml with a license
        linked, but the source file is not referenced. Source file itself has
        no license declaration in it."""
        process, stdout = open_subprocess("test_pkg_code_has_no_license")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertNotIn(b"WARNING", stdout)

    def test_pkg_has_code_disjoint(self):
        """Test on a package with two disjoint sets of source files under
        a license different from the package main license."""
        process, stdout = open_subprocess("test_pkg_has_code_disjoint")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=WARNING))

    def test_pkg_has_code_of_different_license(self):
        """Test on a package with source files under a license different
        from the package main license (here LGPL). It should fail, because
        the additional license is not declared in the package.xml."""
        process, stdout = open_subprocess("test_pkg_has_code_of_different_license")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_lic_in_code=FAILURE))

    def test_pkg_has_code_of_different_license_and_tag(self):
        """Test on a package with source files under a license different
        from the package main license, but the additional license is declared
        in the package.xml."""
        process, stdout = open_subprocess("test_pkg_has_code_of_different_license_and_tag")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=WARNING))

    def test_pkg_has_code_of_different_license_and_wrong_tag(self):
        """Test on a package with source files under a license different
        from the package main license, but the additional license is declared
        in the package.xml, but with the wrong name."""
        process, stdout = open_subprocess("test_pkg_has_code_of_different_license_and_wrong_tag")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(
                stdout,
                exp_schema_validated=WARNING,
                exp_lic_text_exits=FAILURE,
                exp_lic_in_code=FAILURE,
            )
        )

    def test_pkg_ignore_readme_contents(self):
        """Test on a package with readme files. READMEs mention licenses
        that are not in package and shall therefore be ignored."""
        process, stdout = open_subprocess("test_pkg_ignore_readme_contents")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=WARNING))

    def test_pkg_name_not_in_spdx(self):
        """Test on a package that has valid License file with BSD-3-Clause
        but its license tag BSD is not in SPDX format"""
        process, stdout = open_subprocess("test_pkg_name_not_in_spdx")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(
            check_output_status(stdout, SUCCESS, SUCCESS, WARNING, WARNING, SUCCESS, WARNING)
        )

    def test_pkg_no_file_attribute(self):
        """Test on a package with License file that is not referenced in
        package.xml"""
        process, stdout = open_subprocess("test_pkg_no_file_attribute")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_no_license(self):
        """Test on a package with no license declared in the package.xml."""
        process, stdout = open_subprocess("test_pkg_no_license")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(stdout, FAILURE, FAILURE, SUCCESS, FAILURE, FAILURE, SUCCESS)
        )

    def test_pkg_no_license_file(self):
        """Test on a package with no license text file."""
        process, stdout = open_subprocess("test_pkg_no_license_file")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_lic_text_exits=FAILURE))

    def test_pkg_one_correct_one_license_file_missing(self):
        """Test on a package that has one correct license with file
        and code, but also one not known license tag without file"""
        process, stdout = open_subprocess("test_pkg_one_correct_one_license_file_missing")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(stdout, WARNING, SUCCESS, WARNING, FAILURE, SUCCESS, SUCCESS)
        )

    def test_pkg_scheme1_conform(self):
        """Test on a package that has all attributes for being conform to
        the official scheme v1"""
        process, stdout = open_subprocess("test_pkg_scheme1_conform")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_scheme1_violation(self):
        """Test on a package that has all attributes except for maintainer,
        and therefore not conform to the official scheme v1."""
        process, stdout = open_subprocess("test_pkg_scheme1_violation")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=FAILURE))

    def test_pkg_scheme2_conform(self):
        """Test on a package that has all attributes for being conform to
        the official scheme v2"""
        process, stdout = open_subprocess("test_pkg_scheme2_conform")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_scheme2_violation(self):
        """Test on a package that has all attributes except the wrong version
        format being conform to the official scheme v2"""
        process, stdout = open_subprocess("test_pkg_scheme2_violation")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=FAILURE))

    def test_pkg_scheme3_conform(self):
        """Test on a package that has all attributes for being conform to
        the official scheme v3"""
        process, stdout = open_subprocess("test_pkg_scheme3_conform")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_scheme3_violation(self):
        """Test on a package that has all attributes except faulty name format
        for being conform to the official scheme v3."""
        process, stdout = open_subprocess("test_pkg_scheme3_violation")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_schema_validated=FAILURE))

    def test_pkg_spdx_tag(self):
        """Test on a package with a license declared in the package.xml
        with the SPDX tag."""
        process, stdout = open_subprocess("test_pkg_spdx_tag")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_too_many_license_files(self):
        """ "Test on a package with multiple License files that are not
        declared by any tag and could therefore be removed."""
        process, stdout = open_subprocess("test_pkg_too_many_license_files")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertIn(b"bsd.LICENSE", stdout)
        self.assertIn(b"apl.LICENSE", stdout)
        self.assertNotIn(b"../../../LICENSE", stdout)
        self.assertTrue(check_output_status(stdout, exp_lic_files_referenced=FAILURE))

    def test_pkg_tag_not_spdx(self):
        """Test on a package that has one linked declaration, one code file
        but not in SPDX tag. Tag must be gotten from declaration."""
        process, stdout = open_subprocess("test_pkg_tag_not_spdx")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(
            check_output_status(stdout, SUCCESS, SUCCESS, WARNING, WARNING, WARNING, WARNING)
        )

    def test_pkg_unknown_license(self):
        """Test on a package with an unknown license declared in the
        package.xml."""
        process, stdout = open_subprocess("test_pkg_unknown_license")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(stdout, exp_lic_tag_spdx=WARNING, exp_lic_text_exits=FAILURE)
        )

    def test_pkg_unknown_license_missing_file(self):
        """Test on a package that has an unknown license
        without a license file"""
        process, stdout = open_subprocess("test_pkg_unknown_license_missing_file")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(stdout, exp_lic_tag_spdx=WARNING, exp_lic_text_exits=FAILURE)
        )

    def test_pkg_with_license_and_file(self):
        """Test on a package with a license declared in the package.xml
        and a matching license text file."""
        process, stdout = open_subprocess("test_pkg_with_license_and_file")
        self.assertEqual(os.EX_OK, process.returncode)
        self.assertTrue(check_output_status(stdout))

    def test_pkg_with_multiple_licenses_no_source_files_tag(self):
        """Test on a package with multiple licenses declared in the
        package.xml, none of which have source file tags."""
        process, stdout = open_subprocess("test_pkg_with_multiple_licenses_no_source_files_tag")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(check_output_status(stdout, exp_lic_tag_exists=FAILURE))

    def test_pkg_with_multiple_licenses_one_referenced_incorrect(self):
        """Test on a package with multiple licenses declared in the
        package.xml. First has tag not in SPDX list with correct
        source file, second is in SPDX."""
        process, stdout = open_subprocess(
            "test_pkg_with_multiple_licenses_one_referenced_incorrect"
        )
        self.assertEqual(os.EX_OK, process.returncode)
        print(stdout)
        self.assertIn(b"WARNING Licenses ['BSD'] are not in SPDX list", stdout)
        self.assertTrue(
            check_output_status(stdout, WARNING, SUCCESS, WARNING, WARNING, SUCCESS, WARNING)
        )

    def test_pkg_wrong_license_file(self):
        """Test on a package with a license text file that does not match
        the license declared in the package.xml, both tag and file in spdx"""
        process, stdout = open_subprocess("test_pkg_wrong_license_file")
        self.assertEqual(os.EX_DATAERR, process.returncode)
        self.assertTrue(
            check_output_status(
                stdout, exp_lic_text_exits=FAILURE, exp_lic_files_referenced=WARNING
            )
        )


def open_subprocess(test_data_name: str):
    """Open a subprocess to also gather cl output"""
    with subprocess.Popen(
        ["ros_license_toolkit", "test/_test_data/" + test_data_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        stdout, _ = process.communicate()
    return process, stdout


def check_output_status(  # pylint: disable=too-many-positional-arguments
    output: str,
    exp_schema_validated: Status = Status.SUCCESS,
    exp_lic_tag_exists: Status = Status.SUCCESS,
    exp_lic_tag_spdx: Status = Status.SUCCESS,
    exp_lic_text_exits: Status = Status.SUCCESS,
    exp_lic_in_code: Status = Status.SUCCESS,
    exp_lic_files_referenced: Status = Status.SUCCESS,
) -> bool:
    """Check output of each check for expected status.
    each argument except for output tells the expected status of a
    certain check. The default is always SUCCESS."""
    # pylint: disable=too-many-arguments

    real_lic_validated = get_test_result(output, "SchemaCheck")
    real_lic_tag_exists = get_test_result(output, "LicenseTagExistsCheck")
    real_lic_tag_spdx = get_test_result(output, "LicenseTagIsInSpdxListCheck")
    real_lic_text_exits = get_test_result(output, "LicenseTextExistsCheck")
    real_lic_in_code = get_test_result(output, "LicensesInCodeCheck")
    real_lic_files_referenced = get_test_result(output, "LicenseFilesReferencedCheck")

    return (
        exp_schema_validated == real_lic_validated
        and exp_lic_tag_exists == real_lic_tag_exists
        and exp_lic_tag_spdx == real_lic_tag_spdx
        and exp_lic_text_exits == real_lic_text_exits
        and exp_lic_in_code == real_lic_in_code
        and exp_lic_files_referenced == real_lic_files_referenced
    )


def get_test_result(output: str, test_name: str) -> Optional[Status]:
    """Get result status for specific test.
    Return None if no status could be found"""
    lines = output.splitlines()
    for i, line in enumerate(lines):
        if test_name not in str(line):
            continue
        if i + 1 > len(lines):
            continue
        result_line = str(lines[i + 1])
    if "FAILURE" in result_line:
        return FAILURE
    if "WARNING" in result_line:
        return WARNING
    if "SUCCESS" in result_line:
        return SUCCESS
    return None


if __name__ == "__main__":
    unittest.main()
