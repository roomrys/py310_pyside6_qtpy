from pathlib import Path

def find_qtpy_imports(input_dir, output_dir):
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
            
            if line.startswith('from qtpy'):
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


if __name__ == "__main__":
    input_directory = r'C:\Users\Liezl\Projects\sleap-estimates-animal-poses\pull-requests\sleap'  # Change this to your target input directory
    output_directory = r'.\envexp'  # Change this to your desired output directory
    find_qtpy_imports(input_directory, output_directory)
