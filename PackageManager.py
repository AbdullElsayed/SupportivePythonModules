#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""###
ISSUES TO FIX:
- Script must re-run to be able to detect newly installed packages ==> Must re-run __main__ script within this module if new packages were installed.
###"""
"""
    Package Manager v2.1.5
    \n
    This module allows you to automatically import missing libraries (modules) that are required by a script without the need to any other installation or a requirement file. And you can also use this module to export requirements file specific to your project without dealing with the hustle of creating a venv to collect requirements.
    
    .. include:: ./README.md
"""

############ AUTHOURSHIP & COPYRIGHTS ############
__author__      = "Abdullrahman Elsayed"
__copyright__   = "Copyright 2022, Supportive Python Modules Project"
__credits__     = "Abdullrahman Elsayed"
__license__     = "MIT"
__version__     = "2.1.5"
__maintainer__  = "Abdullrahman Elsayed"
__email__       = "abdull15199@gmail.com"
__status__      = "Production"
__doc__         = "This module allows you to automatically import missing libraries (modules) that are required by any script without the need to any other installation or a requirement file."
##################################################

import ast, importlib.util, importlib.metadata, os, pkgutil, subprocess, sys

def PSL(Text: str, LastLine: bool = False) -> None:
    """
        Print on Same Line (PSL).\n
        Print multiple lines on the same line.

        #### Args:
            - Text (str): Text to be printed.
            - LastLine (bool, optional): If True, when you print after it, it will print in new line.

        #### Returns:
            None
    """
    
    if (bool(LastLine)):
        sys.stdout.write("\r\033[K" + Text + "\n")
    else:
        sys.stdout.write("\r\033[K" + Text)
    
    return None

