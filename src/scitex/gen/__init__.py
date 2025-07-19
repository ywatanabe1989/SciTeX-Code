#!/usr/bin/env python3
"""Scitex gen module."""

from ._DimHandler import DimHandler
from ._TimeStamper import TimeStamper
from ._alternate_kwarg import alternate_kwarg
from ._cache import cache
from ._check_host import check_host, is_host, verify_host
from ._ci import ci
from ._close import close, running2finished
from ._embed import embed
from ._inspect_module import inspect_module
from ._is_ipython import is_ipython, is_script
from ._less import less
from ._list_packages import list_packages, main
from ._mat2py import dir2npy, keys2npa, mat2dict, mat2npa, mat2npy, public_keys, save_npa
from ._norm import clip_perc, to_01, to_nan01, to_nanz, to_z, unbias
from ._paste import paste
from ._print_config import print_config, print_config_main
from ._shell import run_shellcommand, run_shellscript
from ._src import src
from ._start import start
from ._symlink import symlink
from ._symlog import symlog
from ._tee import Tee, main, tee
from ._title2path import title2path
from ._title_case import main, title_case
from ._to_even import to_even
from ._to_odd import to_odd
from ._to_rank import to_rank
from ._transpose import transpose
from ._type import ArrayLike, var_info
from ._var_info import ArrayLike, var_info
from ._wrap import wrap
from ._xml2dict import XmlDictConfig, XmlListConfig, xml2dict
from ._detect_environment import detect_environment, get_output_directory, is_notebook
from ._get_notebook_path import get_notebook_path, get_notebook_name, get_notebook_directory

__all__ = [
    "ArrayLike",
    "ArrayLike",
    "DimHandler",
    "Tee",
    "TimeStamper",
    "XmlDictConfig",
    "XmlListConfig",
    "alternate_kwarg",
    "cache",
    "check_host",
    "ci",
    "clip_perc",
    "close",
    "dir2npy",
    "embed",
    "inspect_module",
    "is_host",
    "is_ipython",
    "is_script",
    "keys2npa",
    "less",
    "list_packages",
    "main",
    "main",
    "main",
    "mat2dict",
    "mat2npa",
    "mat2npy",
    "paste",
    "print_config",
    "print_config_main",
    "public_keys",
    "run_shellcommand",
    "run_shellscript",
    "running2finished",
    "save_npa",
    "src",
    "start",
    "symlink",
    "symlog",
    "tee",
    "title2path",
    "title_case",
    "to_01",
    "to_even",
    "to_nan01",
    "to_nanz",
    "to_odd",
    "to_rank",
    "to_z",
    "transpose",
    "unbias",
    "var_info",
    "var_info",
    "verify_host",
    "wrap",
    "xml2dict",
    "detect_environment",
    "get_output_directory",
    "is_notebook",
    "get_notebook_path",
    "get_notebook_name",
    "get_notebook_directory",
]
