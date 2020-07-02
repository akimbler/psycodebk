"""Modules for constructing variable tabs."""
import pandas as pd
import numpy as np
from flask import render_template
import flask

app = flask.Flask('parsing', template_folder='../templates')


def construct_var_summarytab(metadata: dict, dataset: pd.DataFrame):
    if metadata['name'] not in dataset:
        continue
    value_labels = metadata['values'] if 'values' in metadata else 'None'
    desc = dataset[metadata['name']].describe()
    na_count = dataset[metadata['name']].replace(
        to_replace=metadata['naValues'], value=np.nan).isnull().sum()
    total = len(dataset[metadata['name']])
    complete = total - na_count
    table_format = ''
    if len(desc) == 8:
        (count, mean, std, minimum, p25, p50, p75, maximum) = desc
        with app.app_context():
            table_format = render_template(
            'var_summary_continous.html',
                variable_name=metadata['name'][0],
                desc=metadata['description'][0],
                labels=value_labels,
                missing=na_count,
                complete=complete,
                total=total,
                mean=mean,
                std=std,
                minimum=minimum,
                p25=p25,
                p50=p50,
                p75=p75,
                maximum=maximum)
    elif len(desc) == 4:
        with app.app_context():
            table_format = render_template(
                'var_summary_string.html',
                variable_name=metadata['name'],
                desc=metadata['description'],
                missing=na_count,
                complete=complete,
                total=total,
                mean=mean)
    else:
        continue

    return var_table


def construct_var_disttab(
        metadata: dict,
        dataset: pd.DataFrame,
        variable_type: str,
        dataset_description: dict):

    img_data = plot(
        dataset.replace(to_replace=metadata['naValues'], value=np.nan),
        metadata['name'],
        value_labels)
    var_table = var_table_header.format(
        variable_table=table_format,
        variable_name_upper=metadata['name'].upper(),
        missing_values=na_count,
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
