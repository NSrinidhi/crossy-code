import subprocess

wordlist_filename = 'test_wordlist4.txt'

for i in range(1, 31):
    grid_filename = f'grids/g{i}.txt'
    subprocess.run(['ingrid_core', grid_filename, '--wordlist', wordlist_filename])