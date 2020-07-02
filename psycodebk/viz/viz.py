import matplotlib
import matplotlib.pyplot as plt


def plot_likert(
    variable: dict,
    dataset: pd.DataFrame,
    scales: dict = None,
    plot_percentage: bool = False,
    colors: list = ['#ffffff', '#7A76C2', '#ff6e9c98', '#f62196', '#18c0c4', '#f3907e', '#66E9EC'],
    na_vals: list = None,
    figsize = None,
) -> matplotlib.axes.Axes:
    # Pad each row/question from the left, so that they're centered around the middle (Neutral) response
    if scales:
        scales = {key: value.title() for key, value in _parse_vals(variable['values'])}
    dataset.replace(na_vals, np.nan, inplace=True)
    counts = pd.concat(
        [dataset[x].value_counts().copy() for x in dataset.columns], 
        axis=1).T
    if plot_percentage:
        counts = pd.concat(
            [(dataset[x].value_counts() / dataset.notnull()[x].sum()) * 100 for x in dataset.columns],
            axis=1).T
    counts.fillna(0, inplace=True)
    counts.columns = [str(x) for x in counts.columns]
    if scales:
        counts.rename(scales, axis="columns", inplace=True)
    scale_middle = counts.shape[-1] // 2
    if scale_middle == counts.shape[-1] / 2:
        middles = counts.iloc[:, 0:scale_middle].sum(axis=1)
    else:
        middles = (
            counts.iloc[:, :scale_middle].sum(axis=1)
            + counts.iloc[:, scale_middle] / 2)
    padding_left = 0.05 * counts.sum(axis="columns").max()
    
    center = middles.max() + padding_left
    padding_values = (middles - center).abs()
    padded_counts = pd.concat([padding_values, counts], axis=1)
    # hack to "hide" the label for the padding
    padded_counts = padded_counts.rename({0: "Legend"}, axis=1)

    # Reverse rows to keep the questions in order
    # (Otherwise, the plot function shows the last one at the top.)
    reversed_rows = padded_counts.iloc[::-1]

    # Start putting together the plot
    ax = reversed_rows.plot.barh(stacked=True, color=colors, figsize=figsize)

    # Draw center line
    center_line = plt.axvline(center, linestyle="--", color="black", alpha=1.0)
    center_line.set_zorder(-1)

    # Compute and show x labels
    num_ticks = ax.xaxis.get_tick_space()
    max_width = int(round(padded_counts.sum(axis=1).max()))
    interval = round(max_width / num_ticks)
    right_edge = max_width - center
    right_labels = np.arange(0, right_edge + interval, interval)
    right_values = center + right_labels
    left_labels = np.arange(0, center + 1, interval)
    left_values = center - left_labels
    xlabels = np.concatenate([left_labels, right_labels])
    xvalues = np.concatenate([left_values, right_values])

    xlabels = [int(l) for l in xlabels if round(l) == l]
    if plot_percentage:
        xlabels = [str(label) + "%" for label in xlabels]

    ax.set_xticks(xvalues)
    ax.set_xticklabels(xlabels)
    if plot_percentage is True:
        ax.set_xlabel("Percent of Responses")
    else:
        ax.set_xlabel("Number of Responses")
    # Control legend
    plt.legend(bbox_to_anchor=(1.05, 1))

    return ax


def plot_distribution(dataframe, varname, value_labels):
    from io import BytesIO
    import seaborn as sns
    import matplotlib.pyplot as plt
    import base64
    if len(dataframe[varname].unique()) < 20:
        counts = pd.DataFrame(dataframe[varname].value_counts())
        counts.reset_index(inplace=True)
        counts['index'] = counts['index'].astype('str')
        counts.replace(_parse_vals(value_labels), inplace=True)
        image = BytesIO()
        g = sns.barplot(
            data=counts,
            x=varname,
            y='index',
            palette=[
                '#7A76C2', '#BC72AF', '#ff6e9c98',
                '#FA4799', '#f62196','#8770AD', 
                '#18c0c4','#85A8A1', '#f3907e', '#ACBCB5'], orient='h')
        g.set_xlabel('Count')
        g.set_ylabel('Values')
        plt.savefig(image, format='png', dpi=300, bbox_inches='tight')
        image_data = base64.encodebytes(image.getvalue()).decode('utf-8').strip('\n')
        plt.close()
    else:
        image_data = 'None'
    return image_data