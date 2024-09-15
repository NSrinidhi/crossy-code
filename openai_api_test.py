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

#test whether clue generation is better that stupid smolLM
clue_gen_chat = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You're a helpful assistant who outputs possible clues for a given word that's a crossword answer. Respond with no introductory or conversational text and clue(s) in a python array of strings. The clues shouldn't have any apostrophes or quotation marks in them."},
        {"role": "user", "content": "Give me a crossword-style clue for the word EBOOK"},
        {"role": "assistant", "content": "['Where to find a story online']"},
        {"role": "user", "content": "Give me a crossword-style clue for the word KETTLE"},
        {"role": "assistant", "content": "['One whistling in the kitchen?']"},
        {"role": "user", "content": "Give me a crossword-style clue for the word DOG. This time I'd like 2 clues as two elements of the list"}
    ],
    model="gpt-4o-mini"
)

clue_output = clue_gen_chat.choices[0].message.content
print(clue_output)

exec(clue_output)
print(f"clues for puzzle and word metadata are {clue_output}")