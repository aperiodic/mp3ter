#!/usr/bin/env python

import re, sys
import eyed3

##
## Constant Values (Mostly Useful Regexen)
##

FEATURING_RGX = re.compile(r'\(?\[?(featuring|Featuring|feat\.|Feat\.|feat|Feat|ft\.|Ft\.|ft|Ft)([^\(\)\[\]]+)\)?\]?')
VERSION_RGX = re.compile(r'[\(\[]([^\)^\]]+)(Remix|Dub|Version)[\)\]]')

TITLE_MINOR_WORDS = [# articles
                     'the' ,'a' ,'an'
                    # conjunctions
                    ,'if' ,'and' ,'but' ,'for' ,'nor' ,'or' ,'yet'
                    # prepositions
                    ,'in' ,'on' ,'at' ,'to' ,'by' ,'from' ,'of' ,'as' ,'off'
                    ,'per' ,'than' ,'via' ,'with'
                    ]

LOWER_UPPER_RGX = re.compile(r"[a-z][A-Z]")
LOWER_RGX = re.compile(r"[a-z]")
UPPER_RGX = re.compile(r"[A-Z]")

##
## Sequence Utilities
##

def besidesFirstAndLast(seq):
  if len(seq) <= 2:
    return []
  else:
    ret = seq.copy()
    ret.pop()
    ret.pop(0)
    return ret

##
## String Utilities
##

def lowercaseCharacterCount(s):
  return len(LOWER_RGX.findall(s))


def uppercaseCharacterCount(s):
  return len(UPPER_RGX.findall(s))


def quoted(s):
  return '"' + s + '"'


def splitAtIndex(s, i):
  return [s[0:i], s[i:]]

##
## Title Case
##

def downcaseIfMinor(word):
  if word.lower() in TITLE_MINOR_WORDS:
    return word.lower()
  else:
    return word


def hasStrangeCapitalization(songName):
    if LOWER_UPPER_RGX.search(songName):
        return True

    uc_count = uppercaseCharacterCount(songName)
    lc_count = lowercaseCharacterCount(songName)
    if uc_count == 0 or lc_count == 0:
        return True
    elif uc_count > lc_count:
        return True

    for word in songName.split():
      if word == word.upper() and len(word) > 1 and word.find('.') < 0:
        return True

    return False


def notRomanAlphabet(title):
    return (uppercaseCharacterCount(title) == 0
            and lowercaseCharacterCount(title) == 0)


def titleCase(title):
    if notRomanAlphabet(title) or hasStrangeCapitalization(title):
        return title

    words = title.split()
    if len(words) <= 2:
      return title
    else:
      cased = []
      cased.append(words[0])
      for word in besidesFirstAndLast(words):
        cased.append(downcaseIfMinor(word))
      cased.append(words.pop()) # words no longer referenced here
      cased = ' '.join(cased)

      pre_space = re.match('(\s+)', title)
      post_space = re.search('(\s+)$', title)

      # this conditional ensures the function preserves leading
      # & trailing whitespace
      if pre_space and post_space:
        return pre_space.group(1) + cased + post_space.group(1)
      elif pre_space:
        return pre_space.group(1) + cased
      elif post_space:
        return cased + post_space.group(1)
      else:
        return cased

##
## Formatting Featured Artists & Version
##

def formatFeaturedArtists(title):
    if FEATURING_RGX.search(title):
        with_ands = FEATURING_RGX.sub('(ft.\\2)', title)
        return re.sub(r'\band\b', '&', with_ands)
    return title


def formatSongVersion(title):
    if VERSION_RGX.search(title):
        return VERSION_RGX.sub('(\\1\\2)', title)
    return title


def fixBareFeaturingWithVersion(title):
    return re.sub(r' \)\(', ') (', title)


def formatSongInfo(info):
    formatted = formatSongVersion(formatFeaturedArtists(info))
    return fixBareFeaturingWithVersion(formatted)


def formatSongName(songName):
    version_match = VERSION_RGX.search(songName)
    if version_match:
        title, version = splitAtIndex(songName, version_match.start())
        return titleCase(title) + ' ' + formatSongVersion(version)

    paren_match = re.match('(.*?)\((.*)\)(.*)', songName)
    if paren_match:
      b4_paren = titleCase(paren_match.group(1))
      parenthetical = formatSongName(paren_match.group(2))
      after_paren = titleCase(paren_match.group(3))
      return b4_paren + '(' + parenthetical + ')' + after_paren

    return titleCase(songName)


def formatTitleTag(title):
    for info_begin in [FEATURING_RGX, VERSION_RGX]:
        title_info_begin = info_begin.search(title)
        if title_info_begin:
            name, info = splitAtIndex(title, title_info_begin.start())
            return formatSongName(name) + formatSongInfo(info)
    return formatSongName(title)

##
## Editing MP3 Files
##

def loadMp3File(path):
  return eyed3.load(path)


def setTitle(mp3File, title):
  mp3File.tag.title = title
  mp3File.tag.save()

##
## Parsing Arguments
##

def findMP3sInArgs(argv):
    if len(argv) < 2:
        raise IndexError('At least one MP3 file to edit must be given as an argument')
    files = argv.copy()
    files.pop(0)
    return files

##
## Main
##

files = findMP3sInArgs(sys.argv)
for f in files:
    mp3 = loadMp3File(f)
    orig_title = mp3.tag.title
    formatted_title = formatTitleTag(orig_title)
    if formatted_title != orig_title:
        print(quoted(orig_title), "->", quoted(formatted_title))
        setTitle(mp3, formatted_title)
    else:
        print("Keeping original title", quoted(orig_title))
