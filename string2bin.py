#!/usr/bin/python

import sys
import os
import Image

imgPath = "./silkscreen/"
binValues = {}

# dictionary for translating filenames of special characters
translation = {
	'_semicolon': ';',
	'_colon': ':',
	'_comma': ',',
	'_period': '.',
	'_question': '?',
	'_exclamation': '!',
	'_dash': '-', 
	'_apos': '\'',
	'_quotes': '\"',
	'_heart': '|'
	 }
	 
# same dictionary with keys/values swapped
# useful for getting the appropriate file when given a special character
revtranslation = {}
for key, val in translation.iteritems():
	revtranslation[val] = key

# simple function for getting the contents of a directory
# returns a list of the files
# NOTE: this is not recursive, will give strange results if there are subdirs
def getDirContents(path,extension="png"):
	fileList = []
	tree = os.walk(path)
	for directory in tree:
		for file in directory[2]:
			if (file.endswith("png")):
				fileList.append(file)
	return fileList

# receives an Image object
# returns a string with binary values
def img2bin(img):
	binValue = ""
	columns = img.size[0]
	rows = img.size[1]
	for col in range(columns):
		for row in range(rows):
			colorValue = img.getpixel((col,row))[0]
			if colorValue == 0:
				# pixel is black; return 1
				binValue = binValue + "1"
			elif colorValue == 255:
				# pixel is white; return 0
				binValue = binValue + "0"
			else:
				print "VALUE ERROR: check img2bin function" # debug only
	# add an empty column for letterspacing
	binValue = binValue + "00000"
	return binValue

# accepts a single character string
# returns binary value of the bitmap character's colour values
def char2bin(char):
	if char == " ":
		return "000000000000000"
	specialchars = revtranslation.keys()
	#print char
	if len(char) > 1:
		print "ERROR: input string has more than 1 character"
	# is it a special character? check if it passes through the next statement
	# if so, reverse translate it to get the appropriate filename
	try:
		char = revtranslation[char]
	except KeyError:
		pass
	filename = char + ".png"	
	img = Image.open(imgPath + filename)
	return img2bin(img)
	
def string2bin(string):
	binValue = ""
	for index in range(len(string)):
		binValue = binValue + char2bin(string[index])
	return binValue
	
# End of function definition	

def run(data):
    '''Accepts a string and returns a binary output for use in Lightwriter.'''
    global fileList, imgPath
    
    # create the file list
    fileList = getDirContents(imgPath)

    for file in fileList:
	    # first load the image
	    img = Image.open(imgPath + file)
	    # then make sure we get proper representations of special chars
	    key = file.split('.')[0]
	    if (len(key) > 1):
		    # translate the names of special characters
		    key = translation[key]

    # now create the output string	
    output = string2bin(data)

    # check for output length before spitting it out
    # more than 400 and arduino flips
    if len(output) > 800:
	    raise IOError("String is too big!")
    else:
	    return output
