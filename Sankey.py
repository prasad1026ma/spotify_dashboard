import plotly.graph_objects as go
import pandas as pd

def _code_mapping(df, src, targ):
    """
    Maps values in the dataframe from the source and target columns to numerical codes.

    :param df: a dataframe with two columns of attributes and a count column
    :param src: the source column name (right of sankey)
    :param targ: the target column name (left of sankey)
    :return df: a dataframe of values in src and targ columns replaced by numerical codes
    :return labels: a list of unique labels found in src and targ columns
    """
    print("BEFORE:\n", df)

    # get the distinct labels from src/targ columns
    labels = list(set(list(df[src]) + list(df[targ])))

    # generate n integers for n labels
    codes = list(range(len(labels)))

    # create a map from label to code
    lc_map = dict(zip(labels, codes))

    # substitute names for codes in the dataframe
    df = df.replace({src: lc_map, targ: lc_map})

    print("AFTER:\n", df)

    return df, labels

def stacking(df, *cols):
    """
    stacks the dataframe to allow one to create sankey diagrams
    :param df: a dataframe with over two columns
    :param cols: two or more strings representing the attributes in the dataframe
    :return newDf: a dataframe suitable for creating sankey diagrams
    :return src: the first attribute in cols and the source column name
    :return targ: the last attribute in cols and the target column name
    """
    # create a new DataFrame
    newDf = pd.DataFrame()

    # iterate through each target column and stack it with the source colum
    for i in range(len(cols) - 1):

        # creates a temporary dataframe to hold two columns of data
        tempDf = df[[cols[i], cols[i+1], 'count']]

        # renames the dataframe columns to source, target, and count
        tempDf.columns = ['source', 'target', 'count']

        # combines the dataframes together to create one stacked dataframe
        newDf = pd.concat([newDf, tempDf])

    # aggregates the data to give a weight to the nodes of the sankey diagram
    newDf = newDf.groupby(['source', 'target']).agg({'count': 'sum'}).reset_index()

    src = newDf.columns[0]

    targ = newDf.columns[1]

    return newDf, src, targ
def make_sankey(df, *cols, vals=None, save=None, **kwargs):
    """

    :param df: a dataframe filled with columsn and values
    :param cols: a collection of strings representing the column names of the datframe
    :param vals: a series represnting the weights that correpsond to the weights of nodes on sankey
    :param save: save the generated Sankey diagram as an image file.
    :param kwargs:allows you to pass additional keyword arguments
    :return:
    """
    assert (len(cols) <= 2, "At least 2 columns are required to create a Sankey diagram.")
    # calls the stacking function to prepare the DataFrame for creating the Sankey diagram.
    df, src, targ = stacking(df, *cols)

    # sets vals as the variable count
    vals = 'count'

    if vals:
        values = df[vals]
    else:
        values = [1] * len(df)

    # calls code mapping to map the source and target values in the DataFrame
    df, labels = _code_mapping(df, src, targ)

    # creates a Sankey diagram with a link, node thickness, and nodes
    link = {'source': df[src], 'target': df[targ], 'value': values,
            'line': {'color': 'black', 'width': 2}}

    node_thickness = kwargs.get("node_thickness", 50)

    node = {'label': labels, 'pad': 50, 'thickness': node_thickness,
            'line': {'color': 'black', 'width': 1}}

    # uses the plotly library to create the sankey diagram
    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    #fig.show()
    return fig

    # This requires installation of kaleido library
    if save:
        fig.write_image(save)

