"""
For this script we will,
Create pivot table to sales of Brands across different countries.
"""

import pandas as pd
df = pd.read_excel("C:\Coding\scripts\\beverage_sales_data.xlsx")

#take necessary columns for the pivot table
df = df[['country','sales','brand']]

#create the pivot table
pivot_table = df.pivot_table(index='brand', columns='country', values='sales', aggfunc=sum)

#create new excel file with the pivot table
pivot_table.to_excel('C:\Coding\scripts\Generated\\beverage_sales_pivot_table.xlsx', 'Report')
