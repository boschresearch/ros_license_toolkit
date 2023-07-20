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

import unittest
from unittest.mock import patch

from ros_license_toolkit.copyright import (
    _get_year_from_copyright_str, Copyright)


class TestCopyright(unittest.TestCase):

    def test_get_year_from_copyright_str(self):
        # should be able to extract the year from a copyright string
        copyright_str = 'Copyright (c) 2023 - for information on the '\
            'respective copyright owner'
        self.assertEqual(_get_year_from_copyright_str(copyright_str), 2023)

        # should be able to extract the year range from a copyright string
        copyright_str = 'Copyright (c) 2010-2023 - Michael "Mickey" Mouse'
        self.assertEqual(_get_year_from_copyright_str(
            copyright_str), (2010, 2023))

        # everything else should raise an exception
        copyright_str = 'Copyright (c) who knows when'
        with self.assertRaises(ValueError):
            _get_year_from_copyright_str(copyright_str)
        copyright_str = 'Copyright 42'
        with self.assertRaises(ValueError):
            _get_year_from_copyright_str(copyright_str)

    @patch('ros_license_toolkit.package.Package')
    def test_copyrigth_str(self, mock_package):
        mock_package.name = 'test_package'
        mock_package.license_file = 'LICENSE'
        c = Copyright(mock_package)
        self.assertEqual(c.__str__(), 'test_package (LICENSE)')
