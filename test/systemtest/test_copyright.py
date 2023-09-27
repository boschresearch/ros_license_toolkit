# Copyright (c) 2023 - for information on the respective copyright owner
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

import os
from test.systemtest._test_helpers import make_repo, remove_repo

from ros_license_toolkit.copyright import CopyrightPerPkg
from ros_license_toolkit.package import Package, get_packages_in_path

TEST_DATA_FOLDER = os.path.abspath("test/_test_data")

TEST_PACKAGES_COPYRIGHT_FILE = [
    "test_pkg_has_code_disjoint",
    "test_pkg_has_code_of_different_license_and_tag",
    "test_pkg_spdx_name",
    "test_pkg_spdx_tag",
    "test_pkg_with_license_and_file"
]


def remove_existing_copyright_file(path: str):
    if os.path.exists(path):
        os.remove(path)


def test_copyright():
    pkg_path = os.path.join(TEST_DATA_FOLDER, "test_pkg_has_code_disjoint")
    pkg = Package(pkg_path)
    cpr_secs = CopyrightPerPkg(pkg).copyright_strings
    assert len(cpr_secs) == 2


def test_copyright_to_string():
    pkg_path = os.path.join(TEST_DATA_FOLDER, "test_pkg_has_code_disjoint")
    pkg = Package(pkg_path)
    cprs = CopyrightPerPkg(pkg)
    assert '1995' in str(cprs)
    assert 'Foo Bar' in str(cprs)
    assert '2000' in str(cprs)
    assert '2002' in str(cprs)
    assert 'Another' in str(cprs)


def test_get_copyright_file_contents():
    make_repo(TEST_DATA_FOLDER)
    for pkg_name in TEST_PACKAGES_COPYRIGHT_FILE:
        pkg_path = os.path.join(TEST_DATA_FOLDER, pkg_name)
        pkg = get_packages_in_path(pkg_path)[0]
        copyright_file_content = pkg.get_copyright_file_contents()
        print(copyright_file_content)
        with open(os.path.join(
                TEST_DATA_FOLDER,
                "copyright_file_contents",
                pkg_name
        ), "r") as f:
            expected = f.read()
            assert expected == copyright_file_content
    remove_repo(TEST_DATA_FOLDER)


def test_write_copyright_file():
    make_repo(TEST_DATA_FOLDER)
    for pkg_name in TEST_PACKAGES_COPYRIGHT_FILE:
        pkg_path = os.path.join(TEST_DATA_FOLDER, pkg_name)
        copyright_file_folder = \
            os.path.join("/tmp", pkg_name)
        os.makedirs(name=copyright_file_folder,
                    exist_ok=True)
        copyright_file_path = os.path.join(
            copyright_file_folder, 'copyright')
        remove_existing_copyright_file(
            path=copyright_file_path)
        pkg = get_packages_in_path(pkg_path)[0]
        pkg.write_copyright_file(
            copyright_file_path)
        assert os.path.exists(copyright_file_path)
        with open(copyright_file_path, "r") as f:
            output = f.read()
            with open(os.path.join(
                TEST_DATA_FOLDER,
                "copyright_file_contents",
                pkg_name
            ), "r") as f:
                expected = f.read()
                assert expected == output
        remove_existing_copyright_file(
            path=copyright_file_path)
    make_repo(TEST_DATA_FOLDER)
