import argparse
import logging
import shutil
import subprocess
import time
from pathlib import Path


def wait_for_log_update(logfile_path, timeout=10):
    logfile_path = Path(logfile_path)  # Ensure logfile_path is a Path object
    start_time = time.time()
    initial_mod_time = logfile_path.stat().st_mtime
    while time.time() - start_time < timeout:
        current_mod_time = logfile_path.stat().st_mtime
        if current_mod_time != initial_mod_time:
            return True  # Log file has been updated
        time.sleep(0.5)  # Wait for half a second before checking again
    return False  # Timeout reached without detecting an update


# Function to close and remove all handlers from the logger
def close_logger_handlers(logger):
    for handler in logger.handlers[:]:  # Iterate over a copy of the list
        handler.close()
        logger.removeHandler(handler)


# Configure the logging module to write logs to a file
BASE_DIR = Path(__file__).parent.parent.absolute()
LOGFILE = BASE_DIR / "test.log"
logging.basicConfig(
    filename=LOGFILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def determine_conda():
    """Determines the conda executable to use (i.e. mm, mamba, or conda)."""

    # Check if mamba is installed
    try:
        output = subprocess.run("mamba --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No mamba executable found.")
        return "mamba"
    except Exception as e:
        print(output.stderr.decode())
        pass

    # Check if micromamba is installed
    try:
        output = subprocess.run("micromamba --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No micromamba executable found.")
        return "micromamba"
    except FileNotFoundError:
        pass

    # Check if conda is installed
    try:
        output = subprocess.run("conda --version", shell=True, capture_output=True)
        if len(output.stderr) > 0:
            raise FileNotFoundError("No conda executable found.")
        return "conda"
    except FileNotFoundError:
        pass

    raise FileNotFoundError("No conda executable found.")


def remove_environment(conda_command):
    """Removes the conda environment created for the experiment."""

    # Remove the conda environment
    command = f"{conda_command} env remove -n experiment"
    if conda_command == "micromamba":
        command += " -y"
    subprocess.run(f"{command}", shell=True)


def create_environment(conda_command):
    """Creates a new conda environment with the required dependencies."""

    parent_dir = Path(__file__).resolve().parent
    environment_file = parent_dir / "environment.yml"

    # Create a new conda environment with the required dependencies
    command = f"{conda_command} env create -f {environment_file.as_posix()}"
    if conda_command == "micromamba":
        command += " -y"

    fail_message = "Failed to create environment!"
    pass_message = "Environment created successfully!"

    try:
        run_and_log(
            command=command, fail_message=fail_message, pass_message=pass_message
        )
    except Exception as e:
        raise e
    finally:
        # Log the dependencies
        log_dependencies(conda_command=conda_command)


def remove_imports(imports_dir):
    """Removes the imports directory if it exists."""
    imports_dir = Path(imports_dir)
    if imports_dir.exists():
        print("Removing imports directory...")
        shutil.rmtree(imports_dir)


def find_imports(library, input_dir, output_dir=None):
    """Finds all imports from a given library in Python files and copies them to test.

    Args:
        library (str): The library to search for in the imports. E.g. 'qtpy'.
        input_dir (str): The directory to search for Python files.
            E.g. 'C:\path\to\sleap'.
        output_dir (str): The directory to save the modified Python files. Defaults to
            '.\experiment'.
    """

    if output_dir is None:
        current_file = Path(__file__).resolve()
        output_dir = Path(current_file.parent) / "experiment"

    # Remove the imports directory if it exists
    remove_imports(imports_dir=output_dir)

    input_path = Path(input_dir)
    output_path = Path(
        output_dir
    ).resolve()  # Resolve to absolute path but keep it relative if given so
    output_path.mkdir(
        parents=True, exist_ok=True
    )  # Create output directory if it doesn't exist
    init_path = (
        output_path / "__init__.py"
    )  # Create __init__.py file in output directory

    for python_file in input_path.rglob("*.py"):  # Search recursively for Python files
        with python_file.open("r") as infile:
            lines = infile.readlines()

        # Find and collect multi-line imports that start with 'from qtpy'
        qtpy_imports = []
        multi_line_import = False
        current_import = ""

        for line in lines:
            if multi_line_import:
                current_import += line.strip()
                if line.strip().endswith(")"):
                    qtpy_imports.append(current_import)
                    multi_line_import = False
                    current_import = ""
                continue

            if line.startswith(f"from {library}"):
                if line.strip().endswith("("):
                    multi_line_import = True
                    current_import = line.strip()
                else:
                    qtpy_imports.append(line.strip())

        # Only write to the output file if there are matching lines
        if qtpy_imports:
            # Create the output file path
            output_file_path = output_path / python_file.name
            with output_file_path.open("w") as outfile:
                outfile.write("\n".join(qtpy_imports) + "\n")
            # Append the output file path to the __init__.py file
            with init_path.open("a") as initfile:
                initfile.write(f"from {output_path.name} import {python_file.stem}\n")


def user_test_code():
    """User-defined test code to run after the imports have been tested."""

    return

    # Example test code that is not run since after return
    from qtpy.QtWidgets import QApplication, QMainWindow

    def create_app():
        """Creates Qt application."""
        app = QApplication([])
        return app

    app = create_app()

    window = QMainWindow()
    window.showMaximized()

    app.exec_()


def run_and_log(command, fail_message=None, pass_message=None):
    """Runs a command and logs the output."""

    if fail_message is None:
        fail_message = "Failed!"

    if pass_message is None:
        pass_message = "Passed!"

    try:
        output = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            cwd=Path(__file__).resolve().parent,
        )
        if output.returncode != 0:
            error = output.stderr.decode()
            error = error.replace("\r\r", "")
            raise Exception(error)
        print(output.stdout.decode())
        logger.info(pass_message)
        print(pass_message)
    except Exception as e:
        logger.exception(fail_message)
        print(fail_message)
        raise e


