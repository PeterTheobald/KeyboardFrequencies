# KeyboardFrequencies

Collect keyboard frequency data WITH control keys.

All of the data I've seen only compiles visible characters from stored files, but ignores all the arrows backspace delete copy/paste home end and control codes that we spend a lot of our time typing. I'd bet backspace at least deserves a place on a main layer alongside the alpha keys. 
To do something about this, I wrote a very small Python program to keep stats on our typing. Yes it is technically a keystroke logger, but it is just one page long and you can see that it only keeps a count of each key and doesn't store anything else. It outputs the results to a file "key_counts.json".
I am running it right now on my PC and I will leave it running for at least a week. I ask others to do the same. I can compile and consolidate the results if people are interested.

I have only tested it on Windows, but it should work on Mac and Linux.
To run:

download key-logger.py
pip install pynput
python key-logger.py

Leave it running for at least a week. When you're ready, kill it w Control-C or Control-Break or just kill the window. Then send me the key_counts.json for collating.
It might be helpful if you also told me if you are using VSCode, Vim, Emacs or something else for text editing. I can do separate analysis for users of each editor.
