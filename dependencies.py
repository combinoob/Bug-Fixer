import os
import ast
import json

def get_imports(filepath):
    with open(filepath, 'r') as file:
        tree = ast.parse(file.read(), filename=filepath)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    return imports

def find_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def is_project_import(import_name, project_directory):
    project_files = {os.path.splitext(os.path.relpath(file, project_directory))[0].replace(os.path.sep, '.') for file in python_files}
    return import_name in project_files

def get_project_imports(filepath, project_directory):
    imports = get_imports(filepath)
    project_imports = [imp for imp in imports if is_project_import(imp, project_directory)]
    return project_imports

def build_dependency_dict(python_files, project_directory):
    dependency_dict = {}
    for file in python_files:
        try:
            file_imports = get_project_imports(file, project_directory)
            dependency_dict[file] = [os.path.join(project_directory, imp.replace('.', os.path.sep) + '.py') for imp in file_imports]
        except:
            pass
    return dependency_dict

def save_dependency_dict_to_json(dependency_dict, output_filepath):
    with open(output_filepath, 'w') as json_file:
        json.dump(dependency_dict, json_file, indent=4)


project_directory = 'chatbotui-master/Combined_LLM_Docker/Main'
python_files = find_python_files(project_directory)
dependency_dict = build_dependency_dict(python_files, project_directory)
#print (dependency_dict)
output_filepath = 'dependency.json'
save_dependency_dict_to_json(dependency_dict, output_filepath)