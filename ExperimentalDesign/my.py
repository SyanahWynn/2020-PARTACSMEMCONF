#!/usr/bin/env python
# -*- coding: utf-8 -*-
# My functions.

from __future__ import division
from psychopy import sound
from psychopy import visual
from psychopy import core, clock, event, tools
import csv, os, time, pip
from psychopy import prefs
# pygame has a worse latency as compared to pyo!!!
prefs.general['audioLib'] = ['pygame'] # this line probably does not do anything (change it manually in psychopy)
import numpy as np
from win32api import GetSystemMetrics # screen resolution
import math
from rusocsci import buttonbox

## Function section

def getGridloc(window,nx,ny,locs):
    # define the vertical line positions
    stepx = 2/nx
    stepy = 2/ny
    boundx = np.arange(-1,1.1,stepx)
    boundy = np.arange(1,-1.1,-stepy)
    midx = np.arange(-1+(stepx/2),.99,stepx)
    midx = np.tile(midx,(1,ny))
    midy = np.arange(1-(stepy/2),-.99,-stepy)
    midy2=()
    for my in range(0,ny):
        midy2 = np.append(midy2,np.tile(midy[my],(1,nx)))
    locs = np.dstack((midx,midy2))
    locs=[locs,boundx,boundy]
    return locs


def makeGrid(window,nx,ny):
    # define the vertical line positions
    stepx = 2/nx
    locx = np.arange(-1+stepx,.99,stepx)
    stepy = 2/ny
    locy = np.arange(-1+stepy,.99,stepy)
    for lx in locx:
        visual.Line(window,units='norm',start=(lx,-1),end=(lx,1),lineColor='black').draw()
    for ly in locy:
        visual.Line(window,units='norm',start=(-1,ly),end=(1,ly),lineColor='black').draw()
    #window.flip()

def getCharacter(window, question="Press any key to continue"):
	message = visual.TextStim(window, text=question)
	message.draw()
	window.flip()
	c = event.waitKeys()
	if c:
		return c[0]
	else:
		return ''

def introScreen(window, question="Press any key to continue"):
    message = visual.TextStim(window, text=question)
    message.draw()
    window.flip()
    core.wait(3.000)
    c = event.waitKeys()
    if c:
        return c[0]
    else:
        return ''

def blankScreen(window, wait = 1.0, text = ""):
	"""Wait for a specified amount of seconds."""
	message = visual.TextStim(window, text=text)
	message.draw()
	window.flip()
	c = event.waitKeys(maxWait=wait, keyList = [])

def fixedBreak(window,wait=30.000,text=""):
    message = visual.TextStim(window, text=text)
    message.pos = [0, 0]
    message.draw()
    starttime = clock.getTime()
    curtime = starttime + wait - clock.getTime()
    while curtime > 1:
        curtime = starttime + wait - clock.getTime()
        cntdwntext = " nog " + str(round(curtime,0)) + " seconden pauze"
        #cntdwn = visual.TextStim(window, text=cntdwntext)
        cntdwn = visual.TextBox(
            window=window,
            text=cntdwntext,
            font_size=20,
            font_color=[1,1,1],
            color_space='rgb',
            size=(1.8,.1),
            pos=(.6,-.5),
            units='norm'
            )
        message.draw()
        cntdwn.draw()
        print(cntdwntext)
        window.flip()
        core.wait(1)

def restEEG(win,bb,block_dur, number_blocks,marker_open,marker_closed):
    tone = sound.Sound(700,secs=0.5)
    c = []
    message = visual.TextStim(win,text="Welkom. \n\nWe beginnen met een rustmeting van het EEG signaal. Blijft u rustig zitten en volg de instructies op het scherm (sluiten/open uw ogen). Als de instructies veranderen, wordt u gewaarschuwd door een geluid.")
    message.draw()
    win.flip()
    event.waitKeys()
    bb.sendMarker(val=1)
    core.wait(0.01)
    bb.sendMarker(val=0)
    for block in range(1,number_blocks+1):
        tone.play()
        if block%2 != 0: #uneven block
            eegmarker = marker_open
            message = visual.TextStim(win, text="Open uw ogen")
        elif block%2 == 0: #even blocks
            eegmarker = marker_closed
            message = visual.TextStim(win, text="Sluit uw ogen")
        bb.sendMarker(val=eegmarker)
        core.wait(0.001)
        bb.sendMarker(val=0)
        startTime = core.getTime()
        while core.getTime() < (startTime+block_dur) and c == []:
            message.draw()
            win.flip()
            c = event.getKeys(['escape'])
        print(core.getTime()-startTime)
    bb.sendMarker(val=9)
    core.wait(0.001)
    bb.sendMarker(val=0)
    tone.play()
    message = visual.TextStim(win,text="Open uw ogen. Dit is het einde van de rustmeting.")
    message.draw()
    win.flip()
    core.wait(2.000)

def lights(light_timing,running,BB):
    while running:
        marker = 1
        if BB:
            bb.sendMarker(val=marker)
        else:
            print("on")
        core.wait(light_timing)
        marker = 0
        if BB:
            bb.sendMarker(val=marker)
        else:
            print("off")
        core.wait(light_timing)

