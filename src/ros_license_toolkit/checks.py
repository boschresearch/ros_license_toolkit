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

"""This module contains the checks for the linter."""

from enum import IntEnum

from ros_license_toolkit.package import Package, PackageException
from ros_license_toolkit.ui_elements import NO_REASON_STR, green, red, yellow


class Status(IntEnum):
    """Levels of success or failure for the output"""

    SUCCESS = 0
    WARNING = 1
    FAILURE = 2


class Check:
    """Base class for checks."""

    def __init__(self: "Check"):
        """Initialize a check."""
        # overall success of this check
        self.status: Status = Status.FAILURE

        # explanation for success or failure for normal output
        self.reason: str = NO_REASON_STR

        # string with additional information for verbose output
        self.verbose_output: str = ""

    def _failed(self, reason: str):
        """Set this check as failed for `reason`."""
        self.status = Status.FAILURE
        self.reason = reason

    def _warning(self, reason: str):
        """Set this check as passed but display a warning for reason `r`."""
        self.status = Status.WARNING
        self.reason = reason

    def _success(self, reason: str):
        """Set this check as successful for reason `r`."""
        self.status = Status.SUCCESS
        if self.reason == NO_REASON_STR:
            self.reason = ""
        else:
            self.reason += "\n "
        self.reason += reason

    def __str__(self) -> str:
        """Return formatted string for normal output."""
        info: str = str(type(self).__name__) + "\n"
        if self.status == Status.SUCCESS:
            info += green(f" SUCCESS {self.reason}")
        elif self.status == Status.WARNING:
            info += yellow(f" WARNING {self.reason}")
        else:
            info += red(f" FAILURE {self.reason}")
        return info

    def verbose(self) -> str:
        """Return string with additional information for verbose output."""
        return self.verbose_output

    def __bool__(self) -> bool:
        """Evaluate success of check as bool. Warning is treated as success"""
        return self.status != Status.FAILURE

    def get_status(self) -> Status:
        """Get the level of success to also consider possible warnings"""
        return self.status

    def check(self, package: Package):
        """
        Check `package` and set success and reason.

        Calls `_check` internally. If they raise an exception, this is
        caught and the check is set to failed.
        """
        try:
            self._check(package)
        except PackageException as ex:
            self._failed(f"PackageException: {ex}")
            return
        except AssertionError as ex:
            self._failed(f"AssertionError: {ex}")
            return

    def _check(self, package: Package):
        """Check `package`. To be overwritten by subclasses."""
        raise NotImplementedError("Overwrite this")
