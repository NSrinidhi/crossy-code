import pandas as pd
import json
import os
import openai
from openai import OpenAI
import time

df = pd.read_csv('nytcrossword_tinytim_tester.csv')

#now, messages contains both the formatted prompt and the clue (target response)
df['messages'] = df.apply(lambda row: [
    {"role": "system", "content": "You are a helpful assistant that provides crossword-style clues for words"},
    {"role": "user", "content": f"Give me a crossword-style clue for the word {row['Word']}."},
    {"role": "assistant", "content": row['Clue']}
], axis=1)

#df['prompt'] = df['Word'].apply(lambda x: f"Give me a crossword-style clue for the word {x}")
#df = df.rename(columns={"Clue": "completion"})
#df = df[['prompt', 'completion']]

with open('xword_clues.jsonl', 'w') as f:
    for idx, row in df.iterrows():
        record = {
            "messages": row['messages']
        }
        f.write(json.dumps(record)+ '\n')

#test if json writing worked properly
data = []
with open('xword_clues.jsonl', 'r') as f:
    for line in f:
        data.append(json.loads(line.strip()))

for entry in data[:5]:
    print(entry)

#upload dataset to OpenAI server
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

response = openai.files.create(
    file=open("xword_clues.jsonl", "rb"),
    purpose='fine-tune'
)

file_id = response.id
print("File ID post upload: ", file_id)

ft_response = client.fine_tuning.jobs.create(
    training_file=file_id,
    model="gpt-3.5-turbo",
    hyperparameters={
        "n_epochs": 4,
        "batch_size": 32,
        "learning_rate_multiplier": 0.1,
    }
)
fine_tune_id = ft_response.id

def check_fine_tuning_events(fine_tune_id):
    events = client.fine_tuning.jobs.list_events(fine_tune_id)
    for event in events:
        print(event)

def monitor_fine_tuning(fine_tune_id, interval=60):
    while True:
        progress_response = client.fine_tuning.jobs.retrieve(fine_tune_id)
        job_status = progress_response.status

        print(f"Job status: {job_status}")

        if job_status in ["succeeded", "completed", "failed", "cancelled"]:
            print(f"fine-tuning status is {job_status}. EXIT.")
            break

        print(f"Checking events for fine-tuning job {fine_tune_id}......")
        check_fine_tuning_events(fine_tune_id)
        print("Waiting for next check.... \n")
        time.sleep(interval)

#get post-SFT model ID

print("pre-SFT ID: ", fine_tune_id)
monitor_fine_tuning(fine_tune_id, interval=60)

job_details = client.fine_tuning.jobs.retrieve(fine_tune_id)
sft_model_id = job_details.fine_tuned_model

if sft_model_id:
    print(f"SFT model ID: {sft_model_id}")
else:
    print(f"Job hasn't succeeded yet")