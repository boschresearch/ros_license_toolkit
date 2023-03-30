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

from ros_license_toolkit.copyright import Copyright
from ros_license_toolkit.package import Package


def test_copyright():
    path = os.path.abspath("test/_test_data/test_pkg_has_code_disjoint")
    pkg = Package(path)
    cpr_secs = Copyright(pkg).copyright_sections
    assert len(cpr_secs) == 2


def test_copyright_to_string():
    path = os.path.abspath("test/_test_data/test_pkg_has_code_disjoint")
    pkg = Package(path)
    cprs = Copyright(pkg)
    assert '1995' in str(cprs)
    assert 'Foo Bar' in str(cprs)
    assert '2000' in str(cprs)
    assert '2002' in str(cprs)
    assert 'Another' in str(cprs)
