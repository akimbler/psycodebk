"""Modules for constructing variable tabs."""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import shapiro, kurtosistest, skewtest
from ..utils.misc import _parse_vals
script_dir = Path(__file__).parent.parent
# from .viz.viz import plot_likert, plot_distribution


def construct_var_summtab(metadata: dict, dataset: pd.DataFrame, typing: str) -> (str, int):
    # value_labels = metadata['values'] if 'values' in metadata else 'None'
    if 'naValues' in metadata and typing in ['Scale', 'interval', 'ordinal']:
        missing_values = dataset[metadata['name']].replace(
            to_replace=metadata['naValues'], value=pd.NA).isnull().sum()
        desc = dataset[metadata['name']].replace(
            to_replace=metadata['naValues'], value=pd.NA).describe().to_frame().T
    elif 'naValues' in metadata and typing not in ['Scale', 'interval', 'ordinal']:
        missing_values = dataset[metadata['name']].replace(
            to_replace=[str(x) for x in metadata['naValues']], value=pd.NA).isnull().sum()
        desc = dataset[metadata['name']].replace(
            to_replace=[str(x) for x in metadata['naValues']], value=pd.NA).describe().to_frame().T
    else:
        missing_values = dataset[metadata['name']].isnull().sum()
        desc = dataset[metadata['name']].describe().T
    # total = len(dataset[metadata['name']])
    # complete = total - missing_values
    if typing in ['ordinal', 'interval', 'Scale']:
        if 'naValues' in metadata:
            var_data = dataset[metadata['name']].replace(
                to_replace=metadata['naValues'],
                value=np.nan)
        else:
            var_data = dataset[metadata['name']].replace(to_replace=[-88.0], value=pd.NA)
        var_data = var_data[var_data.notnull()]
        if var_data.shape[0] > 20:
            kurtosis = pd.Series(
                kurtosistest(var_data), index=['Kurtosis Z', 'Kurtosis p']).to_frame().T
        else:
            kurtosis = pd.Series(
                [pd.NA, pd.NA], index=['Kurtosis Z', 'Kurtosis p']).to_frame().T

        if var_data.shape[0] > 8:
            skewness = pd.Series(skewtest(var_data), index=['Skew Z', 'Skew p']).to_frame().T
        else:
            skewness = pd.Series([pd.NA, pd.NA], index=['Skew Z', 'Skew p']).to_frame().T

        if var_data.shape[0] > 2 and (var_data.max() - var_data.min()) > 0:
            normality = pd.Series(
                shapiro(var_data[var_data.notnull()]),
                index=['Normality W', 'Normality p']).to_frame().T
        else:
            normality = pd.Series(
                [pd.NA, pd.NA],
                index=['Normality W', 'Normality p']).to_frame().T
        kurtosis.rename({0: metadata['name']}, inplace=True)
        skewness.rename({0: metadata['name']}, inplace=True)
        normality.rename({0: metadata['name']}, inplace=True)
        desc = pd.concat([desc, kurtosis, skewness, normality], axis=1)
        return desc.round(3).to_html(classes='topazCells'), missing_values
    return desc.to_html(classes='topazCells'), missing_values


def produce_value_list(variable: dict) -> str:
    list_string = []
    for value, label in _parse_vals(variable['values']).items():
        list_string.append(f'<li><strong>{label.title()}</strong>: <em>{value}</em></li>')
    return '\n'.join(list_string)


"""
def construct_var_disttab(
        metadata: dict,
        dataset: pd.DataFrame,
        variable_type: str,
        dataset_description: dict):

    img_data = plot_distribution(
        dataset.replace(to_replace=metadata['naValues'], value=np.nan),
        metadata['name'],
        value_labels)
    var_table = var_table_header.format(
        variable_table=table_format,
        variable_name_upper=metadata['name'].upper(),
        missing_values=missing_values,
        variable_name=metadata['name'],
        description=metadata['description'],
        image_64_encode=img_data,
        variable_labels=value_labels)
    # TODO: Organize figure subplots on scale items by if different scales.
    if variable_type == 'derived':
        plot_data = dataset[metadata['derivation']['vars']]
        scale = {}
        # for x in dataset_description['variableMeasured']:
        #    if x['name'] in metadata['derivation']['vars'] and x['values'] not in scale:
        #        scale[x['values']] = [x['name']]
        #        scale.update(**_parse_vars(x['values']) for x in if x['name'] in }
        g = plot_likert(metadata, plot_data)
"""
