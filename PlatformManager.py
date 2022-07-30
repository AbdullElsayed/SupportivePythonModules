#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Platform Manager v1.0.3
    \n
    MISSING DESCRIPTION!
    
    .. include:: ./README.md
"""

############ AUTHOURSHIP & COPYRIGHTS ############
__author__      = "Abdullrahman Elsayed"
__copyright__   = "Copyright 2022, Supportive Python Modules Project"
__credits__     = "Abdullrahman Elsayed"
__license__     = "MIT"
__version__     = "1.0.3"
__maintainer__  = "Abdullrahman Elsayed"
__email__       = "abdull15199@gmail.com"
__status__      = "Development"
# __doc__         = ""
##################################################

import platform, sys, types

class CrossPlatform:
    """
        ## Contains Methods That Short-hands Cross-Platform Execution.

        ### Variables:\n
            >>> PlatformIsSupported
            >>> SupportedPlatforms
        
        ### Functions:\n
            None
        
        ### Public Methods:\n
            >>> Function(self)
            >>> PlatformInformation(self)
        
        ### Private Methods:\n
            None
    """

    def __init__(self, SupportedPlatforms : tuple = ('Windows', 'Linux', 'Darwin')) -> None:
        self.SupportedPlatforms = tuple(SupportedPlatforms)
        self.PlatformIsSupported = bool(self.PlatformInformation() != None)

    def PlatformInformation(self) -> dict | None:
        """
            ### Collects Operating System and Python Build Information (OS Name, Release, Python Version, etc.).

            #### Args:\n
                None

            #### Returns:
                - dict | None: System information dictionary or None if kernel is not supported.
                    Returned dict has the following keys:
                    * All
                    * Arch
                    * Distro (Linux Only)
                    * DistroBase (Linux Only)
                    * DistroVersion (Linux Only)
                    * PlatformName
                    * Machine
                    * PythonVersion
                    * Release
                    * Version
        """

        # region: OS 
        # Collecting system information
        sys_info = platform.uname()

        # Define 'SupportedPlatforms' by this software
        self.SupportedPlatforms = tuple(self.SupportedPlatforms)

        # Cross-Platform Information
        self.PlatformName   = sys_info.system
        self.Release        = sys_info.release
        self.Version        = sys_info.version
        self.Machine        = sys_info.machine
        self.Arch           = 64 if bool(sys.maxsize > (2 ** 32)) else 32
        self.PythonVersion  = platform.python_version()

        # Linux Specific Information
        self.Distro         = None
        self.DistroBase     = None
        self.DistroVersion  = None

        # endregion

        # Check Operating System Support
        if  (self.PlatformName in self.SupportedPlatforms):
            # Detect Operating System
            if (self.PlatformName == 'Linux'):
                # Linux specific command to get distribution information
                distro_info = platform.freedesktop_os_release()

                self.Distro         = distro_info['NAME']
                self.DistroBase     = distro_info['ID_LIKE']
                self.DistroVersion  = distro_info['VERSION_ID']
            
            elif (self.PlatformName == 'Darwin'):
                # MacOS specific command to get distribution information
                distro_info = platform.mac_ver()

                print('NOT YET DEVELOPED', distro_info)

                # self.Distro         = distro_info['NAME']
                # self.DistroBase     = distro_info['ID_LIKE']
                # self.DistroVersion  = distro_info['VERSION_ID']
                pass

            elif (self.PlatformName == 'Windows'):
                # Windows specific command to get distribution information
                distro_info = platform.win32_ver()

                print('NOT YET DEVELOPED', distro_info)

                # self.Distro         = distro_info['NAME']
                # self.DistroBase     = distro_info['ID_LIKE']
                # self.DistroVersion  = distro_info['VERSION_ID']
                pass

            # TODO: an unlisted, supported platform error raise to be triggered if code reaches this 'else'
            else:
                print(f'RAISE: UN-LISTED, SUPPORTED PLATFORM ERROR!')

        else:
            print(f'{self.PlatformName} IS NOT YET SUPPORTED!')
            return None

        # Combine all system information into one variable named 'self.All'
        self.All = {
            # Cross-Platform Information
            'Platform'      : self.PlatformName,
            'Release'       : self.Release,
            'Version'       : self.Version,
            'Machine'       : self.Machine,
            'Arch'          : self.Arch,
            'PythonVersion' : self.PythonVersion,
            
            # Linux Specific Information
            'Distro'        : self.Distro,
            'DistroBase'    : self.DistroBase,
            'DistroVersion' : self.DistroVersion,
        }

        return dict(self.All)

    def Function(self, LinuxFunction : types.FunctionType | None, DarwinFunction : types.FunctionType | None, WindowsFunction : types.FunctionType | None) -> types.FunctionType | None:
        """
            ### Picks up a function out of provided functions that meets the running OS.

            #### Args:
                - LinuxFunction (types.FunctionType | None): A function to run on Linux kernel.
                - DarwinFunction (types.FunctionType | None): A function to run on Darwin kernel.
                - WindowsFunction (types.FunctionType | None): A function to run on Windows kernel.

            #### Returns:
                - types.FunctionType | None: Selected function based on running OS.
        """
        
        ### DON'T THINK ABOUT 'locals()' AND 'ast.literal_eval()' METHOD. \
        ### IT LOOKS PRETTIER THIS WAY

        # Check current OS and return the function corresponding to it
        if  (self.PlatformName == 'Linux') \
        and (LinuxFunction != None):
            return LinuxFunction
        
        elif (self.PlatformName == 'Darwin') \
        and  (DarwinFunction != None):
            return DarwinFunction

        elif (self.PlatformName == 'Windows') \
        and  (WindowsFunction != None):
            return WindowsFunction
        
        # This 'else' must never be reached under normal circumstances \
        # since SupportedPlatforms is validated in 'PlatformInformation' class
        else:
            print("UN-SUPPORTED OS!")
            return None
