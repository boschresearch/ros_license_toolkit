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
This module contains helper functions for testing.
"""

import os
import shutil

import git


def remove_repo(repo_path):
    """Remove an existing git repo."""
    shutil.rmtree(os.path.join(repo_path, ".git"))


def make_repo(repo_path):
    """Make a git repo with a commit."""
    assert os.path.exists(repo_path)
    if os.path.exists(os.path.join(repo_path, ".git")):
        remove_repo(repo_path)
    repo = git.Repo.init(repo_path)
    repo.create_remote(
        "origin", "https://fake.git")
    repo.index.add(["."])
    repo.index.commit("initial commit")
