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
4. specify the path to the source code for the repo we want to test imports for
5. determine which library's imports we are testing in envexp/test_env.py
6. test that all the imports work using CLI
   ```bash
   test-env
   ```

> Note: this project was created to verify that Python 3.10, PySide6, and QtPy could work
> together in an environment.
