""" This script applies several functions that allow for better readibility
 of the data from the .csv"""

import pandas as pd

def clean_df(df):
    """ This function cleans the data from the data frame.
    - Drops duplicates
    - Removes NaN variables
    - Merge categories 07
    - Create an extra column having the numbers of each  category """
    # Drop duplicates
    df = df.drop_duplicates()
    # Drop NaN
    df = df.dropna()
    # Clean categories column, category 7 is repeated
    df.category = df.category.apply(
        lambda x: '07_edible_vegetables_and_certain_roots_and_tubers' \
            if x == '07_edible_vegetables_and_certain_roots_and_tu' else x)
    # Create an extra column with the number of the category
    df['category_num'] = df.category.apply(
        lambda x: int(x[1])
    )
    return df

def get_df_european_countries(df_countries, df):
    europe_countries = list(df_countries[df_countries.columns[0]])
    df_countries = list(df['country_or_area'].unique())
    selected_european_countries = []
    for i in europe_countries:
        if i in df_countries:
            selected_european_countries.append(i)
    df = df[df['country_or_area'].isin(selected_european_countries)]
    return df