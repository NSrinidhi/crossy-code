from flask import Flask
import os
import openai
from openai import OpenAI
import apikey from apikey.py
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
	return "Hello, world!"

# given theme -> get words --> return grid (helper for grid-to-clue and mega-dictionary)
# given grid -> return clues
# given filled grid -> return correctness

#@app.route('/get-grid')
def get_grid(theme):

	#start by getting superset of 200 relevant words
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
	#return words

	#words is the list of potential words

	#make .txt file with these words (scored as 1s) and remaining dictionary words (scored as 0s)
	with open('fullwordlist.txt', 'w') as file:
		for word in words:
			file.write(f"{word}; 1\n")

		#change scores of all words in spread_the_word_list to be 0
		spread_the_word_lines = []
		with open('spreadthewordlist.txt', 'r') as file:
			for line in file:
				word, _ = line.split(';')
				if word not in words: #check that we don't ovewrite the superset words
					spread_the_word_lines.append(f"{word.strip()}; 0\n")
		
		#fullwordlist.txt is the full .txt file
		file.writelines(spread_the_word_lines)
	
	for i in range(1, 31):
    	grid_filename = f'grids/g{i}.txt'
    	v = subprocess.run(['ingrid_core', grid_filename, '--wordlist', 'fullwordlist.txt', '--min-score', '3'], encoding="utf-8", capture_output=True)
		if v.returncode == 0:
			break
	if v.returncode == 0:
		return v.stdout
	else:
		return None

#@app.route('/get-words')
def get_words():

	#get grid from theme first
	grid = get_grid(theme)
	if grid is None:
		return {'Error': True}

	#given a grid from a particular theme
	grid_arr = grid.split("\n")
	grid_arr = [list(row) for row in grid_arr]
	#with open(filename) as file:
	#	while line := file.readline():
	#		grid_arr.append(list(line.rstrip()))

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

#MAIN ROUTE (returns big mapping of coordinates to words and clues)
@app.route('/', methods=['GET'])
def get_clues():
	theme = request.args.gets('topic', '')
	#get words in grid that came from theme first
	words = get_words(theme)

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

	word_to_clue['Error'] = False
	return word_to_clue


app.run(port=5000)