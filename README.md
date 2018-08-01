# Lyrics-Embedder

An application that'll scrape Song Lyrics from Genius.com (if they exist) and put them into your mp3 files. For it to work you need to have the Title and Artist tags in the mp3 file. 

# Why make this? WHY?

I made this project mostly for personal use, but also to learn about: 
* MP3 manipulation
* Web scraping
* Trying out multi-threading as opposed to multi-processing

# Dependencies
* [PyQt5](https://pypi.python.org/pypi/PyQt5) (For GUI)
* [Mutagen](https://mutagen.readthedocs.io/en/latest/) (For MP3 stuff)
* [Chardet](https://pypi.python.org/pypi/chardet) and [Ftfy](https://github.com/LuminosoInsight/python-ftfy) (For unicode and lyrics stuff)

# Further improvements:
* Find a better way to get Genius.com url 
* Make a lyrics box that displays what we scraped
* Make it so users can manually insert Titles and Artists for songs 
* Maybe implement detecting/translating non-english lyrics

