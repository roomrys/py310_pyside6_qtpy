import logging
import subprocess
from pathlib import Path

# Configure the logging module to write logs to a file
LOGFILE = 'test.log'
logging.basicConfig(filename=LOGFILE, level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def find_imports(library, input_dir, output_dir=None):
    """Finds all imports from a given library in Python files and copies them to test.
    
    Args:
        library (str): The library to search for in the imports. E.g. 'qtpy'.
        input_dir (str): The directory to search for Python files. 
            E.g. 'C:\path\to\sleap'.
        output_dir (str): The directory to save the modified Python files. Defaults to 
            '.\envexp'.
    """

    if output_dir is None:
        output_dir = '.\envexp'

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
        import envexp
        passed = True
        print("Imports passed successfully!")
        logger.info("Imports passed successfully!")
    except Exception as e:
        passed = False
        print("Imports failed!")
        logger.error(e)
        logger.info("Imports failed!")
        raise e


def log_dependencies():

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
        subprocess.run('mamba run -n envexp mamba list', stdout=f)

    # pip freeze > pip_freeze.txt
    with open(pip_filename, 'w') as f:
        subprocess.run('mamba run -n envexp pip freeze', stdout=f)

    # Remove empty lines from the files
    for filename in [mamba_filename, pip_filename]:
        post_process_file(filename)



def main():
    # Find imports from qtpy in the given directory
    find_imports(library='qtpy', input_dir=r'D:\social-leap-estimates-animal-poses\source\sleap')

    # Test the imports
    test_imports()

    # Log the dependencies
    log_dependencies()

if __name__ == "__main__":
    main()