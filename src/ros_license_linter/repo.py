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

"""
This module contains the Repo class.
"""

import os
from typing import Optional

import git

# how many folders up to search for a repo
REPO_SEARCH_DEPTH = 2


def is_git_repo(path: str) -> bool:
    """Check if a path is a git repo."""
    return os.path.isdir(os.path.join(path, ".git"))


class NotARepoError(Exception):
    """Exception raised when we can't find a repo."""


class Repo:
    """Represents a git repository."""

    def __init__(self, package_path: str):
        """Initialize a Repo object.

        :param package_path: Absolute path to the package.
        :type package_path: str
        """

        # absolute path to the package
        self.abs_package_path: str = package_path

        # repo path relative to the package
        relpath: Optional[str] = None
        search_path = package_path
        for _ in range(REPO_SEARCH_DEPTH + 1):
            if is_git_repo(search_path):
                relpath = os.path.relpath(
                    search_path, self.abs_package_path)
                break
            search_path = os.path.dirname(search_path)

        if relpath is None:
            raise NotARepoError("No git repo found for package.")

        # absolute path to the repo
        self.abs_path: str = os.path.join(
            self.abs_package_path, relpath)

        # (for logging purposes) the current git hash
        repo = git.Repo()
        self.git_hash: str = repo.head.object.hexsha

        # pylint: disable=fixme
        # TODO: search for license text files here and use the info for
        #  all packages in the repo to speed up the process and avoid
        #  duplicate scans.

    def __eq__(self, __o) -> bool:
        """Check if two repos are the same."""
        return os.path.samefile(self.abs_path, __o.abs_path)

    def get_path(self) -> str:
        """Get the absolute path to the repo."""
        return self.abs_path
