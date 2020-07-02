def _parse_vals(values):
    if isinstance(values, list) and len(values) == 1:
        values = values[0]
    mapping = {f'{float(value.split()[0]):.1f}':value.split()[1] for value in values.splitlines()}
    return mapping