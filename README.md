# Lyrics-Embedder

An application that'll get lyrics from genius.com (if they exist) and put them into your mp3 files. For it to work you need to have the title and artist tags in the mp3. 

# Why make this? WHY? FOR THE LOVE OF GOD WHY?

I made this project mostly for person use, but also to learn about: 
* MP3 manipulation
* Web scraping
* Trying muli-threading
* Learning how to read words

# Dependencies
* [PyQt5](https://pypi.python.org/pypi/PyQt5) (For GUI)
* [Mutagen](https://mutagen.readthedocs.io/en/latest/) (For MP3 stuff)
* [Chardet](https://pypi.python.org/pypi/chardet) and [Ftfy](https://github.com/LuminosoInsight/python-ftfy) (For unicode and lyrics stuff)

# Further improvements:
* Find a better way to get genius.com url 
* Make a lyrics box that displays what we scraped 
* Maybe implement detecting/translating non-english lyrics

