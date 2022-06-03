#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Package Manager v2.0.0
    \n
    This module allows you to automatically import missing libraries (modules) that are required
    by any script without the need to any other installation or a requirement file.
    
    .. include:: ./README.md
"""

############ AUTHOURSHIP & COPYRIGHTS ############
__author__      = "Abdullrahman Elsayed"
__copyright__   = "Copyright 2022, Supportive Python Modules Project"
__credits__     = __author__
__license__     = "MIT"
__version__     = "2.0.0"
__maintainer__  = __author__
__email__       = "abdull15199@gmail.com"
__status__      = "Production"
__doc__         = "This module allows you to automatically import missing libraries (modules) that are required by any script without the need to any other installation or a requirement file."
##################################################

import ast, importlib.util, os, pkgutil, subprocess, sys

def PSL(Text: str, LastLine: bool = False) -> None:
    """
        Print on Same Line (PSL).\n
        Print multiple lines on the same line.

        ### Args:
            - Text (str): Text to be printed.
            - LastLine (bool, optional): If True, when you print after it, it will print in new line.

        ### Returns:
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
        self.__mainScriptPath = str((self.__mainScript.__file__).replace('\\', '/'))

        # User Accessable Variable
        self.InstalledPackages = tuple(self.__GetInstalledPackages())
        self.STDPackages = tuple(list(sys.stdlib_module_names) + list(sys.builtin_module_names))
        self.RequiredPackages = tuple()
        self.AnalyzedPackages = set()

        # User Accessable Methods
        self.InstallPackage = lambda PackageName, PackageVersion, Verbose: \
            self.__InstallPackage(PackageName=str(PackageName), PackageVersion=str(PackageVersion), Verbose=bool(Verbose))
        
        self.GetImportedPackages = lambda PackagePath, IncludeDynamic, StrictSearch, Verbose: \
            self.__GetImportedPackages(PackagePath=PackagePath, IncludeDynamic=IncludeDynamic, StrictSearch=StrictSearch, Verbose=Verbose)

        self.UpgradePIP = lambda Verbose: self.__UpgradePIP(Verbose=bool(Verbose))

    ### INFORMATION RETRIVERS

    def __GetPackagePath(self, PackageName: str, IgnoreBuiltins: bool = False, Verbose: bool = False) -> str | None:
        """
            Searches and returns a package path using its name.

            ### Args:
                - PackageName (str): Target package name.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            ### Returns:
                - str | None: Package file path if package exist, else, None will be returned.
        """

        # Print progress to stdout
        if (bool(Verbose)): print(f"Locating package '{PackageName}'...")
        
        # Load module without executing it
        module = importlib.util.find_spec(str(PackageName))

        # Check if module is found
        if (hasattr(module, 'origin')):
            module_path = str(module.origin)

        # Check if module is not found (if module == None)
        else:
            module_path = None

        # If 'IgnoreBuiltins' is True, any built-in package will be returned as None
        if (bool(IgnoreBuiltins)) \
        and (module_path == 'built-in'):
            module_path = None

        else:
            pass

        return module_path

    def __GetImportedPackages(self, PackagePath: str, IncludeDynamic: bool = True, StrictSearch: bool = False, Verbose: bool = False) -> tuple:
        """
            Collects imported packages from python code.\n
            #### IMPORT STATEMENTS INSIDE LOOPS CANNOT BE ACCESSED BY 'IncludeDynamic'

            ### Args:
                - PackagePath (str): Python file path to be analyzed for imports.
                - IncludeDynamic (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - StrictSearch (bool, optional): If enabled, only nodes containing the word 'import' in their source code will be processed. Preferably keep it to default. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            ### Returns:
                - tuple: Names of imported modules by the code provided. If no imported modules found, an empty tuple will be returned.
        """
        
        if (bool(Verbose)): PSL(f"Collecting packages imported by '{os.path.basename(PackagePath)}'")

        def __getPackageSource(FilePath: str) -> str:
            """
                Reads source code from Python file

                ### Args:
                    - PackagePath (str): Python file absoulte path

                ### Raises:
                    - FileNotFoundError: If provided path is invalid or not a file

                ### Returns:
                    - str: Target file content
            """
            # Check if provided parameter is a file path
            if os.path.isfile(FilePath):
                # Open and read content then return it
                with open(file=PackagePath, mode='r', errors='ignore') as source:
                    src_code = source.read()

            # If provided parameter is not a file, raise 'FileNotFoundError'
            else:
                raise FileNotFoundError
            
            return src_code

        def __handleImport(Node: ast.Import) -> tuple:
            """
                Collects packages names imported by 'import ...'

                ### Args:
                    - Node (ast.Import): AST Import type node object

                ### Returns:
                    - tuple: Imported packages names
            """

            # Assure 'Node' type to process it
            if (type(Node) == ast.Import):
                # Collect packages names from Import Nodes
                pkgs = [getPkgName(pkg.name) for pkg in Node.names]
            
            else:
                # Return (None) if this is not an Import Node
                pkgs = [None]
            
            return tuple(pkgs)

        def __handleImportFrom(Node: ast.ImportFrom) -> tuple:
            """
                Collects packages names imported by 'from ... import ...'

                ### Args:
                    Node (ast.ImportFrom): AST ImportFrom type node object

                ### Returns:
                    tuple: Imported packages names
            """
            
            # Assure 'Node' type to process it
            if (type(Node) == ast.ImportFrom):
                # Collect packages names from From...Import Nodes
                pkg = [getPkgName(Node.module)]
            else:
                # Return (None) if this is not an ImportFrom Node
                pkg = [None]
            
            return tuple(pkg)

        def __handleAssign(Node: ast.Assign) -> tuple:
            """
                Collects packages names imported dynamically by assignment 'e.g. variable = __import__(module)'

                ### Args:
                    - Node (ast.Assign): AST Assign type node object

                ### Returns:
                    - tuple: Imported packages names
            """

            # Assure 'Node' type to process it
            if (type(Node) == ast.Assign):
                # Creating empty set to collect packages throughout the process
                pkgs = set()
                # Picking only functions assigned to a variable
                if (hasattr(Node.value, 'func')):
                    # Shorthanding 'Node.value.func'
                    Node_func = Node.value.func
                    
                    # First if statement select directly called dynamic imports (e.g. import_module(module) or __import__(module))
                    # Second if statement select class.method called dynamic imports (e.g. importlib.import_module(module))
                    if (hasattr(Node_func, 'id') and (Node_func.id in ['__import__', 'import_module'])) \
                    or (hasattr(Node_func, 'value') and (Node_func.value.id in ['importlib'])):
                        
                        # Looping over import function arguments to collect modules passed as arguments
                        # This loop applies to positined argument assignment (e.g. __import__(module))
                        for arg in Node.value.args:
                            # Collecting argument value in the packages container
                            pkgs.add(getPkgName(arg.value))
                        
                        # This loop applies to referenced argument assignment (e.g. __import__(name=module))
                        for keyword in Node.value.keywords:
                            # Check if reference argument name == name (applies to '__import__' and 'importlib.import_module')
                            if (keyword.arg == 'name'):
                                # Collecting argument value in the packages container
                                pkgs.add(getPkgName(keyword.value.value))
                    
                    else:
                        pass
                
                else:
                    pass
            
            else:
                # Return (None) if this is not an Assign Node
                pkgs = [None]

            return tuple(pkgs)
                
        def __handleExpr(Node: ast.Expr) -> tuple:
            """
                Collects packages names imported dynamically by direct expression 'e.g. __import__(module)'

                ### Args:
                    - Node (ast.Expr): AST Expr type node object

                ### Returns:
                    - tuple: Imported packages names
            """
            
            # Assure 'Node' type to process it
            # The second part of the if statment is used to ensure it catches only called functions not comments
            # The third part of the if statment ensures that the called import has valid argument value
            if (type(Node) == ast.Expr) \
            and (type(Node.value) == ast.Call) \
            and ((Node.value.args) or (Node.value.keywords)):
                # Creating empty set to collect packages throughout the process
                pkgs = set()

                # This loop applies to positined argument assignment (e.g. __import__(module))
                for arg in Node.value.args:
                    # Picking only directly called functions (|__import__) not functions assigned to variables
                    if (type(arg) == ast.Constant) \
                    and (hasattr(arg, 'value')):
                        # Adding module name to set container
                        pkgs.add(arg.value)
                
                # Applies to referenced argument assignment (e.g. __import__(name=module))
                for keyword in Node.value.keywords:
                    # Ensuring types appropriate for desired import calls (__import__(), importlib.import_module())
                    if (type(keyword.value) == ast.Constant) \
                    and (hasattr(keyword, 'value')):
                        # Adding module name to set container
                        pkgs.add(keyword.value.value)

            else:
                # Return (None) if this is not an Expr Node or the expression is not a function
                pkgs = [None]

            return tuple(pkgs)

        #region FuncBody

        # Extracting source code from target package file
        source_code = str(__getPackageSource(FilePath=PackagePath))

        # Parsed code into ast nodes
        parsed_code = ast.parse(source_code)

        # Shorthanding slicing dot-separated imports (e.g. import os.path)
        # To be used in above functions
        getPkgName = lambda pkg: pkg.split('.')[0]

        # Two empty containers to collect initial and dynamic imports
        initial_imports = set()
        dynamic_imports = set()

        # If 'StrictSearch' is enabled, only nodes containing the word 'import' in their source code will be processed
        if (bool(StrictSearch)):
            code_nodes = [node for node in parsed_code.body if 'import' in ast.get_source_segment(source=source_code, node=node)]
        else:
            code_nodes = parsed_code.body

        # Looping over code nodes
        for node in code_nodes:
            # The following if statments selects only Import, ImportFrom, Assign, and Expression nodes
            # from the provided code and process each node speacially.
            if   type(node) == ast.Import:      initial_imports.update(__handleImport(Node=node))
            elif type(node) == ast.ImportFrom:  initial_imports.update(__handleImportFrom(Node=node))
            elif type(node) == ast.Assign:      dynamic_imports.update(__handleAssign(Node=node))
            elif type(node) == ast.Expr:        dynamic_imports.update(__handleExpr(Node=node))
            # 'else' here is set to pass to ignore every other node type
            else: pass

            # print(node)
            # print(dynamic_imports)
        
        # If 'IncludeDynamic' is enabled, packages imported dynamically while the code runs will be collected.
        # This includes packages imported by '__import__()' and 'importlib.import_module()'.
        # IMPORTS STATEMENTS INSIDE LOOPS WILL NOT BE PROCESSED
        if (bool(IncludeDynamic)):
            imports = set().union(initial_imports, dynamic_imports)
        else:
            imports = initial_imports

        # Check if imports has content. if yes, sort them, if no, set imports to None to indicate No Imports
        if (imports):
            # Neglecting every 'None' element
            imports = [pkg for pkg in imports if pkg != None]
            # Sorting the imports list
            imports = list(sorted(imports))
        else:
            imports = tuple()

        #endregion

        return tuple(imports)

    def __GetRequiredPackages(self, PackagePath: str, IncludeDynamicImports: bool = True, IncludePrivatePackages: bool = False, DeepScan: bool = False, Verbose: bool = False) -> tuple:
        """
            Collects all imported packages by a script and (optionally) imports of its imports,\n
            then tests wheather these packages are installed and importable or not.\n
            #### If you are working on a project with many relative imports, it is prefered to Enable 'DeepScan'

            ### Args:
                - PackagePath (str): Python file path to be analyzed for imports.
                - IncludeDynamicImports (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - IncludePrivatePackages (bool, optional): If enabled, packages names starting with '_' will be collected. PREFERABLY, DON'T CHANGE DEFAULT. Defaults to False.
                - DeepScan (bool, optional): Scans imported scripts in target script for their own imports. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            ### Returns:
                - tuple: Packages imported but not installed or cannot be imported.
        """

        # Collecting imported packages by module given its path 'PackagePath'
        imported_packages = self.__GetImportedPackages(PackagePath=PackagePath, IncludeDynamic=IncludeDynamicImports, StrictSearch=True, Verbose=Verbose)
        # Getting missing packages (packages not accessible in 'sys.path')
        missed_main_imports = [pkg for pkg in imported_packages if pkg not in self.InstalledPackages]
        # Getting project packages (packages in 'sys.modules' but not in 'sys.stdlib_module_names' or 'sys.builtin_module_names')
        project_main_imports = [pkg for pkg in imported_packages if pkg not in set().union(self.STDPackages, missed_main_imports)]
        # 'required_packes' is used as recursion container
        required_packages = set(imported_packages)

        # Check 'DeepScan' state
        if (bool(DeepScan)):
            # Loop over project packages only.
            # System packages are not checked since we can check their requirements through pip,
            # also system packages would take very long time to check, which is unreliable.
            for pkg in project_main_imports:
                if (bool(Verbose)): PSL(f"Analyzing packages imported by '{pkg}'")
                # Check if 'pkg' not in 'self.AnalyzedPackages'
                # 'self.AnalyzedPackages' work as recursion terminator if all project packages are in it
                if pkg not in self.AnalyzedPackages:
                    # Adding 'pkg' to recursion termination list so it is not processed twice
                    self.AnalyzedPackages.add(pkg)

                    # Locating target 'pkg' path
                    pkg_path = self.__GetPackagePath(PackageName=pkg, IgnoreBuiltins=True)

                    # Check if package has a path (not a built-in nor does not exist)
                    if (pkg_path != None):
                        # Firing recursion #
                        # Recursion here works as follow:
                        # 1. 'pkg_path' which is an imported package from '__main__' is checked for its own imports
                        # 2. Second time when the function reachs this recursion again, it checks the imported packages
                        #    in of package imported by '__main__' and so on.
                        # 3. Recursion is terminated when all sub-packages are checked for imports (when pkg_path is None)
                        recursion = self.__GetRequiredPackages(PackagePath=pkg_path, IncludeDynamicImports=IncludeDynamicImports, IncludePrivatePackages=IncludePrivatePackages, DeepScan=DeepScan)

                        # Updating 'required_packages' with new imports from recursion to be carried out to next recursion loop
                        required_packages.update(recursion)
                    
                    # If package is None (built-in or does not exist), continue loop
                    else:
                        continue
                
                # If 'pkg' in 'self.AnalyzedPackages' (else is True),
                # the loop continues without analyzing current 'pkg' since it must have been analyzed before
                else:
                    continue
        
        # If 'DeepScan' is False, return only packages required by __main__
        else:
            if (bool(Verbose)): PSL(f"Analyzing packages imported by '{os.path.basename(PackagePath)}'")
            pass
        
        if (bool(Verbose)): PSL(f"Sorting required packages...")

        # Selecting only parent packages (by using 'pkg.split('.')[0]')
        required_packages = [pkg.split('.')[0] for pkg in required_packages]

        # Another filtration of 'requried_packages', removing packages already installed in 'sys.path' (a.k.a. 'self.InstalledPackages')
        required_packages = sorted(set([pkg for pkg in required_packages if pkg not in self.InstalledPackages]))

        # Selects either to include private modules (modules names starts with '_') in required packages or not
        if (bool(IncludePrivatePackages) == False):
            # Filtration step
            required_packages = [pkg for pkg in required_packages if ((pkg.startswith('_') == False) and (pkg not in project_main_imports))]
        else:
            pass

        # Assigning return value to self.Variable
        self.RequiredPackages = tuple(required_packages)

        return tuple(required_packages)

    def __GetInstalledPackages(self, Verbose: bool = False) -> tuple:
        """
            Collects all packages (built-ins & installed) accessible by Python.

            ### Args:
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            ### Returns:
                - tuple: Names of all accessible packages (installed & built-ins).
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

        return tuple(packages)

    ### ACTION MAKERS

    # def __UpgradePackage(self, PackageName: str, PackageVersion = "latest", Verbose = False):
    #     pass

    def __InstallPackage(self, PackageName: str, PackageVersion: str = "latest", Verbose: bool = False) -> dict:
        """
            Installs specific package with desired version. If 'PackageVersion' == None -> latest version will be installed.

            ### Args:
                - PackageName (str): Exact package name to be installed.
                - PackageVersion (str, optional): Exact package version to be installed. Comparator operators are not allowed! Defaults to "latest".
                - Verbose (bool, optional): Prints function progress.

            ### Returns:
                - dict: Return keys = ReturnMessage, ExitCode, ExitMessage
        """

        # Check package version to be installed
        if PackageVersion.replace('.','').isdigit():
            target_package = f'{str(PackageName)}=={str(PackageVersion)}'
        else:
            target_package = str(PackageName)

        # Print progress to stdout
        if Verbose: PSL(f'Attempting to install "{target_package}"...')

        # Setup a command to install the package
        # Using 'sys.executable' to ensure that we install the package for the same version and location of running Python
        installation_command = f'"{sys.executable}" -m pip install {str(target_package)}'
        installation_process = subprocess.Popen(str(installation_command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Collect return messages from executed command
        execution_message = str(installation_process.communicate())
        execution_exit_code = int(installation_process.wait())

        # Define function return messages based on execution return message
        if execution_exit_code == 0:    # 0 -> Successful Exit Code
            return_message = f'"{target_package}" has been installed successfully!'
        elif execution_exit_code == 1:  # 1 -> Successful Exit Code
            return_message = f'"{target_package}" was not recognized, please consider installing it manually!'
        else:                           # Other -> Unknown Exit Code
            return_message = f'Unexpected exit code ({execution_exit_code}) returned while installing "{target_package}"'

        # Print progress to stdout
        if Verbose: PSL(return_message, LastLine=True)
        
        return dict(
                {
                "ReturnMessage" : return_message,
                "ExitCode"      : execution_exit_code,
                "ExitMessage"   : execution_message
                }
            )

    # def __RemovePackage(self, PackageName: str, PackageVersion = "latest", Verbose = False):
    #     pass

    def __UpgradePIP(self, Verbose: bool = False) -> int:
        """
            Upgrade pip if an upgrade is available.

            ### Args:
                - Verbose (bool, optional): Prints function progress.

            ### Returns:
                - int: Exit Code {
                    * 0 : Successfully upgraded | No new version available
                    * 1 : An error occured
                    * 2 : Unknown exit code
                }
        """

        def __getPIPVersion() -> dict:
            # Retriving pip version
            execution = subprocess.Popen(f'"{sys.executable}" -m pip --version', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pip_version_msg = execution.communicate()[0].decode('UTF-8')
            pip_version = pip_version_msg.split(' ')[1]

            return dict({
                'version': pip_version,
                'message': pip_version_msg
            })

        # Print progress to stdout
        if Verbose: PSL(f'Attempting to upgrade pip...')

        current_pip_version = __getPIPVersion()['version']

        # Setup a command to install the package
        # Using 'sys.executable' to ensure that we install the package for the same version and location of running Python
        execution = subprocess.Popen(f'"{sys.executable}" -m pip install --upgrade pip', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Collect return code from executed command
        execution_exit_code = int(execution.wait())

        new_pip = __getPIPVersion()
        new_pip_version = new_pip['version']
        new_pip_message = new_pip['message'].rstrip('\n')

        pip_is_new = int(new_pip_version.replace('.','')) > int(current_pip_version.replace('.',''))
        
        # Define function return messages based on execution return message
        if (execution_exit_code == 0) and pip_is_new:           # 0 -> Successful Exit Code
            return_code = 0
            return_message = 'pip has been upgraded successfuly!'

        elif (execution_exit_code == 0) and not pip_is_new:     # 0 -> Successful Exit Code
            return_code = 0
            return_message = 'pip is already latest!'

        elif execution_exit_code == 1:  # 1 -> Error Exit Code
            return_code = 1
            return_message = 'pip was not upgraded, please consider upgrading pip manually!'

        else:                           # Other -> Unknown Exit Code
            return_code = 2
            return_message = 'Unexpected exit code!'

        # Print progress to stdout
        if Verbose: PSL(f'{return_message}\n{new_pip_message}', LastLine=True)

        return int(return_code)

    ### USER ACCESSIBLE

    def AutoImportMissings(self, IncludeDynamicImports: bool = True, DeepScan: bool = True, UpgradePIP: bool = False, Verbose: bool = False) -> bool:
        """
            Automatically analysis '__main__' script, update PIP, and installs required packages if missing.

            ### Args:
                - IncludeDynamicImports (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - DeepScan (bool, optional): Scans imported scripts in target script for their own imports. Defaults to True.
                - UpgradePIP (bool, optional): Optionally upgrade PIP before installing required packages. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            ### Returns:
                - bool: returns True if all packages were successfully installed, else, False.
        """

        failed_packages = set()

        requried_packages = self.__GetRequiredPackages(PackagePath=self.__mainScriptPath, IncludeDynamicImports=IncludeDynamicImports, DeepScan=DeepScan, Verbose=Verbose)

        if UpgradePIP: self.__UpgradePIP(Verbose=Verbose)

        for ind, pkg in enumerate(requried_packages, 1):
            if Verbose: print(f"\nInstalling Packages {ind}/{len(requried_packages)}")
            
            retry_counter = 1
            while (retry_counter > 0):
                pkg_installer = self.__InstallPackage(PackageName=pkg, Verbose=Verbose)

                if pkg_installer['ExitCode'] == 0:
                    if pkg in failed_packages:
                        failed_packages.remove(pkg)
                    else:
                        pass
                    
                    break

                else:
                    retry_counter -= 1
                    failed_packages.add(pkg)
        
        if (len(failed_packages) > 0):
            print(f'\nCOULD NOT INSTALL THESE PACKAGES: ({", ".join(failed_packages)})!\nPLEASE CONSIDER INSTALLING THEM MANUALLY!\n')

            while True:
                decision = input('Would you like to continue executing your code? *IT WILL PROBABLY RAISE AN ERROR IF YOU CONTINUE..* (Y/n) ')

                if decision == 'Y':
                    print()
                    return False
                elif decision == 'n':
                    exit()
                else:
                    print('Invalid input!')
        elif (requried_packages == None) \
        or (len(requried_packages) == 0):
            print(f'\nNo missing required packages were found!\n')
        
        else:
            print(f'\nRequired missing packages have been installed successfully!\n')

class AutoImporter:
    """
        Auto Imports missing required modules.\n
        This class is riggered by importing it.
    """
    # Call AutoImportMissings as a variable value so that it is triggered as soon as the class AutoImporter is imported
    if __name__ != '__main':
        PackageManager().AutoImportMissings(IncludeDynamicImports=True, DeepScan=True, UpgradePIP=False, Verbose=True)
