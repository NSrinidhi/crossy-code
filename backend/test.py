import pandas as pd
from datasets import dataset

#upload and preprocess dataset
df = pd.read_csv("nytcrosswords_small.csv", encoding='ISO-8859-1')
df['prompt'] = df['Word'].apply(lambda x: f"give me a crossword-style clue for the word {x}")
# df_small = df.sample(frac=0.01)
df_small = df

# df_small
# type(df_small.iloc[0].Clue)
df_small.iloc[0].Clue, df_small.iloc[0].Word, df_small.iloc[0].prompt
df_small = df_small[['prompt', 'Clue']]

print(df_small.head(10))

hf_dataset_small = Dataset.from_pandas(df_small)
print(hf_dataset_small)

def tokenize_function(examples):
  return tokenizer(examples['prompt'], text_target=examples['Clue'], truncation=True, padding='max_length')

tokenized_datasets = hf_dataset_small.map(tokenize_function)