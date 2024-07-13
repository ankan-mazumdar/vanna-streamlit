import os

file_path = '/home/vscode/.local/lib/python3.11/site-packages/chromadb/api/types.py'

# Check if the file exists
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Replace np.float_ with np.float64
    content = content.replace('np.float_', 'np.float64')

    with open(file_path, 'w') as file:
        file.write(content)

    print(f'Modified {file_path} successfully.')
else:
    print(f'{file_path} does not exist.')
