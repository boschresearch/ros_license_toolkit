# Copyright (c) 2024 - for information on the respective copyright owner
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

"""This Module contains SchemaCheck, which implements Check."""

import os
from typing import Optional, Tuple

import requests  # type: ignore[import-untyped]
from lxml import etree

from ros_license_toolkit.checks import Check
from ros_license_toolkit.package import Package


class SchemaCheck(Check):
    """This checks the xml scheme and returns the version number."""

    def __init__(self):
        super().__init__()
        self.accepted_versions = [1, 2, 3]
        self.validation_schema: Optional[etree.XMLSchema] = None

    def _check(self, package: Package):
        """Checks via scheme validation via self._validate.
        Also considers version of package.xml for validation."""
        version: int = package.package_xml_format_ver
        if version in self.accepted_versions:
            status, message = self.validate(package)
            if status:
                self._success(
                    f"Detected package.xml version {version}, " "validation of scheme successful."
                )
            else:
                reason = f"package.xml contains errors: {message}"
                self._failed(reason)
        else:
            # Temporary workaround for not implemented version 4
            if version == 4:
                reason = (
                    "couldn't check package.xml scheme. Version 4 is " + "not available right now"
                )
                self._warning(reason)
            else:
                reason = (
                    "package.xml does not contain correct package "
                    + "format number. Please use a real version. "
                    + '(e.g. <package format="3">)'
                )
                self._failed(reason)

    def validate(self, package: Package) -> Tuple[bool, str]:
        """This is validating the package.xml schema from given package.
        This can only validate for format version 1, 2 or 3. Every other
        version WILL FAIL. If everything is correct, returns format number,
        else -1."""
        version = package.package_xml_format_ver
        message = ""
        schema = self.get_validation_schema(version)
        if schema:
            result = schema.validate(package.parsed_package_xml)
            if not result:
                message = schema.error_log.last_error
            return result, message
        return False, "Couldn't get schema, no validation possible."

    def get_validation_schema(self, version: int):
        """Return validation schema for version 1, 2 or 3. If called for other
        version numbers, this WILL FAIL. Version is not checked again.
        Only call with version 1, 2 or 3."""
        cache_dir: str = os.path.expanduser("~/.cache/ros_license_toolkit")
        os.makedirs(cache_dir, exist_ok=True)
        schema_file = os.path.join(cache_dir, f"package_format{version}.xsd")

        if not os.path.exists(schema_file):
            address = f"http://download.ros.org/schema/package_format{version}.xsd"
            try:
                response = requests.get(address, stream=True, timeout=100)
                response.raise_for_status()
                response_parsed = response.content  # throw error when bad http code

                schema = etree.fromstring(response_parsed)
                with open(schema_file, "wb") as f:
                    f.write(etree.tostring(schema))
            except (AttributeError, etree.XMLSyntaxError) as error:
                print(error)
                print("An error encountered while getting " + address)
        else:
            schema = etree.parse(schema_file)

        self.validation_schema = etree.XMLSchema(schema)
        return self.validation_schema
