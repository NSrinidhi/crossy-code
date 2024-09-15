from flask import Flask
import os
import openai
from openai import OpenAI
import apikey from apikey.py

app = Flask(__name__)

@app.route('/')
def home():
	return "Hello, world!"

# given theme -> return words
# given words -> return grid
# given grid -> return clues
# given filled grid -> return correctness

@app.route('/get-words')
def get_words(theme):
	openai.api_key = apikey
	client = OpenAI(api_key=openai.api_key)

	models = client.models.list()
	#print(models)

	test_chat = client.chat.completions.create(
		messages=[
			{"role": "system", "content": "You're a helpful assistant giving me words related to a topic; the words are potential answer words in a crossword. Respond with only the array and no introductory or conversational text. Also, always call the array 'words' and not anything more specific."},
			{"role": "user", "content": "Can you give me 10 words related to movies? Some proper nouns are okay but preferably only a few. And could you give them to me in the format of a python array? Lastly, I'd like the majority of the words to be <=5 letters"},
			{"role": "assistant", "content": "words = ['film', 'cast', 'edit', 'hero', 'shot', 'plot', 'star', 'role', 'seat', 'tape']"},
			{"role": "user", "content": f"Can you give me 200 words related to {theme}? Some proper nouns are okay but preferably only a few. And could you give them to me in the format of a python array? Lastly, I'd like the majority of the words to be <=5 letters"}
		],
		model="gpt-4o-mini"
	)

	#prepare output for passing into grid generator
	raw_output = test_chat.choices[0].message.content

	exec(raw_output)
	return words

@app.route('/get-grid')
def get_grid():
	return "Hello, world!"

@app.route('/get-words')
def get_words(grid):
	grid_arr = []
	with open(filename) as file:
		while line := file.readline():
			grid_arr.append(list(line.rstrip()))
	rows = len(grid_arr)
	cols = len(grid_arr[0])
	words = {}
	for r in range(rows):
		w = ''
		for c in range(cols):
			if r[c] == "#":
				if len(w) > 1:
					words[(r, c - len(w))] = w
			else:
				w += c
		if len(w) > 1:
			words[(r, c - len(w))] = w
	for c in range(cols):
		w = ''
		for r in range(rows):
			if r[c] == "#":
				if len(w) > 1:
					words[(r - len(w), c)] = w
			else:
				w += c
		if len(w) > 1:
			words[(r - len(w), c)] = w
	return words

@app.route('/')
def get_clues(words):
	openai.api_key = apikey
	client = OpenAI(api_key=openai.api_key)

	word_to_clue = {}
	for word in words:
		clue_gen_chat = client.chat.completions.create(
			messages=[
				{"role": "system", "content": "You're a helpful assistant who outputs possible clues for a given word that's a crossword answer. Respond with no introductory or conversational text and clue(s) in a python array of strings. The clues shouldn't have any apostrophes or quotation marks in them."},
				{"role": "user", "content": "Give me a crossword-style clue for the word EBOOK"},
				{"role": "assistant", "content": "['Where to find a story online']"},
				{"role": "user", "content": "Give me a crossword-style clue for the word KETTLE"},
				{"role": "assistant", "content": "['One whistling in the kitchen?']"},
				{"role": "user", "content": f"Give me a crossword-style clue for the word {word}"}
			],
			model="gpt-4o-mini"
		)

		clue_output = clue_gen_chat.choices[0].message.content
		exec(clue_output)
		word_to_clue[word] = clue_output

	return word_to_clue

@app.route('/check-grid')
def check_grid():
	return "Hello, world!"

app.run(port=5000)