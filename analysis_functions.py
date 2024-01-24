from Sankey import make_sankey, _code_mapping, stacking
import plotly.express as px
import pandas as pd


def read_and_clean_csv(file_name,*desired_cols, encoding = " "):
    """
    This function reads a CSV file into a pandas Dataframe. Then, it cleans and process the
    dataset.
    :parameters
    - String : file name
    - Tuple : desired column names in the dataframe
    - String : (optional) encoding for reading in the CSV
    :return:
    - Data Frame : cleaned and ready for processing data
    """
    # Reads in the CSV File
    if (encoding != " "):
        df = pd.read_csv(file_name, encoding=encoding)
    else:
        df = pd.read_csv(file_name)


    # Create dataframe with desired columns
    col_specific_df = df[list(desired_cols)]

    # Remove any null values
    col_specific_df = col_specific_df.dropna()

    # Remove duplicate rows if any.
    col_specific_df = col_specific_df.drop_duplicates()

    # Makes all string values lowered so no issues with casing
    for col in col_specific_df.columns:
        if col_specific_df[col].dtypes == object:
            col_specific_df[col] =  col_specific_df[col].str.lower()

    integer_columns = [ 'released_year','released_month','in_spotify_playlists',
                       'in_spotify_charts','streams','bpm', 'danceability_%','valence_%','energy_%','acousticness_%',
                        'instrumentalness_%','liveness_%','speechiness_%']

    # Converts all columns that can be integers into ints
    for col in integer_columns:
        non_integer_mask = col_specific_df[col].apply(filter_non_integer)
        col_specific_df = col_specific_df[non_integer_mask]

    col_specific_df[integer_columns] = col_specific_df[integer_columns].apply(pd.to_numeric)

    return col_specific_df
def create_sankey(df, *cols):
    """
    This function creates a sankey diagram based on the given 2 columns. It then returns
    the sankey diagram

    :param df: a dataframe used to create a sankey diagram
    :param cols: the columns used to create the sankey diagram
    :return sankey_diagram: returns a sankey plot that will be saved as a png
    """
    # Aggregates the data by counting the number of artists
    columns = list(cols)
    df = df.groupby(by=columns).size().reset_index(name='count')

    # Only includes artists with over 10 songs on the chart
    df = df[df['count'] >= 3]

    # Create an interactive Sankey diagram
    sankey_diagram = make_sankey(df, *cols, save = 'Sankey_diagram.png')
    return sankey_diagram

def create_facet_plot(df, x_axis_col, y_axis_col, facet_col):
    """
    This function creates a facet plot based on two columns. It will
    then return the plot

    :param df: a dataframe used to create a facet plot
    :param x_axis_col: a string representing the column name for the xaxis of the plot
    :param y_axis_col: a string representing the column name for the yaxis of the plot
    :param facet_col: a string representing the column name for the coloring of the plot
    :return fig: a scatter plot of the bpm vs key colored by the mode
    """
    # Get the sub data set based on the given columns
    df_sub = df[[x_axis_col, y_axis_col, facet_col]]

    # Count the number of similar observations for sizing
    df['count'] = df.groupby(['bpm', 'key', 'mode'])['bpm'].transform('size')
    # df_sub['count'] = df_sub.groupby(['bpm', 'key', 'mode']).transform('count')

    color_mappings = {'major': '#88A774', 'minor': '#B583A2'}

    # Create a facet scatter plot where there are two plots (one for major and one for minor keys)
    fig = px.scatter(df, x=x_axis_col, y=y_axis_col,
                    color='mode',  # You can use color to further distinguish points
                    facet_col='mode',size='count', opacity = 0.6, # Create separate plots for 'major' and 'minor'
                    title=f"Scatter plot of {y_axis_col} vs. {x_axis_col} by Mode",
                    labels={x_axis_col: x_axis_col, y_axis_col: y_axis_col},
                    color_discrete_map=color_mappings)
    fig.update_layout(
        font=dict(
            family="Times New Roman",
            color="white"  # Text color
        ),
        paper_bgcolor="#1F1F1F",  # Background color of the plot
        plot_bgcolor="#1F1F1F",  # Inside background color
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=50,
            pad=4
        ),
        xaxis=dict(
            tickcolor="white",  # Tick color
            gridcolor="white"  # Grid line color
        ),
        yaxis=dict(
            tickcolor="white",
            gridcolor="white"
        ),
        width=800,
        height=600,

    ),

    return fig


def create_facet_histogram_plot(df, x_axis_col, y_axis_col, facet_col):
    """
    This function creates a facet histogram plot to showcase the bpm vs key by mode
    similar to the facet plot

    :param df: a dataframe used to create a facet histogram plot
    :param x_axis_col: a string representing the column name for the xaxis of the plot
    :param y_axis_col: a string representing the column name for the yaxis of the plot
    :param facet_col: a string representing the column name for the coloring of the plot
    :return fig : a histogram showing the bpm vs key colored by the mode
    """
    # Gets the sub data set based on the given columns
    df_sub = df[[x_axis_col, y_axis_col, facet_col]]

    fig = px.violin(df, x='key', y='bpm', color='mode',
                    box=True, points="all",
                    title="Violin plot of bpm vs. key by Mode",
                    labels={'bpm': 'BPM', 'key': 'Key'},
                    color_discrete_map={'major': 'blue', 'minor': 'red'})


    fig.show()

    return fig
def filter_non_integer(x):
    """
    This function is used to check if the values in a column can
     be converted to an integer or not

    :param x: value in a dataframe
    :return: boolean value of True of False based on if x can be converted to an int
    """
    try:
        int(x)
        return True  # Successfully converted to an integer
    except ValueError:
        return False  # Cannot be converted to an integer
def create_mean_val(df):
    """
    This function is used to group the data based on certain
    attributes and then will be used to create a bar chart

    :param df: a dataframe that will be used to group the data based on month
    :return: a series representing the released_month and the avg number of streams per month
    """
    # Groups the streams by the released month and find the mean streams for those groupings
    mean_streams_by_month = df.groupby('released_month')['streams'].mean()

    return mean_streams_by_month

def create_bar(df):
    """
    This function creates and customizes a bar chart to display the
    grouped data information

    :param df: a dataframe of information from spotify
    :return bar: a bar chart of the released_months vs avg streams per month
    """
    # calls from mean streams to get the series
    mean_streams = create_mean_val(df)

    # Create bar chart
    bar = px.bar(mean_streams, x=mean_streams.index, y=mean_streams.values)

    # Customize layout and traces
    bar.update_layout(
        title="Graph of AVG Streams vs Month",
        font=dict(
            family="Times New Roman",
            color="white"  # Text color
        ),
        paper_bgcolor="#1F1F1F",  # Background color of the plot
        plot_bgcolor="#1F1F1F",  # Inside background color
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=50,
            pad=4
        ),
        xaxis=dict(
            tickcolor="white",  # Tick color
            gridcolor="white"  # Grid line color
        ),
        yaxis=dict(
            tickcolor="white",
            gridcolor="white"
        ),
        width=800,
        height=600
    ),

    bar.update_traces(
        marker=dict(color='#88A774')  # Bar color
    )

    # Show the figure
    return bar
