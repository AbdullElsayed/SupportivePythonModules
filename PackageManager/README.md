<br>

# Package Manager

## Description
This module allows you to automatically import missing libraries (modules) that are required by a script without the need to any other installation or a requirement file. And you can also use this module to export requirements file specific to your project without dealing with the hustle of creating a venv to collect requirements.

## Status
<div align="center">

[![Status](https://img.shields.io/badge/Status-Production-brightgreen)](https://github.com/AbdullElsayed/SupportivePythonModules/tree/master/PackageManager)
[![MIT License](https://img.shields.io/github/license/AbdullElsayed/SupportivePythonModules?label=License)](https://github.com/AbdullElsayed/SupportivePythonModules/blob/main/LICENSE)
[![Latest Version](https://img.shields.io/github/v/release/AbdullElsayed/SupportivePythonModules?display_name=tag&include_prereleases&label=Latest%20Version&sort=semver&color=crimson)](https://github.com/AbdullElsayed/SupportivePythonModules/releases/latest)
[![Latest Release](https://img.shields.io/github/v/release/AbdullElsayed/SupportivePythonModules?display_name=release&include_prereleases&label=Latest%20Release&sort=semver)](https://github.com/AbdullElsayed/SupportivePythonModules/releases/latest)

</div>

## Getting Started
### Fact-Sheet
|       Info      	|                                                                                                         Value                                                                                                         	|
|:---------------:	|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:	|
| Package Content 	|                                                                                                     ![Files Count](https://img.shields.io/github/directory-file-count/AbdullElsayed/SupportivePythonModules/PackageManager?color=purple&label=Files)                                                                                                     	|
|     Built on    	|                                                                          ![Python Version](https://img.shields.io/badge/Python-v3.10-ffd43b)                                                                          	|
|    Tested on    	|                                                                    ![Python Version](https://img.shields.io/badge/Python-v3.9%20\|%20v3.10-ffd43b)                                                                    	|
|    OS Support   	| ![Python Version](https://img.shields.io/badge/Windows-≥8.1-357EC7) ![Python Version](https://img.shields.io/badge/macOS-≥10.9-A2AAAD) ![Python Version](https://img.shields.io/badge/Linux-Dont%20be%20silly-E95420) 	|

### Prerequisites
![Prerequisites](https://img.shields.io/badge/-None-brightgreen)

### Installation
![Installation](https://img.shields.io/badge/-Not_Required-brightgreen)

## Usage
- ### Basic Usage
    ***WARNING: PackageManager MUST ALWAYS BE THE FIRST MODULE TO BE IMPORTED!***

    No need to call any function, instentiate a class, or any other actions! Just add the import line and everything will be done automatically!
    ```Python
    from PackageManager import AutoImporter
    ```

- ### Advanced Usage
    ***WARNING: DON'T USE THE SAME INSTANCE TO CALL MULTIPLE METHODS UNTIL WE FIX THE ISSUES BEHIND IT!***

    If you wish to customize the process, you can call 'AutoImportMissings()' method from 'PackageManager' class.
    ```Python
    from PackageManager import PackageManager

    PackageManager().AutoImportMissings(IncludeDynamicImports: bool = True, DeepScan: bool = True, UpgradePIP: bool = False, Verbose: bool = False)
    ```
    
    You can also use other provided methods to perform various operations.
    ```Python

    PackageManager().ExportRequirements(ExportTo__main__Dir: str | bool = False)

    PackageManager().GetImportedPackages(PackagePath: str, IncludeDynamicImports: bool = True, StrictSearch: bool = False, Verbose: bool = False)

    PackageManager().InstallPackage(PackageName: str, PackageVersion: str = "latest", Verbose: bool = False)

    PackageManager().UpgradePIP(Verbose: bool = False)
    ```
    
    For further information, please refer to [Documentation](https://abdullelsayed.github.io/SupportivePythonModules/PackageManager_Doc.html)

## Authors

- [Abdullrahman Elsayed](https://www.github.com/AbdullElsayed)

## Contact

For issues, inquires, or support, please contact me:

[![GitHub](https://img.shields.io/badge/GitHub-%40AbdullElsayed-black)](https://github.com/AbdullElsayed/)

[![Email](https://img.shields.io/badge/Email-abdull15199%40gmail.com-black)](mailto:abdull15199.gmail.com)

## Licenses

All projects in this repository lay under [MIT License](https://github.com/AbdullElsayed/SupportivePythonModules/blob/main/LICENSE)

