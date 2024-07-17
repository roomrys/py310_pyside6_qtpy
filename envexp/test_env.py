import logging
import subprocess
from pathlib import Path

# Configure the logging module to write logs to a file
LOGFILE = 'test.log'
logging.basicConfig(filename=LOGFILE, level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def remove_environment():
    """Removes the conda environment created for the experiment."""

    # Remove the conda environment
    subprocess.run('mamba env remove -n experiment', shell=True)

def create_environment():
    """Creates a new conda environment with the required dependencies."""

    parent_dir = Path(__file__).resolve().parent
    environment_file = parent_dir / 'environment.yml'

    # Create a new conda environment with the required dependencies
    subprocess.run(f'mamba env create -f {environment_file.as_posix()}', shell=True)

    # Log the dependencies
    log_dependencies()

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
        output_dir = f'{current_file.parent}\experiment'

    input_path = Path(input_dir)
    output_path = Path(output_dir).resolve()  # Resolve to absolute path but keep it relative if given so
    output_path.mkdir(parents=True, exist_ok=True)  # Create output directory if it doesn't exist
    init_path = output_path / '__init__.py'  # Create __init__.py file in output directory

    for python_file in input_path.rglob('*.py'):  # Search recursively for Python files
        with python_file.open('r') as infile:
            lines = infile.readlines()

        # Find and collect multi-line imports that start with 'from qtpy'
        qtpy_imports = []
        multi_line_import = False
        current_import = ''
        
        for line in lines:
            if multi_line_import:
                current_import += line.strip()
                if line.strip().endswith(')'):
                    qtpy_imports.append(current_import)
                    multi_line_import = False
                    current_import = ''
                continue
            
            if line.startswith(f'from {library}'):
                if line.strip().endswith('('):
                    multi_line_import = True
                    current_import = line.strip()
                else:
                    qtpy_imports.append(line.strip())

        # Only write to the output file if there are matching lines
        if qtpy_imports:
            # Create the output file path
            output_file_path = output_path / python_file.name
            with output_file_path.open('w') as outfile:
                outfile.write('\n'.join(qtpy_imports) + '\n')
            # Append the output file path to the __init__.py file
            with init_path.open('a') as initfile:
                initfile.write(f'from {output_path.name} import {python_file.stem}\n')


def test_imports():

    # Reset log file
    with open(LOGFILE, 'w') as f:
        pass

    # Run the test and log results
    try:
        output = subprocess.run('mamba run -n experiment python -c "import experiment"', shell=True, capture_output=True)
        if output.returncode != 0:
            error = output.stderr.decode()
            error = error.replace('\r\r', '')
            raise Exception(error)
        print("Imports passed successfully!")
        logger.info("Imports passed successfully!")
    except Exception as e:
        logger.exception("Imports failed!")
        print("Imports failed!")
        raise e


def log_dependencies():
    """Logs the dependencies of the experiment environment to file."""

    def post_process_file(filename):
        """Removes empty lines from a file."""

        with open(filename, 'r') as f:
            lines = f.readlines()

        with open(filename, 'w') as f:
            for line in lines:
                if line.strip():  # only write the line if it's not empty
                    f.write(line)

    mamba_filename = 'mamba_list.txt'
    pip_filename = 'pip_freeze.txt'

    # mamba list > mamba_list.txt
    with open(mamba_filename, 'w') as f:
        subprocess.run('mamba run -n experiment mamba list', stdout=f)

    # pip freeze > pip_freeze.txt
    with open(pip_filename, 'w') as f:
        subprocess.run('mamba run -n experiment pip freeze', stdout=f)

    # Remove empty lines from the files
    for filename in [mamba_filename, pip_filename]:
        post_process_file(filename)



def main():
    # Remove environment
    remove_environment()

    # Create a new conda environment
    create_environment()

    # Find imports from qtpy in the given directory
    find_imports(library='qtpy', input_dir=r'D:\social-leap-estimates-animal-poses\source\sleap')

    # Test the imports
    test_imports()

if __name__ == "__main__":
    main()