import os
import openai
from openai import OpenAI

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai.api_key)

models = client.models.list()
#print(models)

test_chat = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You're a helpful assistant giving me words related to a topic; the words are potential answer words in a crossword. Respond with only the array and no introductory or conversational text. Also, always call the array 'words' and not anything more specific."},
        {"role": "user", "content": "Can you give me 10 words related to movies? Some proper nouns are okay but preferably only a few. And could you give them to me in the format of a python array? Lastly, I'd like the majority of the words to be <=5 letters"},
        {"role": "assistant", "content": "words = ['film', 'cast', 'edit', 'hero', 'shot', 'plot', 'star', 'role', 'seat', 'tape']"},
        {"role": "user", "content": "Can you give me 200 words related to the bible? Some proper nouns are okay but preferably only a few. And could you give them to me in the format of a python array? Lastly, I'd like the majority of the words to be <=5 letters"}
    ],
    model="gpt-4o-mini"
)

#prepare output for passing into grid generator
raw_output = test_chat.choices[0].message.content

exec(raw_output)
print(f"word list for grid generation is {words}")