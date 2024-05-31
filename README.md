# KeyboardFrequencies

Collect keyboard frequency data WITH control keys.

All of the data I've seen only compiles visible characters from stored files, but ignores all the arrows backspace delete copy/paste home end and control codes that we spend a lot of our time typing. I'd bet backspace at least deserves a place on a main layer alongside the alpha keys. 
To do something about this, I wrote a very small Python program to keep stats on our typing. Yes it is technically a keystroke logger, but it is just one page long and you can see that it only keeps a count of each key and doesn't store anything else. It outputs the results to a SQLite database file "key_counts.db".
I am running it right now on my PC and I will leave it running for at least a week. I ask others to do the same. I can compile and consolidate the results if people are interested.
It counts individual keystrokes and bigrams.

I have only tested it on Windows, but it should work on Mac and Linux.
To run:
```
if you have an older Windows you may need to install Python first: (Microsoft Store Python Installer)[https://apps.microsoft.com/detail/9nj46sx7x90p?activetab=pivot%3Aoverviewtab&rtc=1&hl=en-us&gl=US]
download key-logger.py
pip install pynput
python key-logger.py
```
Leave it running for at least a week. When you're ready, press the STOP button. Use `python key-logger.py --display` to see the results. Then send me the key_counts.db for collating.
It might be helpful if you also told me if you are using Windows or Mac, VSCode, Vim, Emacs or something else for text editing. I can do separate analysis for users of each platform and editor.

```
python key-logger.py --display
This will display the counts in the database after running the program.
```

## Todo:
- [x] Record unigrams, bigrams and trigrams. The data file will be much bigger, so move from dumping a json file to updating a SQLite database.
- [x] Add a GUI interface
- [ ] Test on Mac OSX
- [ ] Reach out to keyboard layout analysis program maintainers and ask them to add the ability to read a unigram,bigram,trigram data file instead of consuming a text corpus (obviously I can't ask people to send me their actual text instead of just counts)
- [ ] Write a tool to consolidate multiple people's data files into one large data file. Do this to make one huge data file, and one for people using different editors (VSCode, vim, emacs, etc).
