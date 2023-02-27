# ros_license_linter

[![Pytest](https://github.com/boschresearch/ros_license_linter/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/boschresearch/ros_license_linter/actions/workflows/pytest.yml) [![Lint](https://github.com/boschresearch/ros_license_linter/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/boschresearch/ros_license_linter/actions/workflows/lint.yml) [![GitHub issues](https://img.shields.io/github/issues/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/issues) [![GitHub prs](https://img.shields.io/github/issues-pr/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/pulls) [![python](https://img.shields.io/github/languages/top/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/search?l=python) [![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](https://github.com/boschresearch/ros_license_linter/blob/main/LICENSE)

> Checks ROS packages for correct license declaration

## Motivation
ROS packages must have licenses. 
This tool checks if the license declarations in the `package.xml` matches the license(s) of the code.
We do this by using `scancode-toolkit` to scan the code and compare the results to the declaration in the `package.xml`

## Features
This checks:
- [x] Is any license defined in `package.xml`?
    [- LicenseTagExistsCheck](src/ros_license_linter/checks.py#L90)
- [x] Has at most one license tag without a source-files declaration?
    [- LicenseTagExistsCheck](src/ros_license_linter/checks.py#L90)
- [x] Do all licenses tags follow the SPDX standard?
    [- LicenseTagIsInSpdxListCheck](src/ros_license_linter/checks.py#L104)
- [x] Are license texts available and correctly referenced for all declared licenses?
    [- LicenseTextExistsCheck](src/ros_license_linter/checks.py#L123)
- [x] Does the code contain licenses not declared in any license tags source-file attribute (source-files="src/something/**")?
    [- LicensesInCodeCheck](src/ros_license_linter/checks.py#L182)

## State of Development
*WORK IN PROGRESS*
This is currently working and feature complete to the point it was originally intended.
But there are still open points concerning testing and it is also very important to make sure how this behaves with existing ROS packages.
In particular, the following things will have to be done:

### To Do
- [ ] Coverage analysis
- [x] Linter(s) per CI
- [x] Field trials (check existing ROS packages and see what to do with the results). see [field-trials/](field-trials/)
- [ ] Evaluate runtime. If scancode-toolkit takes too long on too many cases, we will have to look for an alternative.
- [x] Allow license name in tag to be also full name of SPDX key.
- [x] Each LicenseTag should have SPDX id.
- [ ] Single license tag without file attribute and single license text should match automatically.
- [ ] Turn into github action.

## License
ros_license_linter is open-sourced under the Apache-2.0 license. See the
[LICENSE](LICENSE) file for details.
