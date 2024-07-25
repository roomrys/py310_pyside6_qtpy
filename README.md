# envexp

To get started with the ENVironment EXPeriment package:

1. create an environment with
   ```bash
   mamba env create -f environment.yml
   ```
2. activate the environemnt with
   ```bash
   mamba activate envexp
   ```
3. edit the `envexp/environemnt.yml` to contain the dependencies you need
4. edit the `user_test_code` function in `envexp/test_env.py` to test a specific code block
5. test that all the imports/tests work using CLI
   ```bash
   test-env --library <required> --input-dir <required> --commit-message <required>
   ```

## test-env

```bash
usage: test-env [-h] [--library LIBRARY] [--input-dir INPUT_DIR] [--commit-message COMMIT_MESSAGE]

options:
  -h, --help            show this help message and exit
  --library LIBRARY     The library to search for in the imports. E.g. 'qtpy'.
  --input-dir INPUT_DIR
                        The directory to search for Python files. E.g. 'C:\path o\sleap'.
  --commit-message COMMIT_MESSAGE
                        The commit message to use when committing the changes.
```

> Note: this project was created to verify that Python 3.10, PySide6, and QtPy could work
> together in an environment.
