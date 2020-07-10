"""Miscellaneous parsing utilities."""
import re
import pandas as pd


def _parse_vals(values: str) -> dict:
    if isinstance(values, list) and len(values) == 1:
        values = values[0]
    pattern = re.compile('(?P<key>[0-9.]+) (?P<value>[a-z-A-Z0-9. ]+)')
    mapping = {
        float(re.match(pattern, value).group("key")): re.match(pattern, value).group('value')
        for value in values.splitlines()}
    mapping = {f'{key:.1f}': value for key, value in mapping.items()}
    return mapping


def type_variable(variable: dict, dataset: pd.DataFrame) -> str:
    if variable['value'] == 'numeric':
        if 'derivation' in variable:
            return 'Scale'
        elif 'values' in variable:
            return 'ordinal'
        else:
            return 'interval'
    elif variable['value'] == 'string':
        if 'levels' in variable:
            return 'categorical'
        else:
            return 'open'


def natural_key(string_: str) -> list:
    """Sort strings in human order.

    See http://www.codinghorror.com/blog/archives/001018.html
    """
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
