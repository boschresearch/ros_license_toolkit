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

from typing import Tuple

from lxml import etree

from ros_license_toolkit.checks import Check


class SchemaCheck(Check):
    """This checks the xml scheme and returns the version number."""
    def __init__(self):
        super().__init__()
        xml_schema_3_parsed = etree.parse('./schemas/package_format3.xsd')
        self.xml_schema_3 = etree.XMLSchema(xml_schema_3_parsed)
        xml_schema_2_parsed = etree.parse('./schemas/package_format3.xsd')
        self.xml_schema_2 = etree.XMLSchema(xml_schema_2_parsed)
        xml_schema_1_parsed = etree.parse('./schemas/package_format1.xsd')
        self.xml_schema_1 = etree.XMLSchema(xml_schema_1_parsed)

    def _check(self, package):
        version, status = self.validate(package.abspath + "/package.xml")
        if status:
            self._success(f"Detected package.xml version {version}, "
                          "validation of scheme successful.")
        else:
            reason = ''
            if version == 1:
                reason = "package.xml contains errors: " +\
                    f"{self.xml_schema_1.error_log.last_error.message}"
            elif version == 2:
                reason = "package.xml contains errors: " +\
                    f"{self.xml_schema_2.error_log.last_error.message}"
            elif version == 3:
                reason = "package.xml contains errors: " +\
                    f"{self.xml_schema_3.error_log.last_error.message}"
            elif version == -1:
                reason = "package.xml does not contain correct package " +\
                    "format number. Please use a real version. " +\
                    "(e.g. <package format=\"3\">)"
            self._failed(reason)

    def validate(self, pck_xml_path: str) -> Tuple[int, bool]:
        """This is validating package.xml file from given path.
        Automatically detects version number and validates
        it with corresponding scheme, e.g. format 3.
        If everything is correct, returns format number, else -1."""
        xml_doc_parsed = etree.parse(pck_xml_path)
        for element in xml_doc_parsed.getiterator():
            if element.tag == 'package' and 'format' in element.attrib:
                version = element.attrib['format']
                status_check = False
                if version == '3':
                    version = 3
                    status_check = self.xml_schema_3.validate(xml_doc_parsed)
                elif version == '2':
                    version = 2
                    status_check = self.xml_schema_2.validate(xml_doc_parsed)
                elif version == '1':
                    version = 1
                    status_check = self.xml_schema_1.validate(xml_doc_parsed)
                else:
                    version = -1
                return (version, status_check)
        return (-1, False)
