"""
    Package Manager v1.0.0
"""

import inspect, pkgutil, subprocess, sys

class PackageManager:
    ### DONE
    def __init__(self) -> None:
        """
            Constructor gets the main script file path

            Returns:
                None: None
        """

        self.MainScript = sys.modules['__main__']
        self.MainScriptPath = str(self.MainScript.__file__)
        self.MainScriptCode = list(inspect.getsourcelines(self.MainScript)[0])
        self.InstalledPackages = list(self.GetImportablePackages())
        self.RequiredPackages = list(self.GetRequiredPackages())

        return None
    
    ### DONE
    def GetRequiredPackages(self, Verbose = False) -> list:
        """
            Extracts imported packages from __main__ file.

            Args:
                Verbose (bool, optional): Prints function progress. Defaults to False.

            Returns:
                list: Required packages names. 
        """
        # Print progress to stdout
        if Verbose: print("Analyzing Main Script...")

        # Looing over __main__ source code lines
        required_packages = []
        
        for line in self.MainScriptCode:
            # Remove leading and trailing spaces and line breaksof each line
            line = line.lstrip(' ').rstrip(' ').rstrip('\n')
            
            # Selecting only 'import' lines
            if line.startswith(('import', 'from')):
                # Splitting 'import_lines' to extract packages names
                line = line.split(' ')
                # Removing commas between multiple one-line imports
                line = [word.replace(',', '') for word in line if word != ',']
                # Removing spaces and empty elements
                line = [word for word in line if word]
                
                # Extracting packages names from cleaned lines
                # Ignoring 'as' synonyms
                if 'as' in line:
                    line = line[:line.index('as')]
                else:
                    pass
                
                # If packages is imported, not a submodule (e.g. import package)
                if line[0] == 'import':
                    required_packages.extend(line[1:])
                # If a submodule is imported from a package (e.g. from package import module)
                else:
                    required_packages.extend(line[1:line.index('import')])
                
        # Collecting only packages names and ignoring submodules names
        required_packages = [pkg.split('.')[0] for pkg in required_packages]

        # Extracting only the packages that are not installed and deleting duplicates using 'set()'
        required_packages = [pkg for pkg in set(required_packages) if pkg not in self.InstalledPackages]

        ######################## KEEP IT FOR LATER ########################
        # finder_process = modulefinder.ModuleFinder()
        # finder_process.run_script(self.MainScriptPath)
        # imported_packages = list(finder_process.modules['__main__'].globalnames.keys())
        # required_packages = []
        # for pkg in imported_packages:
        #     if pkg not in self.InstalledPackages:
        #         required_packages.append(pkg)
        ######################## KEEP IT FOR LATER ########################

        return list(required_packages)

    ### DONE
    def GetImportablePackages(self, Verbose = False) -> list:
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

    ### DONE
    def InstallPackage(self, PackageName: str, PackageVersion = "latest", Verbose = False) -> dict:
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

    ### DONE
    def UpgradePIP(self, Verbose = False) -> int:
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

    ### DONE
    def LetMeRelax(self, UpgradePIP = False, Verbose = False) -> bool:
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
            if UpgradePIP: self.UpgradePIP(Verbose=Verbose)

            retry_counter = 3

            while retry_counter:

                for ind, pkg in enumerate(self.RequiredPackages, 1):
                    if Verbose: print(f"\nInstalling Packages {ind}/{len(self.RequiredPackages)}")
                    
                    pkg_installer = self.InstallPackage(PackageName=pkg, Verbose=Verbose)

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

# Setup auto importer
if __name__ != '__main__':
    PackageManager().LetMeRelax(UpgradePIP=True, Verbose=False)