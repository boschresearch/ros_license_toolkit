# # Copyright (c) 2023 - for information on the respective copyright owner
# # see the NOTICE file and/or the repository
# # https://github.com/boschresearch/ros_license_linter

# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at

# #     http://www.apache.org/licenses/LICENSE-2.0

# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.

# """Assemble copyright notices for a package."""

# from typing import Dict, List

# from ros_license_linter.package import Package
# from ros_license_linter.license_tag import LicenseTag


# class Copyright:

#     def __init__(self, pkg: Package):
#         self.pkg = pkg
#         # one section per license tag
#         # each section is a list of unique copyright lines
#         self.copyright_sections: Dict[str, List[str]] = {}
#         for license_tag in self.pkg.license_tags:
#             self.copyright_sections[license_tag.source_files_str] = []