class PackageManager:
    """
        ## Main class of the module.

        ### Variables:\n
            >>> AccessiblePackages
            >>> AnalyzedPackages
            >>> InstalledPackages
            >>> RequiredPackages
            >>> STDPackages
        
        ### Functions:\n
            None
        
        ### Public Methods:\n
            >>> AutoImportMissings(self)
            >>> ExportRequirements(self)
            >>> GetImportedPackages(self)
            >>> InstallPackage(self)
            >>> UpgradePIP(self)
        
        ### Private Methods:\n
            >>> __GetInstalledPackages(self)
            >>> __GetImportedPackages(self)
            >>> __GetMissingPackages(self)
            >>> __GetPackagePath(self)
            >>> __GetRequiredPackages(self)
            >>> __InstallPackage(self)
            >>> __UpgradePIP(self)
    """

    def __init__(self) -> None:
        """
            ### Constructor gets the main script file path and store class-scope variables
        """

        # Class Variables
        self.__mainScript = sys.modules['__main__']
        self.__mainScriptPath = str((self.__mainScript.__file__).replace('\\', '/'))

        # User Accessable Variable
        self.STDPackages = tuple(list(sys.stdlib_module_names) + list(sys.builtin_module_names))
        self.InstalledPackages = tuple(self.__GetInstalledPackages())
        self.AccessiblePackages = tuple(self.STDPackages + self.InstalledPackages)
        self.RequiredPackages = tuple()
        self.AnalyzedPackages = set()

        # User Accessable Methods
        self.InstallPackage = lambda PackageName, PackageVersion, Verbose: \
            self.__InstallPackage(PackageName=str(PackageName), PackageVersion=str(PackageVersion), Verbose=bool(Verbose))
        
        self.GetImportedPackages = lambda PackagePath, IncludeDynamicImports, StrictSearch, Verbose: \
            self.__GetImportedPackages(PackagePath=PackagePath, IncludeDynamicImports=IncludeDynamicImports, StrictSearch=StrictSearch, Verbose=Verbose)

        self.UpgradePIP = lambda Verbose: self.__UpgradePIP(Verbose=bool(Verbose))

    ### INFORMATION RETRIVERS

    def __GetPackagePath(self, PackageName: str, IgnoreBuiltins: bool = False, Verbose: bool = False) -> str | None:
        """
            ### Searches and returns a package path using its name.

            #### Args:
                - PackageName (str): Target package name.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - str | None: Package file path if package exist, else, None will be returned.
        """

        # Print progress to stdout
        if (bool(Verbose)): print(f"Locating package '{PackageName}'...")
        
        # Load module without executing it
        module = importlib.util.find_spec(str(PackageName))

        # Check if module is found
        if (hasattr(module, 'origin')):
            module_path = str(module.origin)

            # Check if module has 'origin' has a value which is not None
            if (str(module_path) != 'None'):
                module_path = module_path
            
            # Check if module is not normally included in 'sys.path' (has 'submodule_search_locations' value)
            # and try to read its path
            elif (str(module_path) == 'None') \
            and (str(module.submodule_search_locations) != 'None'):
                # Collecting path domain
                namespace = module.submodule_search_locations
                # Concatenate path domain
                module_path = str(f'{namespace._path[0]}/{namespace._name}.py')
            
            else:
                module_path = None


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

    def __GetInstalledPackages(self, Verbose: bool = False) -> tuple:
        """
            ### Collects all packages (built-ins & installed) accessible by Python.

            #### Args:
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - tuple: Names of all accessible packages (installed & built-ins).
        """

        # Print progress to stdout
        if (bool(Verbose)): print("Collecting Installed Packages...")

        # Retriving all 'sys' accessible installed packages
        packages = [pkg.split('.')[0] for pkg in list(sys.modules) if pkg not in self.STDPackages]
        # print(set(packages))
        # exit()

        # Retriving other packages inaccessible by 'sys'
        # Collect package names using '..iter_modules()'
        # Do not use '..walk_packages()'; it is slower than '..iter_modules()' because it retrives submodules as well
        # 'pkgutil.walk_packages()' returns objects of modules, so we need to collect 'pkg.name'
        for pkg in pkgutil.iter_modules():
            # Append to packages list
            packages.append(pkg.name)
        
        # Ensuring collected packages do not contain built-ins or std_libs as well as setting and sorting packages
        packages = sorted(set([pkg for pkg in packages if pkg not in self.STDPackages]))

        return tuple(packages)

    def __GetImportedPackages(self, PackagePath: str, IncludeDynamicImports: bool = True, StrictSearch: bool = False, Verbose: bool = False) -> tuple:
        """
            ### Collects imported packages from python code.\n
            #### IMPORT STATEMENTS INSIDE LOOPS CANNOT BE ACCESSED BY 'IncludeDynamicImports'

            #### Args:
                - PackagePath (str): Python file path to be analyzed for imports.
                - IncludeDynamicImports (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - StrictSearch (bool, optional): If enabled, only nodes containing the word 'import' in their source code will be processed. Preferably keep it to default. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - tuple: Names of imported modules by the code provided. If no imported modules found, an empty tuple will be returned.
        """
        
        if (bool(Verbose)): PSL(f"Collecting packages imported by '{os.path.basename(PackagePath)}'")

        def __getPackageSource(FilePath: str) -> str:
            """
                Reads source code from Python file

                #### Args:
                    - PackagePath (str): Python file absoulte path

                ### Raises:
                    - FileNotFoundError: If provided path is invalid or not a file

                #### Returns:
                    - str: Target file content
            """
            # Check if provided parameter is a file path
            if (os.path.isfile(FilePath)):
                # Open and read content then return it
                with open(file=PackagePath, mode='r', errors='ignore') as source:
                    src_code = source.read()

            # If provided parameter is not a file, raise 'FileNotFoundError'
            else:
                raise FileNotFoundError(f'{FilePath} could not be found!')
            
            return src_code

        def __handleImport(Node: ast.Import) -> tuple:
            """
                Collects packages names imported by 'import ...'

                #### Args:
                    - Node (ast.Import): AST Import type node object

                #### Returns:
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

                #### Args:
                    Node (ast.ImportFrom): AST ImportFrom type node object

                #### Returns:
                    tuple: Imported packages names
            """
            
            # Assure 'Node' type to process it
            if (type(Node) == ast.ImportFrom):
                # Collect packages names from From...Import Nodes
                module_name = Node.module

                # Check if module level, whether it is a parent directory or not 'e.g. from . import pkg ==> level 1' | 'e.g. from module import pkg ==> level 0'
                # MUST CHECK (__name__ not in module_name) == True to avoid issues with relative imports of the package
                ## although this will not bring PackageManager name in packages list but it could be added manually later if need .
                if (int(Node.level) == 0) \
                and (__name__ not in module_name):
                    pkg = [getPkgName(module_name)]
                else:
                    # If module is a parent directory, skip (pass as None)
                    pkg = [None]

            else:
                # Return (None) if this is not an ImportFrom Node
                pkg = [None]
            
            return tuple(pkg)

        def __handleAssign(Node: ast.Assign) -> tuple:
            """
                Collects packages names imported dynamically by assignment 'e.g. variable = __import__(module)'

                #### Args:
                    - Node (ast.Assign): AST Assign type node object

                #### Returns:
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
                    if ((hasattr(Node_func, 'id')) and (Node_func.id in ['__import__', 'import_module'])) \
                    or ((hasattr(Node_func, 'value')) and (Node_func.value.id in ['importlib'])):
                        
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

                #### Args:
                    - Node (ast.Expr): AST Expr type node object

                #### Returns:
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
        # and if pkg is somehow pass as None, return it as it is.
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
            if   (type(node) == ast.Import):      initial_imports.update(__handleImport(Node=node))
            elif (type(node) == ast.ImportFrom):  initial_imports.update(__handleImportFrom(Node=node))
            elif (type(node) == ast.Assign):      dynamic_imports.update(__handleAssign(Node=node))
            elif (type(node) == ast.Expr):        dynamic_imports.update(__handleExpr(Node=node))
            # 'else' here is set to pass to ignore every other node type
            else: pass
        
        # If 'IncludeDynamicImports' is enabled, packages imported dynamically while the code runs will be collected.
        # This includes packages imported by '__import__()' and 'importlib.import_module()'.
        # IMPORTS STATEMENTS INSIDE LOOPS WILL NOT BE PROCESSED
        if (bool(IncludeDynamicImports)):
            imports = set().union(initial_imports, dynamic_imports)
        else:
            imports = initial_imports

        # Check if imports has content. if yes, sort them, if no, set imports to None to indicate No Imports
        if (imports):
            # Neglecting every 'None' element
            imports = [pkg for pkg in imports if str(pkg) != 'None']
            # Sorting the imports list
            imports = list(sorted(imports))
        else:
            imports = tuple()

        #endregion

        return tuple(imports)

    def __GetRequiredPackages(self, PackagePath: str, IncludeDynamicImports: bool = True, IncludePrivatePackages: bool = False, DeepScan: bool = False, Verbose: bool = False) -> tuple:
        """
            ### Collects all imported packages by a script and (optionally) imports of its imports, \
            then tests wheather these packages are built-ins and std-lib packages or not.\n

            #### If you are working on a project with many relative imports, it is prefered to Enable 'DeepScan'

            #### Args:
                - PackagePath (str): Python file path to be analyzed for imports.
                - IncludeDynamicImports (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - IncludePrivatePackages (bool, optional): If enabled, packages names starting with '_' will be collected. PREFERABLY, DON'T CHANGE DEFAULT. Defaults to False.
                - DeepScan (bool, optional): Scans imported scripts in target script for their own imports. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - tuple: Packages imported but not installed or cannot be imported.
        """

        # Collecting imported packages by module given its path 'PackagePath'
        imported_packages = self.__GetImportedPackages(PackagePath=PackagePath, IncludeDynamicImports=IncludeDynamicImports, StrictSearch=True, Verbose=Verbose)
        # Getting project packages (packages in 'sys.modules' but not in 'sys.stdlib_module_names' or 'sys.builtin_module_names') or packages that are not installed
        project_main_imports = [pkg for pkg in imported_packages if pkg not in self.STDPackages]
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
                if (pkg not in self.AnalyzedPackages):
                    # Adding 'pkg' to recursion termination list so it is not processed twice
                    self.AnalyzedPackages.add(pkg)

                    # Locating target 'pkg' path
                    pkg_path = self.__GetPackagePath(PackageName=pkg, IgnoreBuiltins=True)

                    # Check if package has a path (not a built-in nor does not exist)
                    if (str(pkg_path) != 'None'):
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

        # Another filtration of 'requried_packages', removing built-in packages and packages already in 'sys.stdlib_module_names' (a.k.a. 'self.STDPackages')
        required_packages = sorted(set([pkg for pkg in required_packages if pkg not in self.STDPackages]))

        # Selects either to include private modules (modules names starts with '_') in required packages or not
        if (bool(IncludePrivatePackages)):
            pass
        else:
            # If 'IncludePrivatePackages' is set to 'False', then private packages (packages start with _) will be excluded
            required_packages = [pkg for pkg in required_packages if (pkg.startswith('_') == False)]

        # Assigning return value to self.Variable
        self.RequiredPackages = tuple(required_packages)

        return tuple(required_packages)

    def __GetMissingPackages(self, PackagePath: str, IncludeDynamicImports: bool = True, IncludePrivatePackages: bool = False, DeepScan: bool = False, Verbose: bool = False) -> tuple:
        # Collecting required packages by the project that are neither built-ins nor std_lib
        required_packages = self.__GetRequiredPackages(PackagePath=PackagePath, IncludeDynamicImports=IncludeDynamicImports, IncludePrivatePackages=IncludePrivatePackages, DeepScan=DeepScan, Verbose=Verbose)
        # Getting missing packages (packages not accessible in anyway)
        missed_main_imports = [pkg for pkg in required_packages if pkg not in self.AccessiblePackages]

        return tuple(missed_main_imports)

    ### ACTION MAKERS

    def __InstallPackage(self, PackageName: str, PackageVersion: str = "latest", Verbose: bool = False) -> dict:
        """
            ### Installs specific package with desired version. If 'PackageVersion' == None -> latest version will be installed.

            #### Args:
                - PackageName (str): Exact package name to be installed.
                - PackageVersion (str, optional): Exact package version to be installed. Comparator operators are not allowed! Defaults to "latest".
                - Verbose (bool, optional): Prints function progress.

            #### Returns:
                - dict: Return keys = ReturnMessage, ExitCode, ExitMessage
        """

        # Check package version to be installed
        if (PackageVersion.replace('.','').isdigit()):
            target_package = f'{str(PackageName)}=={str(PackageVersion)}'
        else:
            target_package = str(PackageName)

        # Print progress to stdout
        if (bool(Verbose)): PSL(f'Attempting to install "{target_package}"...')

        # Setup a command to install the package
        # Using 'sys.executable' to ensure that we install the package for the same version and location of running Python
        installation_command = f'"{sys.executable}" -m pip install {str(target_package)}'
        installation_process = subprocess.Popen(str(installation_command), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Collect return messages from executed command
        execution_message = str(installation_process.communicate())
        execution_exit_code = int(installation_process.wait())

        # Define function return messages based on execution return message
        if (execution_exit_code == 0):      # 0 -> Successful Exit Code
            return_message = f'"{target_package}" has been installed successfully!'
        elif (execution_exit_code == 1):    # 1 -> Successful Exit Code
            return_message = f'"{target_package}" was not recognized, please consider installing it manually!'
        else:                               # Other -> Unknown Exit Code
            return_message = f'Unexpected exit code ({execution_exit_code}) returned while installing "{target_package}"'

        # Print progress to stdout
        if (bool(Verbose)): PSL(return_message, LastLine=True)
        
        return dict(
                {
                "ReturnMessage" : return_message,
                "ExitCode"      : execution_exit_code,
                "ExitMessage"   : execution_message
                }
            )

    # def __RemovePackage(self, PackageName: str, PackageVersion = "latest", Verbose = False):
    #     pass

    # def __UpgradePackage(self, PackageName: str, PackageVersion = "latest", Verbose = False):
    #     pass

    def __UpgradePIP(self, Verbose: bool = False) -> int:
        """
            ### Upgrade pip if an upgrade is available.

            #### Args:
                - Verbose (bool, optional): Prints function progress.

            #### Returns:
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
        if (bool(Verbose)): PSL(f'Attempting to upgrade pip...')

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

        elif (execution_exit_code == 1):  # 1 -> Error Exit Code
            return_code = 1
            return_message = 'pip was not upgraded, please consider upgrading pip manually!'

        else:                           # Other -> Unknown Exit Code
            return_code = 2
            return_message = 'Unexpected exit code!'

        # Print progress to stdout
        if (bool(Verbose)): PSL(f'{return_message}\n{new_pip_message}', LastLine=True)

        return int(return_code)

    ### USER ACCESSIBLE

    # UNDER DEV
    def AutoImportMissings(self, IncludeDynamicImports: bool = True, DeepScan: bool = True, UpgradePIP: bool = False, Verbose: bool = False) -> bool:
        """
            ### Automatically analysis '__main__' script, update PIP, and installs required packages if missing.

            #### Args:
                - IncludeDynamicImports (bool, optional): If enabled, packages imported dynamically while the code runs will be collected. Defaults to True.
                - DeepScan (bool, optional): Scans imported scripts in target script for their own imports. Defaults to True.
                - UpgradePIP (bool, optional): Optionally upgrade PIP before installing required packages. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - bool: returns True if all packages were successfully installed, else, False.
        """

        failed_packages = set()

        missing_packages = self.__GetMissingPackages(PackagePath=self.__mainScriptPath, IncludeDynamicImports=IncludeDynamicImports, DeepScan=DeepScan, Verbose=Verbose)

        if (bool(UpgradePIP)): self.__UpgradePIP(Verbose=Verbose)

        for ind, pkg in enumerate(missing_packages, 1):
            if (bool(Verbose)): print(f"\nInstalling Packages {ind}/{len(missing_packages)}")
            
            retry_counter = 1
            while (retry_counter > 0):
                pkg_installer = self.__InstallPackage(PackageName=pkg, Verbose=Verbose)

                if (pkg_installer['ExitCode'] == 0):
                    if (pkg in failed_packages):
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

                if (decision == 'Y'):
                    print()
                    return False
                elif (decision == 'n'):
                    exit()
                else:
                    print('Invalid input!')
        elif (str(missing_packages) == 'None') \
        or (len(missing_packages) == 0):
            print(f'\nNo missing required packages were found!\n')
        
        else:
            print(f'\nRequired missing packages have been installed successfully!\n')

    # UNDER DEV
    def ExportRequirements(self, ExportTo__main__Dir: str | bool = False) -> dict:
        """
            ### Exports a requirement file contains modules required by the project which this method is called in.

            #### Args:
                - ExportTo__main__Dir (str | bool, optional): This argument has three modes as explained below.\n
                    * Mode 1: If set to bool(False), will not export to file and will only return a dict of packages and their versions. (Default)
                    * Mode 2: If set to bool(True), will export requirements.txt file to parent directory of __main__ file.
                    * Mode 3: If set to a valid directory str(path), will export requirement.txt to specified directory.

            #### Returns:
                - dict: Dict of packages names and versions (possible keys for each value => 'name', 'version')
        """

        project_dir_path = os.path.dirname(self.__mainScriptPath)
        pkgs = self.__GetRequiredPackages(self.__mainScriptPath, DeepScan=True)
        reqs = []

        for pkg in pkgs:
            if project_dir_path not in self.__GetPackagePath(pkg):
                reqs.append(pkg + "==" + importlib.metadata.version(pkg))
            else:
                pass
        
        reqs.insert(0, __name__ + '==' + __version__)
        
        reqs_dict = {pkg: {'name': pkg, 'version': ver} for pkg, ver in [req.split('==') for req in reqs]}

        if (bool(os.path.isdir(ExportTo__main__Dir))):
            project_dir_path = ExportTo__main__Dir.replace('"', '').replace("'", '').replace('\\', '/')
        else:
            pass
            
        
        if (bool(os.path.isdir(project_dir_path))) \
        and (bool(ExportTo__main__Dir)):
            with open(f'{project_dir_path}/requirements-by-{os.path.basename(self.__mainScript.__file__)}.txt', 'w') as req_file:
                for pkg in reqs:
                    req_file.write(pkg + '\n')
        else:
            pass
            
        return reqs_dict

# UNDER DEVELOPMENT
class AutoImporter:
    """
        Auto Imports missing required modules.\n
        This class is riggered by importing it.
    """
    # Call AutoImportMissings as a variable value so that it is triggered as soon as the class AutoImporter is imported
    if __name__ != '__main__':
        PackageManager().AutoImportMissings(IncludeDynamicImports=True, DeepScan=True, UpgradePIP=False, Verbose=True)
        
