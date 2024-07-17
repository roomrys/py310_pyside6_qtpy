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
3. test that all the imports work
   ```bash
   python test.py
   ```

> Note: this project was created to verify that Python 3.10, PySide6, and QtPy could work
> together in an environment.
