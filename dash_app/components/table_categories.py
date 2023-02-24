"""This script generates a table and a dictionary."""

from dash import html

categories_dict = {
    1: "Live animals",
    2: "Meat and edible meat",
    3: "Fish, crustaceans, molluscs and aquatic invertebrates",
    4: "Dairy products: eggs, honey and edible animal",
    5: "Products of animal origin",
    6: "Live trees, plants, bulbs, roots, flowers, etc",
    7: "Edible vegetables and certain roots and tubers"}


def gen_table_categories():
    """Make bootstrap table.

    This table acts as a legend for the x axis of barplot, it takes the
    dictionary: categories_dict

    """
    table_header = [
        html.Thead(
            html.Tr([
                html.Th("Category"),
                html.Th("Description")]), className='th-header')
    ]

    row1 = html.Tr([
        html.Td(list(categories_dict.keys())[0]),
        html.Td(categories_dict[1])])
    row2 = html.Tr([
        html.Td(list(categories_dict.keys())[1]),
        html.Td(categories_dict[2])])
    row3 = html.Tr([
        html.Td(list(categories_dict.keys())[2]),
        html.Td(categories_dict[3])])
    row4 = html.Tr([
        html.Td(list(categories_dict.keys())[3]),
        html.Td(categories_dict[4])])
    row5 = html.Tr([
        html.Td(list(categories_dict.keys())[4]),
        html.Td(categories_dict[5])])
    row6 = html.Tr([
        html.Td(list(categories_dict.keys())[5]),
        html.Td(categories_dict[6])])
    row7 = html.Tr([
        html.Td(list(categories_dict.keys())[6]),
        html.Td(categories_dict[7])])

    table_body = [
        html.Tbody([row1, row2, row3, row4, row5, row6, row7],
                   className='table-body')]

    return table_header + table_body
