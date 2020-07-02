"""Miscellaneous parsing utilities."""


def _parse_vals(values):
    if isinstance(values, list) and len(values) == 1:
        values = values[0]
    mapping = {
        f'{float(x.split()[0]):.1f}': x.split()[1] for x in values.splitlines()}
    return mapping
