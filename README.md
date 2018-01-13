# mp3ter

Install dependencies with setuptools:
```sh
python setup.py install
```
Then put the scripts somewhere in your $PATH if you want.

The format-title script takes MP3 filepaths as arguments.
```sh
format-title.py Thriller.mp3
```

## format-title.py

### Intended Usage

The format-title script is designed to touch up titles that are reasonably well-formatted to begin with.
It will not work very well on titles that have completely different capitalization or whitespace conventions that you want to fix, such as `scene_style_formatting`.
The benefit of this decision is that the script detects and preserves artist-intended unusual capitalization.

### Title Formatting

The script does its work by splitting the song title into two parts: its name and an optional trailing info string with any featured artists or version label (e.g. 'Sabrepulse Remix').
Most of the time, there's no info part and the entire title is just the song name.

It then formats the name portion of the title to be ALA-style title case, with the small difference that it also downcases the most comon four-word prepositions ('from' and 'with').

If there is a song info portion, it replaces any square brackets around the featured artists or the version label with parentheses, and replaces any 'ands' in the featured artists string with ampersands.

### Implementation Tradeoffs

This script is not perfect because it performs naive word matching instead of part of speech tagging, so it will downcase the preposition words even when they are not being used prepositions in the title.
The goal is for it to do the bulk of the work (esp. on the featured artist tags, which can be a slog otherwise) and that's all; I can make minor edits the few times it does goof up.
