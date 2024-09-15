import pandas as pd

#upload and preprocess dataset
df = pd.read_csv("nytcrosswords_small.csv", encoding='ISO-8859-1')
df['prompt'] = df['Word'].apply(lambda x: f"give me a crossword-style clue for the word {x}")
df_small = df.sample(frac=0.01)

print(df.head(10))