# ros_license_linter
Checks ROS packages for correct license declaration

## Motivation
ROS packages must have licenses. 
This tool checks if the license declarations in the `package.xml` matches the license(s) of the code.
We do this by using `scancode-toolkit` to scan the code and compare the results to the declaration in the `package.xml`

## Features
This checks:
- [x] Is any license defined in `package.xml`?
    [- LicenseTagExistsCheck](src/ros_license_linter/checks.py#L79)
- [x] Has at most one license tag without a source-files declaration?
    [- LicenseTagExistsCheck](src/ros_license_linter/checks.py#L79)
- [x] Do all licenses tags follow the SPDX standard?
    [- LicenseTagIsInSpdxListCheck](src/ros_license_linter/checks.py#L92)
- [x] Are license texts available and correctly referenced for all declared licenses?
    [- LicenseTextExistsCheck](src/ros_license_linter/checks.py#L108)
- [x] Does the code contain licenses not declared in any license tags source-file attribute (source-files="src/something/*")?
    [- LicensesInCodeCheck](src/ros_license_linter/checks.py#L155)

## State of Development
*WORK IN PROGRESS*
This is currently working and feature complete to the point it was originally intended.
But there are still open points concerning testing and it is also very important to make sure how this behaves with existing ROS packages.
In particular, the following things will have to be done:

### To Do
- [ ] Coverage analysis
- [ ] Field trials (check existing ROS packages and see what to do with the results.)
- [ ] Evaluate runtime. If scancode-toolkit takes too long on too many cases, we will have to look for an alternative.

## License
ros_license_linter is open-sourced under the Apache-2.0 license. See the
[LICENSE](LICENSE) file for details.