def openDataFile(ppn=0):
	"""open a data file for output with a filename that nicely uses the current date and time"""
	directory= "data"
	if not os.path.isdir(directory):
		os.mkdir(directory)
	try:
		filename="{}/{}_{}.dat".format(directory, ppn, time.strftime('%Y-%m-%dT%H:%M:%S')) # ISO compliant
		datafile = open(filename, 'wb')
	except Exception as e:
		filename="{}/{}_{}.dat".format(directory, ppn, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
		datafile = open(filename, 'wb')
	return datafile

def openCSVFile(ppn=0):
	"""open a data file for output with a filename that nicely uses the current date and time"""
	directory= "data"
	if not os.path.isdir(directory):
		os.mkdir(directory)
	try:
		filename="{}/{}_{}.csv".format(directory, ppn, time.strftime('%Y-%m-%dT%H:%M:%S')) # ISO compliant
		datafileCSV = open(filename, 'wb')
	except Exception as e:
		filename="{}/{}_{}.csv".format(directory, ppn, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
		datafileCSV = open(filename, 'wb')
	return datafileCSV

def getYN(window, question="Y or N"):
	"""Wait for a maximum of two seconds for a y or n key."""
	message = visual.TextStim(window, text=question)
	message.draw()
	window.flip()
	c = event.waitKeys(maxWait=2.0, keyList = ['y', 'n'])
	if c:
		return c[0]
	else:
		return ''

def getString(window, question="Type: text followed by return"):
    string = ""
    while True:
        message = visual.TextStim(window, text=question+"\n"+string)
        message.draw()
        window.flip()
        c = event.waitKeys()
        if c[0] == 'return':
            return string
        elif c[0] == 'backspace' or c[0] == 'delete':
            string = ""
        else:
            string = string + c[0]
lookup = {
          'space': ' ',
    'exclamation': '!',
    'doublequote': '"',
          'pound': '#',
         'dollar': '$',
        'percent': '%',
      'ampersand': '&',
     'apostrophe': '\'',
      'parenleft': '(',
     'parenright': ')',
       'asterisk': '*',
           'plus': '+',
          'comma': ',',
          'minus': '-',
         'period': '.',
          'slash': '/',
          'colon': ':',
      'semicolon': ';',
           'less': '<',
          'equal': '=',
        'greater': '>',
       'question': '?',
             'at': '@',
    'bracketleft': '[',
      'backslash': '\\',
   'bracketright': ']',
    'asciicircum': '^',
     'underscore': '_',
      'quoteleft': '`',
      'braceleft': '{',
            'bar': '|',
     'braceright': '}',
     'asciitilde': '~',
   'num_multiply': '*',
        'num_add': '+',
  'num_separator': ',',
   'num_subtract': '-',
    'num_decimal': '.',
     'num_divide': '/',
          'num_0': '0',
          'num_1': '1',
          'num_2': '2',
          'num_3': '3',
          'num_4': '4',
          'num_5': '5',
          'num_6': '6',
          'num_7': '7',
          'num_8': '8',
          'num_9': '9',
      'num_equal': '=',
}

def getString2(window, question="Type: text followed by return"):
	"""Return a string typed by the user, much improved version."""
	string = ''
	capitalizeNextCharacter = False
	while True:
		message = visual.TextStim(window, text=question+"\n"+string)
		message.draw()
		window.flip()
		c = event.waitKeys()[0]
		if len(c)==1:
			# add normal characters (charcters of length 1) to the string
			if capitalizeNextCharacter:
				string += c.capitalize()
				capitalizeNextCharacter = False
			else:
				string += c
		elif c == 'backspace' and len(string)>0:
			# shorten the string
			string = string[:-1]
		elif c == 'escape':
			# return no string
			return ''
		elif c == 'lshift' or  c == 'rshift':
			# pressing shift will cause precise one character to be capitalized
			capitalizeNextCharacter = True
		elif c == 'return' or c == 'num_enter':
			# return the string typed so far
			return string
		elif c in lookup.keys():
			# add special characters to the string
			string += lookup[c]
		else:
			# ignore other special characters
			pass


def showText(window, inputText="Text"):
	message = visual.TextStim(window, alignHoriz="center", text=inputText)
	message.draw()
	window.flip()




def getStimulusInputFile(fileName):
	"""Return a list of trials. Each trial is a list of values."""
	# prepare a list of rows
	rows = []
	# open the file
	inputFile = open(fileName, 'rb')
	# connect a csv file reader to the file
	reader = csv.reader(inputFile, delimiter=',')
	# discard the first row, containing the column labels
	reader.next()
	# read every row as a list of values and append it to the list of rows
	for row in reader:
		rows.append(row)
	inputFile.close()
	return rows

def getStimulusInputFileDict(fileName):
	"""Return a list of trials. Each trial is a dict."""
	# prepare a list of rows
	rows = []
	# open the file
	inputFile = open(fileName, 'rb')
	# connect a csv dict file reader to the file
	reader = csv.DictReader(inputFile, delimiter=';')
	# read every row as a dict and append it to the list of rows
	for row in reader:
		rows.append(row)
	inputFile.close()
	return rows
	
def debugLog(text):
	tSinceMidnight = clock.getTime()%86400
	tSinceWholeHour = tSinceMidnight % 3600
	minutes = tSinceWholeHour / 60
	hours = tSinceMidnight / 3600
	seconds = tSinceMidnight % 60
	#print("log {:02d}:{:02d}:{:2.3f}: {}".format(int(hours), int(minutes), seconds, text))
	print("log {:02d}:{:02d}:{:f}: {}".format(int(hours), int(minutes), seconds, text))


#print (getStimulusInputFileLists("template_stimuli.csv"))
