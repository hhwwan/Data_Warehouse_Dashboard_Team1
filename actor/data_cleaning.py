import pandas as pd

# Load the CSV file
df = pd.read_csv('main_data2.csv')

# Select the first split (voting_date, released_date, title, sales, total_sales)
df1 = df[['voting_date', 'released_date', 'title', 'sales', 'total_sales']]
# Select the second split (voting_date, released_date, title, audience, total_audience)
df2 = df[['voting_date', 'released_date', 'title', 'audience', 'total_audience']]
# Save the split data to new CSV files
df1.to_csv('sales.csv', index=False, encoding='utf-8-sig')
df2.to_csv('audience.csv', index=False, encoding='utf-8-sig')

df3 = df[['title', 'genre']]
df3 = df3.drop_duplicates(subset=['title', 'genre'])
df3 = df3.explode('genre')
df3['genre'] = df3['genre'].str.split(',')
df3 = df3.explode('genre')

df4 = df[['title', 'performers']]
df4 = df4.drop_duplicates(subset=['title','performers'])
df4['performers'] = df4['performers'].str.split(',')
df4 = df4.explode('performers')
df3.to_csv('genre.csv', index=False, encoding='utf-8-sig')
df4.to_csv('performers.csv', index=False, encoding='utf-8-sig')


