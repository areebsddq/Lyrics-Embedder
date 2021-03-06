from PyQt5.QtWidgets import *
from PyQt5 import QtCore

# For fetching and manipulating the mp3 files
from tkinter import *
from tkinter.filedialog import askopenfilenames
from mutagen.id3 import ID3NoHeaderError
from mutagen.id3 import ID3, USLT

# To scrape the webpages for lyrics
import urllib.request
import urllib.error
import re
import sys
import threading
import ntpath

# For decoding the lyrics to unicode
import chardet
import ftfy
import unicodedata


def remove_accent_letters(str):
    nfkd_form = unicodedata.normalize('NFKD', str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def remove_brackets(str):
    return re.sub(r"\(.+\)", "", str)


def strip_tag_details(word):
    for c in (",", "'", "'", "`", "’", "?", ".", "!", "*"):
        word = word.replace(c, "")

    word = word.replace("&", "and")
    word = word.replace("/", " ")
    word = remove_accent_letters(word)

    return word


def create_url(title, artist):
    # In case there are several artists
    artist = artist.split(",")[0]

    title = strip_tag_details(title)
    artist = strip_tag_details(artist)

    wordList = artist.split() + title.split()
    wordList.append("lyrics")

    urlTrail = '-'.join(wordList)

    url = "https://genius.com/" + urlTrail

    return url


def get_lyrics(title, artist):
    url = create_url(title, artist)

    try:
        # We give a known user agent so that the site doesn't block access.
        req_obj = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(req_obj)

    except:
        try:
            url = create_url(remove_brackets(title), artist)

            req_obj = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            page = urllib.request.urlopen(req_obj)

        except:
            print("Error with url (may not exist): " + url, file=sys.stderr)
            return

    page_data = page.read()

    char_dict = chardet.detect(page_data)
    enc_type = char_dict['encoding']

    decode_fail = False

    try:
        page_data.decode(enc_type)

    except:
        print("Error decoding data for: " + title, file=sys.stderr)
        decode_fail = True

    # Find lyrics in html data
    lyrics_list = re.findall(r'<div class="lyrics">.*?</div>', str(page_data))

    if not len(lyrics_list) == 1:
        print("Error scraping for lyrics for:" + title, file=sys.stderr)
        return

    lyrics = str(lyrics_list[0])

    # Scraper escapes \n and other chars automatically so we have to undo that.
    lyrics = lyrics.encode().decode('unicode_escape')

    # Was getting error here in a weird edge case
    try:
        # Remove extra html junk
        lyrics = lyrics.replace("<br>",'')
        lyrics = lyrics.split("<p>")[1]
        lyrics = lyrics.split("</p>")[0]

    except:
        pass

    html_junk = re.findall(r"<[\s\S]*?>", str(lyrics))

    for junk in html_junk:
        lyrics = lyrics.replace(junk, "")

    # To fix random unicode text issues that may pop up
    lyrics = ftfy.fix_text(lyrics)

    # Some cases that fail decoding work with this instead:
    if decode_fail:
        try:
            lyrics = lyrics.encode(enc_type).decode(enc_type)

        except:
            pass

    return lyrics


def embedd_lyrics(fileName, lyrics):
    try:
        tags = ID3(fileName)
    except ID3NoHeaderError:
        tags = ID3()

    if not (len(tags.getall(u"USLT::'en'")) == 0):
        tags.delall(u"USLT::'en'")
        tags.save(fileName)

    # Add lyrics to tag object
    try:
        tags[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'eng', text=lyrics))

    except:
        print("Error inserting lyrics for: " + ntpath.basename(fileName), file=sys.stderr)
        return False

    try:
        tags.save(fileName, v2_version=3)

    except Exception:
        print("Error modifying mp3 file", file=sys.stderr)
        return False

    return True


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.songButton = QPushButton("Select Songs")
        self.songButton.clicked.connect(self.songClick)

        self.lyricsDict = {}
        self.songList = QListWidget()

        self.lyricsBox = QLineEdit()
        self.lyricsBox.resize(600, 600)
        self.lyricsBox.sizePolicy()
        self.lyricsBox.setReadOnly(True)

        vBox = QVBoxLayout()
        vBox.addWidget(self.songButton, 0, QtCore.Qt.AlignTop)
        vBox.addWidget(self.lyricsBox, 0, QtCore.Qt.AlignVCenter)

        mainLayout = QGridLayout()
        mainLayout.addLayout(vBox, 0, 0)
        mainLayout.addWidget(self.songList, 0, 1)

        self.setLayout(mainLayout)

        self.setWindowTitle("Mp3 Lyrics Embedder")
        self.setGeometry(600, 300, 700, 500)

    def songClick(self):
        root = Tk()
        root.withdraw()
        songFiles = askopenfilenames(filetypes=(("Mp3 files", "*.mp3"),))

        t = threading.Thread(target=self.add_lyrics_to_song, args=(songFiles,))
        t.start()

    def add_lyrics_to_song(self, songFiles):
        songList = list(songFiles)

        for song in songList:
            try:
                sObj = ID3(song)
                title = str(sObj["TIT2"])
                artist = str(sObj["TPE1"])

            except:
                print("Error getting tags from song file: " + ntpath.basename(song), file=sys.stderr)
                continue

            lyrics = get_lyrics(title, artist)

            if lyrics:
                if embedd_lyrics(song, lyrics):
                    songIdentifier = ''.join([title, " - ", artist])

                    songListItem = QListWidgetItem(songIdentifier)
                    songListItem.setTextAlignment(4)
                    self.songList.addItem(songListItem)

                    self.lyricsDict[songIdentifier] = lyrics

                else:
                    songListItem = QListWidgetItem(''.join([title, " - ", artist, " Failed"]))
                    songListItem.setTextAlignment(4)
                    self.songList.addItem(songListItem)

        exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    screen = Window()
    screen.show()

    sys.exit(app.exec_())