def test_code(conda_command):
    """Runs user-defined test code."""

    fail_message = "Tests failed!"
    pass_message = "Tests passed successfully!"
    command = f'{conda_command} run -n experiment python -c "import test_env; test_env.user_test_code()"'
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)


def test_imports(conda_command):
    """Tests the imports in the experiment environment."""

    fail_message = "Imports failed!"
    pass_message = "Imports passed successfully!"
    command = f'{conda_command} run -n experiment python -c "import experiment"'
    run_and_log(command=command, fail_message=fail_message, pass_message=pass_message)


def log_dependencies(conda_command):
    """Logs the dependencies of the experiment environment to file."""

    def post_process_file(filename):
        """Removes empty lines from a file."""

        with open(filename, "r") as f:
            lines = f.readlines()

        with open(filename, "w") as f:
            for line in lines:
                if line.strip():  # only write the line if it's not empty
                    f.write(line)

    mamba_filename = BASE_DIR / "mamba_list.txt"
    pip_filename = BASE_DIR / "pip_freeze.txt"

    # Reset the files
    for filename in [mamba_filename, pip_filename]:
        with open(filename, "w") as f:
            pass

    # mamba list > mamba_list.txt
    with open(mamba_filename, "w") as f:
        subprocess.run(
            f"{conda_command} run -n experiment {conda_command} list",
            shell=True,
            stdout=f,
        )

    # pip freeze > pip_freeze.txt
    with open(pip_filename, "w") as f:
        subprocess.run(
            f"{conda_command} run -n experiment pip freeze", shell=True, stdout=f
        )

    # Remove empty lines from the files
    for filename in [mamba_filename, pip_filename]:
        post_process_file(filename)


def commit_changes(commit_message: str):
    """Commits the changes to the experiment branch."""

    # Commit the changes to the experiment branch
    subprocess.run("git add .", shell=True)
    subprocess.run(f'git commit -m "{commit_message}"', shell=True)


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--library",
        type=str,
        help="The library to search for in the imports. E.g. 'qtpy'.",
        default=None,
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        help="The directory to search for Python files. E.g. 'C:\path\to\sleap'.",
        default=None,
    )
    parser.add_argument(
        "--commit-message",
        type=str,
        help="The commit message to use when committing the changes.",
    )
    return parser


def parse_args(library=None, input_dir=None, commit_message=None):
    # Parse the command-line arguments
    parser = create_parser()
    args = parser.parse_args()
    library = library or args.library
    input_dir = input_dir or args.input_dir
    commit_message = commit_message or args.commit_message
    print(f"Arguments:\n{args}")

    if commit_message is None:
        parser.print_usage()
        raise ValueError(
            "Missing required argument --commit-message. "
            "Please provide a commit message.",
        )
    return library, input_dir, commit_message


def main(library=None, input_dir=None, commit_message=None):

    # Parse the command-line arguments
    library, input_dir, commit_message = parse_args(library, input_dir, commit_message)

    # Determine the conda executable to use
    conda_command = determine_conda()

    # Remove environment
    remove_environment(conda_command=conda_command)

    # Reset log file
    with open(LOGFILE, "w") as f:
        pass

    try:
        # Create a new conda environment
        create_environment(conda_command=conda_command)

        # Test the imports
        if input_dir is not None and library is not None:
            # Find imports from library in the given directory
            find_imports(
                library=library,
                input_dir=input_dir,
            )
            test_imports(conda_command=conda_command)

        # Run user-defined test code
        test_code(conda_command=conda_command)

        # If no errors, add P: to the commit message
        commit_message = f"P: {commit_message}"
    except Exception as e:
        # If there are errors, add F: to the commit message
        commit_message = f"F: {commit_message}"
        raise e
    finally:
        # Commit the changes
        close_logger_handlers(logger)
        wait_for_log_update(LOGFILE)
        commit_changes(commit_message=commit_message)


if __name__ == "__main__":
    main(
        library="qtpy",
        input_dir=r"C:\Users\Liezl\Projects\sleap-estimates-animal-poses\pull-requests\sleap",
        commit_message="Run test code",
    )
