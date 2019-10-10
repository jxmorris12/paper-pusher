# jm8wx 10/10/2019

# Download an excel sheet with the required fields
# and copy papers into database, in or out of queue.

import pandas as pd
from paper import Paper

path = './data/PaperData-2019-10-10.xlsx'
df = pd.read_excel(path)

# Papers I have read.
read_papers = df[~(df['Read?'].isna())]

for index, paper_data in read_papers.iterrows():
    Paper.from_excel(paper_data).save()

# Papers I have recorded the 'Written' date for, but have not read.
queue_papers = df[~(df['Written'].isna())].reset_index()[df['Read?'].isna()].reset_index()

for index, paper_data in queue_papers.iterrows():
    Paper.from_excel(paper_data).save()
