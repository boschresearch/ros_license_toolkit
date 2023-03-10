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

import os
import subprocess
import unittest


class TestDocumentation(unittest.TestCase):
    """Test if this packages readme is up to date."""

    def test_readme(self):
        """Check if the help text is up to date."""
        with subprocess.Popen(
            ["bin/ros_license_linter", "-h"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            stdout, stderr = process.communicate()
        self.assertEqual(os.EX_OK, process.returncode)
        output = stdout.decode("utf-8").strip()
        # find relevant part of the readme
        with open("README.md", "r") as readme:
            readme_content = readme.read()
        readme_usage = readme_content.split(
            "$ ros_license_linter -h")[1].split(
                "```")[0].strip()
        self.assertEqual(readme_usage, output)
