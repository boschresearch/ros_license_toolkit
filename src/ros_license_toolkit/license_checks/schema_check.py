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

from typing import Dict, Tuple

from lxml import etree

from ros_license_toolkit.checks import Check
from ros_license_toolkit.package import Package


class SchemaCheck(Check):
    """This checks the xml scheme and returns the version number."""
    def __init__(self):
        super().__init__()
        self.xml_schemas: Dict[int, etree] = {}
        for i in range(1, 4):
            xml_schema_parsed = etree.parse(f'./schemas/package_format{i}.xsd')
            self.xml_schemas[i] = etree.XMLSchema(xml_schema_parsed)

    def _check(self, package: Package):
        """Checks via schema validation if the package.xml has the correct
        format, dependant on the version it is in."""
        status, message = self.validate(package)
        version: int = package.package_xml_format_ver
        if status:
            self._success(f"Detected package.xml version {version}, "
                          "validation of scheme successful.")
        else:
            # Temporary workaround for not implemented version 4
            if version == 4:
                reason = "couldn't check package.xml scheme. Version 4 is " +\
                    "not available right now"
                self._warning(reason)
                return

            if message != '':
                reason = f"package.xml contains errors: {message}"
            else:
                reason = "package.xml does not contain correct package " +\
                    "format number. Please use a real version. " +\
                    "(e.g. <package format=\"3\">)"
            self._failed(reason)

    def validate(self, package: Package) -> Tuple[bool, str]:
        """This is validating package.xml file from given path.
        Automatically detects version number and validates
        it with corresponding scheme, e.g. format 3.
        If everything is correct, returns format number, else -1."""
        version = package.package_xml_format_ver
        message = ''
        if version in self.xml_schemas:
            schema = self.xml_schemas[version]
            result = schema.validate(package.parsed_package_xml)
            if not result:
                message = schema.error_log.last_error
            return result, message
        return False, message
