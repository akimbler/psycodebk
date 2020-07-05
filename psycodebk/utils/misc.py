"""Miscellaneous parsing utilities."""
import re
import pandas as pd


def _parse_vals(values: str) -> dict:
    if isinstance(values, list) and len(values) == 1:
        values = values[0]
    mapping = {
        f'{float(x.split()[0]):.1f}': ' '.join(x.split()[1:]) for x in values.splitlines()}
    return mapping


def type_variable(variable: dict, dataset: pd.DataFrame) -> str:
    if 'derivation' in variable and set(variable.keys()).issuperset({'minValue', 'maxValue'}):
        return 'Scale'
    elif set(variable.keys()).issuperset({'minValue', 'maxValue'}) and 'values' in variable:
        return 'ordinal'
    elif set(variable.keys()).issuperset({'minValue', 'maxValue'}) and 'values' not in variable:
        return 'interval'
    elif 'values' in variable:
        return 'categorical'
    elif dataset[variable['name']].dtype in ['float64', 'int64']:
        return 'interval'
    else:
        return 'open'


def get_antecedents(variable: dict) -> list:
    variables = ' '.join([value for _, value in variable['derivation'].items()])
    var_names = sorted(list(set(re.findall('([a-zA-Z_0-9]{5,})', variables))), key=natural_key)
    return var_names


def natural_key(string_: str) -> list:
    """Sort strings in human order.

    See http://www.codinghorror.com/blog/archives/001018.html
    """
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
