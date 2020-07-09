from psycodebk.parsing import parsing
from psycodebk.utils import misc
from psycodebk.viz import viz
import pandas as pd
from flask import render_template
import flask
from argparse import ArgumentParser
from pathlib import Path
import json
from ..__about__ import __version__


def get_parser():
    parser = ArgumentParser(
        description='psycodebk')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        'psychds_dir', action='store', type=Path,
        help='Root folder of PSYCH-DS Dataset being analyzed.')
    parser.add_argument(
        'output_dir', action='store', type=Path,
        help='Output path for visual reports')


def main(psychds_dir: Path = None, output_dir: Path = None):
    if psychds_dir is None:
        raise NameError('Required argument "psychds_dir" is not defined')
    if isinstance(psychds_dir, str):
        psychds_dir = Path(psychds_dir)
    if output_dir is None and psychds_dir is not None:
        output_dir = psychds_dir / 'psycodebk'
    with open(psychds_dir / 'dataset_description.json', 'r') as rf:
        metadata = json.load(rf)

    for dataset_file in (psychds_dir / 'raw_data').rglob('*_data.?sv'):
        if dataset_file.suffix == '.csv':
            sep = ','
        elif dataset_file.suffix == '.tsv':
            sep = '\t'
        dataset = pd.read_csv(dataset_file, sep=sep)
        app = flask.Flask(
            'parsing',
            template_folder=(Path(__file__).parent.parent / 'templates').resolve())
        var_sections = []
        for variable in metadata['variableMeasured']:
            var_name = variable['name']
            if isinstance(var_name, list):
                variable['name'] = var_name[0]
                var_name = var_name[0]
            if var_name not in dataset.columns:
                continue
            var_description = (
                variable['description'][0]
                if isinstance(variable['description'], list)
                else variable['description'])
            var_type = misc.type_variable(variable, dataset)
            var_table, missing_values = parsing.construct_var_summtab(
                metadata=variable, dataset=dataset, typing=var_type)
            image_data, distribution_data = viz.plot(
                variable=variable, dataset=dataset, typing=var_type)
            value_list = (
                parsing.produce_value_list(variable) if 'values' in variable else '<li>None</li>')
            with app.app_context():
                variable_section = render_template(
                    'var_construction.html',
                    var_name=var_name,
                    var_description=var_description,
                    missing_values=missing_values,
                    var_table=var_table,
                    image_data=image_data,
                    value_list=value_list,
                    typing=var_type,
                    distribution_data=distribution_data)
                var_sections.append(variable_section)
        with app.app_context():
            metadata_section = render_template('metadata_section.html', metadata=metadata)
            variable_section = render_template('variable_section.html', var_sections=var_sections)
            out_path = output_dir / dataset_file.name.replace('_data.csv', '_codebook.html')
            out_path.parent.mkdir(exist_ok=True, parents=True)
            rf = open(
                out_path,
                'w',
                encoding='utf-8')
            rf.write(
                render_template(
                    'main_body.html',
                    metadata_section=metadata_section,
                    variable_section=variable_section))
            rf.close()


if __name__ == '__main__':
    main(**get_parser().parse_args())
