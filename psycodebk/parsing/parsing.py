"""Modules for constructing variable tabs."""


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
        table_format = """
        <thead>
          <tr class="header">
            <th align="left">name</th>
            <th align="left">label</th>
            <th align="left">data_type</th>
            <th align="left">value_labels</th>
            <th align="left">missing</th>
            <th align="left">complete</th>
            <th align="left">n</th>
            <th align="left">mean</th>
            <th align="left">sd</th>
            <th align="left">p0</th>
            <th align="left">p25</th>
            <th align="left">p50</th>
            <th align="left">p75</th>
            <th align="left">p100</th>
          </tr>
        </thead>
        <tbody>
          <tr class="odd">
            <td align="left">{variable_name}</td>
            <td align="left">{desc}</td>
            <td align="left">numeric</td>
            <td align="left">{labels}</td>
            <td align="left">{missing}</td>
            <td align="left">{complete}</td>
            <td align="left">{total}</td>
            <td align="left">{mean}</td>
            <td align="left">{std}</td>
            <td align="left">{minimum}</td>
            <td align="left">{p25}</td>
            <td align="left">{p50}</td>
            <td align="left">{p75}</td>
            <td align="left">{maximum}</td>
          </tr>
        </tbody>"""
        (count, mean, std, minimum, p25, p50, p75, maximum) = desc
        table_format = table_format.format(
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
        table_format = """
        <thead>
          <tr class="header">
            <th align="left">name</th>
            <th align="left">data_type</th>
            <th align="left">missing</th>
            <th align="left">complete</th>
            <th align="left">n</th>
          </tr>
        </thead>
        <tbody>
          <tr class="odd">
            <td align="left">{variable_name}</td>
            <td align="left">{desc}</td>
            <td align="left">string</td>
            <td align="left">{missing}</td>
            <td align="left">{complete}</td>
            <td align="left">{total}</td>
          </tr>
        </tbody>"""
        table_format = table_format.format(
            variable_name=metadata['name'],
            desc=metadata['description'],
            missing=na_count,
            complete=complete,
            total=total,
            mean=mean)
    else:
        continue
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
    return var_table


def construct_var_disttab(
        metadata: dict,
        dataset: pd.DataFrame,
        variable_type: str,
        dataset_description: dict):
    # TODO: Organize figure subplots on scale items by if different scales.
    if variable_type == 'derived':
        plot_data = dataset[metadata['derivation']['vars']]
        scale = {}
        # for x in dataset_description['variableMeasured']:
        #    if x['name'] in metadata['derivation']['vars'] and x['values'] not in scale:
        #        scale[x['values']] = [x['name']]
        #        scale.update(**_parse_vars(x['values']) for x in if x['name'] in }
        g = plot_likert(metadata, plot_data)
