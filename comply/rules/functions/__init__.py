# coding=utf-8

from comply.rules.functions.no_redundant_const import NoRedundantConst
from comply.rules.functions.too_many_params import TooManyParams
from comply.rules.functions.split_by_name import SplitByName
from comply.rules.functions.function_too_long import FunctionTooLong
from comply.rules.functions.too_many_functions import TooManyFunctions
from comply.rules.functions.no_redundant_name import NoRedundantName
from comply.rules.functions.no_redundant_size import NoRedundantSize

__all__ = [
    "NoRedundantConst",
    "TooManyParams",
    "SplitByName",
    "FunctionTooLong",
    "TooManyFunctions",
    "NoRedundantName",
    "NoRedundantSize"
]
