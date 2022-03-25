#!/usr/bin/env python
# coding: utf-8

import os
import sys
import shutil
import time
import argparse
import subprocess

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', '--file', type=str, help='define the targeted binary', required=True)
ARGS = PARSER.parse_args()

# The DLL filenames who starts with one element of this list will not be checked.
dlls_excludes = {
	'api-ms',
	'ext-ms',
	'ntdll',
	'kernel32',
	'user32',
	'shell32',
	'comctl32',
	'imm32',
	'gdi32',
	'msvcr',
	'WS2_32',
	'ole32',
	'ninput',
	'setupapi'
}

# Do not modify this part.
imports_excludes = {
	'Import Address Table',
	'Import Name Table',
	'time date stamp',
	'Index of first forwarder reference',
	'Characteristics',
	'Address of HMODULE',
	'Bound Import Name Table',
	'Unload Import Name Table'
}

def ascii():
	print('·▄▄▄▄  ▄▄▌  ▄▄▌  ▪  ▄▄▄   ▄▄▄·  ▐ ▄ ▄▄▄▄▄')
	print('██▪ ██ ██•  ██•  ██ ▀▄ █·▐█ ▀█ •█▌▐█•██  ')
	print('▐█· ▐█▌██▪  ██▪  ▐█·▐▀▀▄ ▄█▀▀█ ▐█▐▐▌ ▐█.▪')
	print('██. ██ ▐█▌▐▌▐█▌▐▌▐█▌▐█•█▌▐█ ▪▐▌██▐█▌ ▐█▌·')
	print('▀▀▀▀▀• .▀▀▀ .▀▀▀ ▀▀▀.▀  ▀ ▀  ▀ ▀▀ █▪ ▀▀▀  v0.1')

def rreplace(s, old, new):
	return (s[::-1].replace(old[::-1],new[::-1], 1))[::-1]

def delete_dir(directory):
	if os.path.exists(directory):
		try:
			shutil.rmtree(directory)
		except PermissionError:
			pass

def create_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def delete_file(file):
	if os.path.exists(file):
		os.remove(file)

def copy_binary_to_ouput_dir(binary_path):
	if not os.path.exists(binary_path):
		return False
	binary_name = os.path.basename(binary_path).replace(' ', '_')
	try:
		shutil.copyfile(binary_path, f'output/{binary_name}')
		return True
	except FileNotFoundError:
		return False
	except PermissionError:
		return False

def copy_binary_and_required_files(binary):
	copy_binary_to_ouput_dir(binary)
	if os.path.exists('import'):
		for (dirpath, dirnames, filenames) in os.walk('import'):
			for file in filenames:
				copy_binary_to_ouput_dir(f'import/{file}')

def get_dependencies(binary_name):
	binary_name = binary_name.replace(' ', '_')
	os.system(f'cd output/ && dumpbin /dependents {binary_name} /OUT:../dependencies.txt')
	with open('dependencies.txt', 'r') as file:
		data = file.read()
		if 'Image has the following dependencies:' in data and 'Summary' in data:
			data = data.split('Image has the following dependencies:')[1]
			data = data.split('Summary')[0]
			with open('output/dependencies.txt', 'w') as subfile:
				for line in data.splitlines():
					if line.lower().endswith('.dll'):
						line = line.strip()
						subfile.write(f'{line}\n')
	delete_file('dependencies.txt')

def get_not_excluded_dll_names():
	filtered_dlls = []
	with open('output/dependencies.txt', 'r') as file:
		for dll_name in file:
			excluded = False
			dll_name = dll_name.strip()
			for exclude in dlls_excludes:
				if dll_name.lower().startswith(exclude):
					excluded = True
			if not excluded:
				filtered_dlls.append(dll_name)	
	delete_file('output/dependencies.txt')			
	return filtered_dlls

def get_imports_functions(binary_name, dll_name):
	functions = []
	binary_name = binary_name.replace(' ', '_')
	os.system(f'cd output/ && dumpbin /imports {binary_name} /OUT:../imports.txt')
	with open('imports.txt', 'r') as file:
		data = file.read()
		if dll_name in data:
			data = data.split(dll_name)[1]
			for line in data.splitlines():
				line = line.strip()
				if line.lower().endswith('.dll') or line.endswith('Summary'):
					break
				if not any(exclude in line for exclude in imports_excludes) and len(line) > 0 and ' ' in line:
					func = line.split(' ')[1].replace(' ', '')
					functions.append(func)
	delete_file('imports.txt')
	return functions

