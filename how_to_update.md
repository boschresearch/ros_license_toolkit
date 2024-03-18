# Note for me

## Requirements

```bash
pip install bumpver build twine
```

## Steps

How to update the project:

1. Increment version

    ```bash
    git checkout main
    git pull
    bumpver update --patch  # or --minor or --major
    git push
    git push --tags
    ```

1. Build and upload to PyPI

    ```bash
    python -m build
    twine check dist/*
    twine upload dist/*  # user: ct2034_0
    ```

## source

<https://realpython.com/pypi-publish-python-package/#build-your-package>
