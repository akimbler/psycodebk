"""Utils for plotting data."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from ..utils.misc import _parse_vals, get_antecedents
from io import BytesIO
import base64


def plot_likert(
        variable: dict,
        dataset: pd.DataFrame,
        scales: dict = None,
        plot_percentage: bool = False,
        colors: list = [
            '#ffffff', '#7A76C2',
            '#ff6e9c98', '#f62196',
            '#18c0c4', '#f3907e', '#66E9EC'],
        figsize: tuple = None) -> str:
    """Produce Distribution of Likert-type data."""
    # Pad each row/question from the left, so that they're centered
    # around the middle (Neutral) response
    if scales:
        scales = {
            key: value.title() for key, value in _parse_vals(variable['values'])}
    if 'naValues' in variable:
        dataset.replace(variable['naValues'], np.nan, inplace=True)
    dataset = dataset[get_antecedents(variable)]
    counts = pd.concat(
        [dataset[x].value_counts().copy() for x in dataset.columns],
        axis=1).T
    if plot_percentage:
        counts = pd.concat(
            [(dataset[x].value_counts()
              / dataset.notnull()[x].sum())
             * 100 for x in dataset.columns],
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

    xlabels = [int(label) for label in xlabels if round(label) == label]
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
    image = BytesIO()
    plt.style.use('seaborn-white')
    plt.savefig(image, format='png', dpi=144, bbox_inches='tight')
    image_data = base64.encodebytes(
        image.getvalue()).decode('utf-8').strip('\n')
    plt.close()
    return image_data


def plot_ordinal(variable: dict, dataset: pd.DataFrame) -> str:
    """Plot distribution of non-likert type data."""
    import matplotlib.pyplot as plt
    import textwrap
    varname = variable['name']
    dataset = dataset[varname].replace(to_replace=variable['naValues'], value=np.nan)
    if dataset.notnull().sum() == 0:
        return 'None'
    if len(dataset.unique()) < 10:
        value_labels = _parse_vals(variable['values'])
        image = BytesIO()
        plt.style.use('seaborn-white')
        g = sns.countplot(data=dataset.to_frame(),
                          y=dataset.name,
                          palette=[
                              '#7A76C2', '#BC72AF', '#ff6e9c98',
                              '#FA4799', '#f62196', '#8770AD',
                              '#18c0c4', '#85A8A1', '#f3907e', '#ACBCB5'])
        g.set_yticklabels(
            [textwrap.fill(value_labels[y._text], width=20) for y in g.get_yticklabels()])
        g.set_ylabel('Values')
        g.set_xlabel('Counts')
        plt.savefig(image, format='png', dpi=144, bbox_inches='tight')
        # Produce image in base64 for html imbedding
        image_data = base64.encodebytes(
            image.getvalue()).decode('utf-8').strip('\n')
        plt.close()
    else:
        image_data = 'None'
    return image_data


def plot_interval(variable: dict, dataset: pd.DataFrame) -> str:
    image = BytesIO()
    sns.distplot(
        dataset[variable['name']].replace(
            to_replace=variable['naValues'],
            value=np.nan).to_numpy(),
        color='#ff6e9c98', kde=False)
    plt.savefig(image, format='png', dpi=144, bbox_inches='tight')
    image_data = base64.encodebytes(
        image.getvalue()).decode('utf-8').strip('\n')
    plt.close()
    return image_data


def plot_open(variable: dict, dataset: pd.DataFrame) -> str:
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    import re

    comment_words = ''
    stopwords = set(STOPWORDS)
    dataset = dataset[variable['name']]
    response_list = dataset[dataset.notnull()].tolist()
    comment_words = " ".join(response_list)

    # plot the WordCloud image
    plt.figure(figsize=(8, 8), facecolor=None)
    wordcloud = WordCloud(
        width=800, height=800,
        background_color='white',
        stopwords=stopwords,
        min_font_size=10)
    wordcloud.generate_from_text(comment_words)
    image_data = wordcloud.to_svg(embed_image=True)
    image_data = re.search(
        r'(?P<svg_tag>[\w\W]+)base64,(?P<base64>[a-zA-Z0-9/+=]+)',
        image_data).group('base64')
    plt.close()
    # Produce image in base64 for html imbedding
    return image_data


def plot(variable: dict, typing: str, dataset: pd.DataFrame) -> str:
    image_data = 'None'
    distribution_data = 'None'
    if typing == 'Scale':
        image_data = plot_likert(variable, dataset)
        distribution_data = plot_interval(variable, dataset)
    if typing == 'ordinal':
        image_data = plot_ordinal(variable, dataset)
    if typing == 'open':
        image_data = plot_open(variable, dataset)
    if typing == 'interval':
        image_data = plot_interval(variable, dataset)

    return image_data, distribution_data
