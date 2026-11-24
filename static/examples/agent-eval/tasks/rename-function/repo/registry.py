"""Parsers looked up by name at run time."""
import importlib

PARSERS = {"timestamp": "timeutil:parse_ts"}


def get_parser(kind):
    module_name, function_name = PARSERS[kind].split(":")
    return getattr(importlib.import_module(module_name), function_name)
