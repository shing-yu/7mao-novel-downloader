"""
SL-Novel-Downloader(Qimao Edition), A downloader for www.qimao.com and com.kmxs.reader app novels.
Copyright (C) 2024  shing-yu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from colorama import Fore, Style, init
import os
import platform

__version__ = "v1.0.2"  # SLQimao Core Version

init(autoreset=True)

red = Fore.RED + Style.BRIGHT
yellow = Fore.YELLOW + Style.BRIGHT
green = Fore.GREEN + Style.BRIGHT

nullproxies = {
    "http": None,
    "https": None
}

version_list = [
    '73720', '73700',
    '73620', '73600',
    '73500',
    '73420', '73400',
    '73328', '73325', '73320', '73300',
    '73220', '73200',
    '73100', '73000', '72900',
    '72820', '72800',
    '70720', '62010', '62112',
]

key = 'd3dGiJc651gSQ8w1'  # sign_key


def clear_screen():
    os.system('cls') if platform.system() == 'Windows' else os.system('clear')
