#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Package Manager v1.1.0
    \n
    This module allows you to automatically import missing libraries (modules) that are required
    by any script without the need to any other installation or a requirement file.
"""

import ast, imp, inspect, os, pkgutil, subprocess, sys

############ AUTHOURSHIP & COPYRIGHTS ############
__author__      = "Abdullrahman Elsayed"
__copyright__   = "Copyright 2022, Supportive Python Modules Project"
__credits__     = __author__
__license__     = "MIT"
__version__     = "1.1.0"
__maintainer__  = __author__
__email__       = "abdull15199@gmail.com"
__status__      = "Production"
__doc__         = "This module allows you to automatically import missing libraries (modules) that are required by any script without the need to any other installation or a requirement file."
##################################################

def PSL(Text: str, LastLine = False) -> None:
    """
        Print on Same Line (PSL).
        Print multiple lines on the same line.

        Args:
            Text (str): Text to be printed.
            LastLine (bool, optional): If True, when you print after it, it will print in new line.

        Returns:
            None
    """
    
    if LastLine:
        sys.stdout.write("\r\033[K" + Text + "\n")
    else:
        sys.stdout.write("\r\033[K" + Text)
    
    return None

class PackageManager:
    """
        Main class of the module.
    """

    def __init__(self) -> None:
        """
            Constructor gets the main script file path and store class-scope variables
        """

        # Class Variables
        self.__mainScript = sys.modules['__main__']
        self.__mainScriptPath = str(self.__mainScript.__file__).replace('\\', '/')
        self.__mainScriptCode = inspect.getsource(self.__mainScript)

        # User Accessable Variable
        self.InstalledPackages = list(self.__getInstalledPackages())
        self.RequiredPackages = list(self.__getRequiredPackages(DeepScan=True, Verbose=True))

        # User Accessable Methods
        self.InstallPackage = lambda PackageName, PackageVersion, Verbose: \
            self.__installPackage(PackageName=str(PackageName), PackageVersion=str(PackageVersion), Verbose=bool(Verbose))

        self.UpgradePIP = lambda Verbose: self.__upgradePIP(Verbose=bool(Verbose))

    def __collectImportedModules(self, FileCode: str, Verbose = False) -> tuple:
        """
            Extracts imported packages from code passed as 'FileCode'.
            This function collects only 'import ...' and 'from ... import ...',
            it does not work with '__import__'. This is a feature to be added in v1.2.0

            Args:
                FileCode (str): Code of target file.
                Verbose (bool, optional): Prints function progress. Defaults to False.

            Returns:
                tuple: Imported modules names. 
        """
        
        def _walk_import_nodes(import_node: object) -> None:
            """
                Walks over import nodes in target code.

                Args:
                    import_node (object): AST.Node object

                Returns:
                    None
            """

            for module in import_node.names:
                imported_modules.add(module.name.split(".")[0])

            return None
        
        def _walk_importFrom_nodes(importFrom_node: object) -> None:
            """
                Walks over from-import nodes in target code.

                Args:
                    importFrom_node (object): AST.Node object

                Returns:
                    None
            """
            # if node.module is missing, it's a "from . import ..." statement
            # if level > 0, it's a "from .submodule import ..." statement
            if (importFrom_node.module is not None) and (importFrom_node.level == 0):
                imported_modules.add(importFrom_node.module.split(".")[0])
            
            return None

        # Print progress to stdout
        if Verbose: print("Analyzing Main Script...")

        # Empty set to collect imported modules
        imported_modules = set()
        # Parsing code into nodes using 'ast' module
        parsed_code = ast.parse(FileCode)

        # Instintiate an instance of 'NodeVisitor'
        walker = ast.NodeVisitor()
        # Assigning function to method (import ...)
        walker.visit_Import = _walk_import_nodes
        # Assigning function to method (from ... import ...)
        walker.visit_ImportFrom = _walk_importFrom_nodes
        # Attempting to walk over parsed code nodes
        walker.visit(parsed_code)

        return tuple(imported_modules)

    def __getRequiredPackages(self, DeepScan = False, Verbose = False) -> tuple:
        
        main_script_imports = self.__collectImportedModules(FileCode=self.__mainScriptCode, Verbose=Verbose)
        installed_main_script_imports = [pkg for pkg in main_script_imports if pkg in self.InstalledPackages]
        required_packages = set([pkg for pkg in main_script_imports if pkg not in installed_main_script_imports])
        
        if DeepScan:
            for pkg in installed_main_script_imports:
                pkg_path = self.__getPackagePathByName(PackageName=pkg, Verbose=Verbose)
                
                for module in pkg_path:
                    if module != None:
                        with open(module, 'r') as pkg_file:
                            pkg_code = pkg_file.read()
                        
                        pkg_imports = self.__collectImportedModules(FileCode=pkg_code, Verbose=Verbose)

                        required_packages.update(pkg_imports)

        else:
            pass
        
        required_packages = [pkg for pkg in required_packages if pkg not in self.InstalledPackages]
        required_packages = sorted(list(required_packages))

        return tuple(required_packages)

    def __getPackagePathByName(self, PackageName: str, Verbose = False) -> tuple:
        """
            Searches and returns a package path using its name.

            Args:
                PackageName (str): Target package name.
                Verbose (bool, optional): Prints function progress. Defaults to False.

            Returns:
                str: Package file path.
        """

        # Print progress to stdout
        if Verbose: print(f"Looking for Package '{PackageName}'...")

        package_path = imp.find_module(PackageName)[1]

        # if 'imp' returns None indicating pre-compiled or binary python file
        if package_path == None:
            package_path = [None]

        # if 'imp' returns one .py file path
        elif os.path.isfile(package_path):
            package_path = [package_path]
        
        # if 'imp' returns module parent dir
        elif os.path.isdir(package_path):
            # check if package dir has an '__init__.py' file
            if os.path.isfile(f'{package_path}/__init__.py'):
                package_path = [f'{package_path}/__init__.py']
            # if package dir has no '__init__.py' file, then return all .py files in it
            else:
                package_path = []
                for root, dirs, files in os.walk(package_path):
                    for f in files:
                        if '.py' in f:
                            package_path.append(f)
                        else:
                            pass
        
        # any other unexpected 'imp' return
        else:
            raise FileNotFoundError

        # Apply consistant path format
        package_path = [pkg.replace('\\','/') if pkg != None else pkg for pkg in package_path]

        return tuple(package_path)

    def __getInstalledPackages(self, Verbose = False) -> list:
        """
            Collects all packages (built-ins & installed) accessible by Python.

            Args:
                Verbose (bool, optional): Prints function progress. Defaults to False.

            Returns:
                list: Names of all accessible packages (installed & built-ins).
        """

        # Print progress to stdout
        if Verbose: print("Collecting Installed Packages...")

        # Retriving all 'sys' accessible packages
        packages = list(sys.modules) + list(sys.builtin_module_names) + list(sys.stdlib_module_names)

        # Retriving other packages inaccessible by 'sys'
        # Collect package names using '..iter_modules()'
        # Do not use '..walk_packages()'; it is slower than '..iter_modules()' because it retrives submodules as well
        # 'pkgutil.walk_packages()' returns objects of modules, so we need to collect 'pkg.name'
        for pkg in pkgutil.iter_modules():
            packages.append(pkg.name)
        
        # Sorting and setting packages names to remove duplicate names
        packages = sorted(set(packages))

        return list(packages)

    def __installPackage(self, PackageName: str, PackageVersion = "latest", Verbose = False) -> dict:
        """
            Installs specific package with desired version. If 'PackageVersion' == None -> latest version will be installed.

            Args:
                PackageName (str): Exact package name to be installed.
                PackageVersion (str, optional): Exact package version to be installed. Comparator operators are not allowed! Defaults to "latest".
                Verbose (bool, optional): Prints function progress.

            Returns:
                dict: Returns a dict; keys = ReturnMessage, ExitCode, ExitMessage
        """

        # Check package version to be installed
        if PackageVersion.replace('.','').isdigit():
            target_package = f'{str(PackageName)}=={str(PackageVersion)}'
        else:
            target_package = str(PackageName)

        # Print progress to stdout
        if Verbose: print(f'Attempting to install "{target_package}"...')

        # Setup a command to install the package
        # Using 'sys.executable' to ensure that we install the package for the same version and location of running Python
        installation_command = f'"{sys.executable}" -m pip install {str(target_package)}'
        installation_process = subprocess.Popen(str(installation_command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Collect return messages from executed command
        execution_message = str(installation_process.communicate())
        execution_exit_code = int(installation_process.wait())

        # Define function return messages based on execution return message
        if execution_exit_code == 0:    # 0 -> Successful Exit Code
            return_message = f'"{target_package}" is already installed or has been installed successfully!'
        elif execution_exit_code == 1:  # 1 -> Successful Exit Code
            return_message = f'"{target_package}" was not recognized, please consider installing it manually!'
        else:                           # Other -> Unknown Exit Code
            return_message = f'Unexpected exit code ({execution_exit_code}) returned while installing "{target_package}"'

        # Print progress to stdout
        if Verbose: print(return_message)
        
        return dict(
                {
                "ReturnMessage" : return_message,
                "ExitCode"      : execution_exit_code,
                "ExitMessage"   : execution_message
                }
            )

    def __upgradePIP(self, Verbose = False) -> int:
        """
            Upgrade pip if an upgrade is available.

            Args:
                Verbose (bool, optional): Prints function progress.

            Returns:
                int: Exit Code {
                    0 : Successfully upgraded | No new version available
                    1 : An error occured
                    2 : Unknown exit code
                }
        """

        # Print progress to stdout
        if Verbose: print(f'Attempting to upgrade pip...')

        # Setup a command to install the package
        # Using 'sys.executable' to ensure that we install the package for the same version and location of running Python
        execution = subprocess.Popen(f'"{sys.executable}" -m pip install --upgrade pip', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Collect return code from executed command
        execution_exit_code = int(execution.wait())
        
        # Define function return messages based on execution return message
        if execution_exit_code == 0:    # 0 -> Successful Exit Code
            return_code = 0
            return_message = 'pip is already latest or has been upgraded successfuly!'
        elif execution_exit_code == 1:  # 1 -> Error Exit Code
            return_code = 1
            return_message = 'pip was not upgraded, please consider upgrading pip manually!'
        else:                           # Other -> Unknown Exit Code
            return_code = 2
            return_message = 'Unexpected exit code!'
        
        # Print progress to stdout
        if Verbose: print(return_message)

        return int(return_code)

    def AutoImportMissings(self, UpgradePIP = False, Verbose = False) -> bool:
        """
            Automatically analysis '__main__' script, update PIP, and installs required packages if missing.

            Args:
                UpgradePIP (bool, optional): Optionally upgrade PIP before installing required packages.
                Verbose (bool, optional): Prints function progress.

            Returns:
                bool: returns True if all packages were successfully installed, else, False.
        """

        failed_packages = []

        if len(self.RequiredPackages) != 0:
            if UpgradePIP: self.__upgradePIP(Verbose=Verbose)

            retry_counter = 3

            while retry_counter:

                for ind, pkg in enumerate(self.RequiredPackages, 1):
                    if Verbose: print(f"\nInstalling Packages {ind}/{len(self.RequiredPackages)}")
                    
                    pkg_installer = self.__installPackage(PackageName=pkg, Verbose=Verbose)

                    if pkg_installer['ExitCode'] != 0:
                        if pkg in failed_packages:
                            pass
                        else:
                            failed_packages.append(pkg)
                
                if len(failed_packages) == 0:
                    break
                else:
                    retry_counter -= 1

            if len(failed_packages) != 0:
                print(f'\nCOULD NOT INSTALL THESE PACKAGES: {", ".join(failed_packages)}!\nPLEASE CONSIDER INSTALLING THEM MANUALLY!\n')

                while True:
                    decision = input('Would you like to continue executing your code? *IT WILL PROBABLY RAISE AN ERROR IF YOU CONTINUE..* (Y/n) ')

                    if decision == 'Y':
                        print()
                        return False
                    elif decision == 'n':
                        exit()
                    else:
                        pass
            else:
                print()
                return True
        
        else:
            return True

class AutoImporter:
    """
        Auto Imports missing required modules.
        This class is riggered by importing it.
    """
    # Call AutoImportMissings as a variable value so that it is triggered as soon as the class AutoImporter is imported
    if __name__ != '__main':
        PackageManager().AutoImportMissings(UpgradePIP=False, Verbose=True)