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
This module contains UI elements for the CLI.
"""

from enum import Enum, auto

# colors

GREEN = "\033[92m"
RED = "\033[91m"
NC = "\033[00m"


def red(message: str):
    """Make this `message` red"""
    return f"{RED}{message}{NC}"


def green(message: str):
    """Make this `message` green"""
    return f"{GREEN}{message}{NC}"

# further UI elements


FAILURE_STR = red("FAILURE")
SUCCESS_STR = green("SUCCESS")
NO_REASON_STR = "No reason provided."
N_SEP = 20


def major_sep() -> str:
    """Get a major separator"""
    return "=" * N_SEP


def minor_sep() -> str:
    """Get a minor separator"""
    return "-" * N_SEP


# verbosity levels

class Verbosity(Enum):
    """Verbosity levels for the output"""
    QUIET = auto()
    NORMAL = auto()
    VERBOSE = auto()


def rll_print_factory(verbosity: Verbosity):
    """Return a function that prints only if the verbosity is high enough"""
    def rll_print(message: str, level: Verbosity = Verbosity.NORMAL):
        """Print `message` if the verbosity is high enough"""
        if level.value <= verbosity.value:
            print(message)
    return rll_print
