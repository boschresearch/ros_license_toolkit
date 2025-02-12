# Note for me

## Requirements

```bash
pip install bumpver build twine
```

## Steps

How to increase the version number:

```bash
git checkout main
git pull
bumpver update --patch  # or --minor or --major
git push
git push --tags
```

This triggers the CI to build and release the package.

## ALL BELOW IS PERFORMED AUTOMATICALLY

> **_ATTENTION:_**
The following steps are performed automatically

(by the [CI release job](.github/workflows/release.yml))

If you want to release manually:

```bash
python -m build
twine check dist/*
twine upload dist/*  # user: ct2034_0
```

## source

<https://realpython.com/pypi-publish-python-package/#build-your-package>
