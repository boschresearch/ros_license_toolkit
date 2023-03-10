# ros_license_linter

[![Pytest](https://github.com/boschresearch/ros_license_linter/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/boschresearch/ros_license_linter/actions/workflows/pytest.yml) [![Lint](https://github.com/boschresearch/ros_license_linter/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/boschresearch/ros_license_linter/actions/workflows/lint.yml) [![GitHub issues](https://img.shields.io/github/issues/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/issues) [![GitHub prs](https://img.shields.io/github/issues-pr/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/pulls) [![python](https://img.shields.io/github/languages/top/boschresearch/ros_license_linter.svg)](https://github.com/boschresearch/ros_license_linter/search?l=python) [![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](https://github.com/boschresearch/ros_license_linter/blob/main/LICENSE)

> **Warning**
> For any legal questions, please consult a lawyer. This tool is not a substitute for legal advice. 

## Motivation
ROS packages must have licenses. This tool checks if the license declarations in the `package.xml` matches the license(s) of the code. We do this by using `scancode-toolkit` to scan the code and compare the results to the declaration in the `package.xml`

## Functionality
```mermaid
graph TD
    classDef stroke stroke:#333,stroke-width:2px;
    s([scan code for licenses and copyrights]) 
    class s stroke
    p[compare to\n package.xml\n _for linter_]
    class p stroke
    c[create\ncopyright file\n_to be implemented_]
    class c stroke
    style c fill:#f98,color:#000
    s --> p
    s --> c
```

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

## Usage
### Installation
Install the package from source:
```bash
pip install .
```

### Basic Usage
You should then have the executable in your `$PATH` and can run it on any ROS package or a directory containing multiple ROS packages:
```bash
ros_license_linter my_ros_package
```

### All Options
```
$ ros_license_linter -h
usage: ros_license_linter [-h] [-v] [-q] path

Checks ROS packages for correct license declaration.

positional arguments:
  path           path to ROS2 package or repo containing packages

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  enable verbose output
  -q, --quiet    disable most output
```

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
