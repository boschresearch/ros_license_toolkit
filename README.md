# ros_license_toolkit

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/boschresearch/ros_license_toolkit/pytest.yml?label=pytest&style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/actions/workflows/pytest.yml)
[![github lint](https://img.shields.io/github/actions/workflow/status/boschresearch/ros_license_toolkit/lint.yml?label=lint&style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/actions/workflows/lint.yml)
[![GitHub issues](https://img.shields.io/github/issues/boschresearch/ros_license_toolkit.svg?style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/issues) 
[![GitHub prs](https://img.shields.io/github/issues-pr/boschresearch/ros_license_toolkit.svg?style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/pulls) 
[![PyPI](https://img.shields.io/pypi/v/ros_license_toolkit?style=flat-square)](https://pypi.org/project/ros-license-toolkit/)
[![python](https://img.shields.io/github/languages/top/boschresearch/ros_license_toolkit.svg?style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/search?l=python) 
[![License](https://img.shields.io/badge/license-Apache%202-blue.svg?style=flat-square)](https://github.com/boschresearch/ros_license_toolkit/blob/main/LICENSE)

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
    p[compare to\n package.xml\nfor linting]
    class p stroke
    c[create\ncopyright file\nfor release]
    class c stroke
    s --> p
    s --> c
```

## Features

This checks:

- [x] Is any license defined in `package.xml`?
    [- LicenseTagExistsCheck](src/ros_license_toolkit/checks.py#L90)
- [x] Has at most one license tag without a source-files declaration?
    [- LicenseTagExistsCheck](src/ros_license_toolkit/checks.py#L90)
- [x] Do all licenses tags follow the SPDX standard?
    [- LicenseTagIsInSpdxListCheck](src/ros_license_toolkit/checks.py#L104)
- [x] Are license texts available and correctly referenced for all declared licenses?
    [- LicenseTextExistsCheck](src/ros_license_toolkit/checks.py#L123)
- [x] Does the code contain licenses not declared in any license tags source-file attribute (source-files="src/something/**")?
    [- LicensesInCodeCheck](src/ros_license_toolkit/checks.py#L182)

## Usage

### Installation

Install the package from source:

```bash
pip install .
```

### Basic Usage

You should then have the executable in your `$PATH` and can run it on any ROS package or a directory containing multiple ROS packages:

```bash
ros_license_toolkit my_ros_package
```

### All Options

```bash
$ ros_license_toolkit -h
usage: ros_license_toolkit [-h] [-c] [-v] [-q] path

Checks ROS packages for correct license declaration.

positional arguments:
  path                  path to ROS2 package or repo containing packages

options:
  -h, --help            show this help message and exit
  -c, --generate_copyright_file
                        generate a copyright file
  -v, --verbose         enable verbose output
  -q, --quiet           disable most output
```

### Using it as a GitHub action

You can use `ros_license_toolkit` inside your GitHub workflow in order to check licenses in your
repository in each pull request. Use the following job inside your workflow file:

```yaml
jobs:
  check_licenses:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - uses: boschresearch/ros_license_toolkit@1.1.5
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
- [x] Turn into github action.

## License

ros_license_toolkit is open-sourced under the Apache-2.0 license. See the
[LICENSE](LICENSE) file for details.
