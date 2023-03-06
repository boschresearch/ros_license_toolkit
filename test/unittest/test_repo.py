# Copyright (c) 2023 - for information on the respective copyright owner
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

"""Unit tests for the repo module"""

import os
import unittest

import git

from ros_license_linter.repo import NotARepoError
from ros_license_linter.repo import Repo


class TestRepo(unittest.TestCase):
    """Test the license tag module"""

    def test_init(self):
        """Test the constructor of the Repo class"""
        # Can we find our own repo?
        repo = Repo(os.path.join(os.path.dirname(__file__)))
        self.assertEqual(
            os.path.basename(repo.get_path()),
            "ros_license_linter"
        )

    def test_raises(self):
        """Test that the constructor raises an exception"""
        with self.assertRaises(NotARepoError):
            Repo('/')

    def test_eq(self):
        """Test the equality operator"""
        repo1 = Repo(os.path.join(os.path.dirname(__file__), '..'))
        repo2 = Repo(os.path.join(os.path.dirname(__file__)))
        self.assertEqual(repo1, repo2)

    def test_get_hash(self):
        """Test the get_hash method"""
        repo = Repo(os.path.join(os.path.dirname(__file__)))
        git_repo = git.Repo(repo.get_path())
        self.assertEqual(
            repo.get_hash(),
            git_repo.head.object.hexsha
        )