def generate_test_dll(functions = None):
	exported_functions = []
	with open('DLLirantDLL\\dllmain-preset.c', 'r') as fin:
		with open('DLLirantDLL\\dllmain.c', 'w') as fout:
			if functions is not None:
				for line in fin:
					if '##DLL_MAIN##' in line:
						fout.write(line.replace('##DLL_MAIN##', ''))
					elif '##EXPORTED_FUNCTIONS##' in line:
						for func in functions:
							if len(func) > 0:
								exported_functions.append(f'__declspec(dllexport) void {func}()' + '{ Main(); }')
						exported_functions = '\n'.join(exported_functions)
						#exported_functions = rreplace(exported_functions, '{ }', '{ Main(); }')
						fout.write(line.replace('##EXPORTED_FUNCTIONS##', exported_functions))
					else:
						fout.write(line)
			else:
				for line in fin:
					if '##DLL_MAIN##' in line:
						fout.write(line.replace('##DLL_MAIN##', 'CreateThread(NULL, NULL, (LPTHREAD_START_ROUTINE)Main, NULL, NULL, NULL);\nbreak;'))
					elif '##EXPORTED_FUNCTIONS##' in line:
						fout.write(line.replace('##EXPORTED_FUNCTIONS##', ''))
					else:
						fout.write(line)
	os.system('cd DLLirantDLL && msbuild DLLirantDLL.sln /t:Rebuild /p:Configuration=Release /p:Platform="x64"')
	return exported_functions

def check_dll_hijacking(binary_name, binary_original_directory, dll_name, exported_functions = 'DllMain'):
	if not os.path.exists(f'DLLirantDLL\\x64\\Release\\DLLirantDLL.dll'):
		return False
	os.system(f'copy DLLirantDLL\\x64\\Release\\DLLirantDLL.dll output\\{dll_name}')
	ascii()
	print('==================================================')
	print(f'[+] Testing {dll_name}')
	print(f'BINARY: {binary_original_directory}\\{binary_name}')
	print(f'EXPORTED FUNCTIONS:\n')
	print(exported_functions)
	print('==================================================')
	try:
		binary_name = binary_name.replace(' ', '_')
		process = subprocess.Popen(f'output/{binary_name}')
		time.sleep(2)
		if os.path.exists('C:\\DLLirant\\output.txt'):
			with open('results.txt', 'a') as file:
				file.write(f'[+] POTENTIAL DLL HIJACKING FOUND IN: {dll_name}\n')
				file.write(f'BINARY: {binary_original_directory}\\{binary_name}\n')
				file.write(f'{exported_functions}\n\n')
			delete_file('C:\\DLLirant\\output.txt')
			input(f'\n\n[+] Potential DLL Hijacking found in the binary {binary_name} with the dll {dll_name} ! Press enter to continue.')
			os.system(f'taskkill /F /pid {process.pid}')
			return True
		os.system(f'taskkill /F /pid {process.pid}')
		return False
	except OSError:
		with open('admin-required.txt', 'a') as file:
			file.write(f'[!] ADMIN PRIVS REQUIRED ON {binary_original_directory}\\{binary_name}\n')
			file.write(f'DLL: {dll_name}\n')
			file.write(f'{exported_functions}\n\n')
		input(f'\n\n[+] [!] Admin privs required on {binary_name} start it manually to test the dll hijack and press enter to continue.')
		return False

def main():
	# Create output dir if not exists.
	create_dir('output')

	# Create or recreate the directory used by the DLLirant DLL specified in dllmain-preset.c file.
	delete_dir('C:\\DLLirant')
	create_dir('C:\\DLLirant')

	# Name of the binary specified and his directory.
	binary_name = os.path.basename(ARGS.file)
	binary_original_directory = os.path.dirname(os.path.realpath(ARGS.file))

	# Copy the binary to the output directory and copy the required files placed by the user in the "import" directory if exists.
	copy_binary_and_required_files(ARGS.file)

	# Get the dependencies of the binary (DLL names) via dumpbin and save it dependencies.txt.
	get_dependencies(binary_name)

	# Get the list of the dll files who are not excluded (dlls_excludes list from the top of this script).
	dll_files = get_not_excluded_dll_names()

	# For each dll files...
	for dll in dll_files:
		# Get the list of imported functions.
		functions = get_imports_functions(binary_name, dll)

		# Generate the DLLirant test dll file without exported functions.
		generate_test_dll()

		# Test the generated dll to check if a dll hijacking is possible.
		check_dll_hijacking(binary_name, binary_original_directory, dll)

		# Test all functions one by one.
		functions_list = []
		for func in functions:
			functions_list.append(func)
			exported_functions = generate_test_dll(functions_list)
			check_dll_hijacking(binary_name, binary_original_directory, dll, exported_functions)

		# Delete and recreate the output directory to test the others dll files.
		delete_dir('output')
		create_dir('output')

		# Recopy the binary and the required files.
		copy_binary_and_required_files(ARGS.file)

if __name__ == '__main__':
	main()
