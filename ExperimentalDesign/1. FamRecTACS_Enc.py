#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FamRecEEG task details

Encoding stimuli: 200 words
Encoding blocks: 2
Encoding stimulus time: 1 sec
Encoding fixation time: 1 sec
Encoding total duration: min 14 min
Retrieval stimuli: 400 words (200 old, 200 new)
Retrival blocks: 4
Retrieval stimulus time: <5 sec
Retrieval fixation time: .5 sec
Retrieval confidence judgement time: <5 sec
Retrieval total duration: ~min 28 min
"""

from psychopy import sound
from psychopy import visual
from psychopy import core, clock, event
import csv, random
import my # import my own functions
import pip
import os
from rusocsci import buttonbox
from psychopy import prefs
# pygame has a worse latency as compared to pyo!!!
prefs.general['audioLib'] = ['pygame'] # this line probably does not do anything (change it manually in psychopy)
import numpy as np
import random


## Setup Section
#VARIABLES
blocks = 2
stimdur = 1
fixdur = 1
cuedur = [.9,.95,1,1.05,1.1]
practrials = 20
enctrials = 200
pauzetrls = np.arange(practrials+1,enctrials+practrials,enctrials/blocks)
pauzetrls = pauzetrls[1:]
gridx = 4
gridy = 4
EEG=0
if EEG == 1:
    bb = buttonbox.Buttonbox()
else:
    class fakebuttonbox(object): # no idea why these steps were needed #pythonnoob
        def __init__(self):
            def sendMarker(val):
                if val!=0:
                    print(val)
            self.sendMarker = sendMarker
    bb = fakebuttonbox()
    bb.sendMarker(val='No EEG')

win = visual.Window([800,600], fullscr=True, monitor="testMonitor", units='norm',allowGUI=False)
#win = visual.Window([800,600], fullscr=False, monitor="testMonitor")

# get info for this participant
session = my.getString(win, "Please enter session number:")
ppn = my.getString(win, "Please enter participant number:")
gender = my.getString(win, "Please enter participant gender:")
age = my.getString(win, "Please enter participant age:")
visual.TextStim(win,text='start-up').draw()
win.flip()

# determine inputfile
inputfile = "SubjectFiles/" + ppn + "_session" + session + "_enc.csv"

# read stimuli file
trials = my.getStimulusInputFile(inputfile)
wordsColumn = 0     #number = trials[trialNumber][wordColumn]
posColumn = 2     #number = trials[trialNumber][posColumn]

# turn the text strings into stimuli
textStimuli = []
for trial in trials:
    # append this stimulus to the list of prepared stimuli
    textStimuli.append(visual.TextStim(win,text=trial[wordsColumn]))
    #imageStimuli.append(visual.ImageStim(win=window, size=[0.5,0.5], image="image/"+row[0]))
    #soundStimuli.append(visual.ImageStim(win=window, size=[0.5,0.5], image="image/"+row[0]))

#fixation cross
fixation = visual.ShapeStim(win,
    vertices=((0, -0.01), (0, 0.01), (0,0), (-0.01,0), (0.01, 0)),
    lineWidth=2,
    closeShape=False,
    lineColor='white',
    units='height'
)
cue = visual.Circle(win,
    radius=.01,
    edges=32,
    units='norm'
)

# mouse set-up
mouse = event.Mouse(visible=True, newPos=None, win=None)

# open data output file
datafile = my.openDataFile(ppn + "_session_" + session + "_enc")
datafileCSV = my.openCSVFile(ppn + "_session_" + session + "_enc")
libraryfile = my.openDataFile(ppn + "_session_" + session + "_enc" + "_library")
# connect it with a csv writer
writer = csv.writer(datafile, delimiter=";")
writerCSV = csv.writer(datafileCSV, delimiter=";")
tempwriter = csv.writer(libraryfile, delimiter=";")
# create output file header
writer.writerow([
    "ppn",
    "gender",
    "age",
    "word",
    "session",
    "pleasure_key",
    "pleasure_rt",
    "position",
    "fixationTime",
    "cue_jit"
    ])
writerCSV.writerow([
    "ppn",
    "gender",
    "age",
    "word",
    "enc_ses",
    "enc_resp",
    "enc_RT",
    "position",
    "fixationTime",
    "cue_jit"
    ])
tempwriter.writerow([__file__])
for pkg in pip.get_installed_distributions():
    tempwriter.writerow([pkg.key, pkg.version])

## REST EEG
restEEG = my.getString(win, "RestEEG")
if restEEG == '':
    my.restEEG(win,bb, block_dur=59.5, number_blocks=4,marker_open=2,marker_closed=3)

## Experiment Section
mouse.setVisible(0)
# show welcome screen
if int(ppn)%2==0:
    my.introScreen(win, "U krijgt straks woorden te zien op het scherm. Is het woord een natuurlijk product, drukt u op de linker muisknop, is het woord door mensen gemaakt, drukt u op de rechter muisknop. \n\nnatuurlijk <--\nmensgemaakt -->\n\ndruk op spatie om te beginnen aan het oefenblok")
else:
    my.introScreen(win, "U krijgt straks woorden te zien op het scherm. Is het woord door mensen gemaakt, drukt u op de linker muisknop, is het woord een natuurlijk product, drukt u op de rechter muisknop. \n\nmensgemaakt <--\nnatuurlijk -->\n\ndruk op spatie om te beginnen aan het oefenblok")
mouse.setPos([0, 0])
# get the positions
locs = []
locs = my.getGridloc(win,gridx,gridy,locs)
locs=locs[0]
startTime = clock.getTime() # clock is in seconds
i=0
while i < len(trials):
    if i == 0:
        mouse.setPos([0, 0])
        print("start practice")
        bb.sendMarker(val=99)
        core.wait(0.001)
        bb.sendMarker(val=0)
        # present fixation
        my.makeGrid(win,gridx,gridy)
        fixation.draw()
        win.flip()
        bb.sendMarker(val=40)
        core.wait(0.001)
        bb.sendMarker(val=0)
        fixationTime = clock.getTime()
        core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
        mouse.setVisible(0)
        mouse.clickReset(buttons=(0, 1, 2))
    if i == practrials:
        mouse.setPos([0, 0])
        my.blankScreen(win)
        answer = my.getCharacter(win, "Dit is het einde van het oefenblok, wilt u nog een keer oefenen? [j/n]")
        if answer[0] == "j":
            i=0
            # present fixation
            my.makeGrid(win,gridx,gridy)
            fixation.draw()
            win.flip()
            bb.sendMarker(val=40)
            core.wait(0.001)
            bb.sendMarker(val=0)
            fixationTime = clock.getTime()
            core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
            mouse.setVisible(0)
            mouse.clickReset(buttons=(0, 1, 2))
        elif answer[0] == "n":
            i=i
            bb.sendMarker(val=10)
            core.wait(0.001)
            bb.sendMarker(val=0)
            core.wait(1.000)
            # present fixation
            my.makeGrid(win,gridx,gridy)
            fixation.draw()
            win.flip()
            bb.sendMarker(val=40)
            core.wait(0.001)
            bb.sendMarker(val=0)
            fixationTime = clock.getTime()
            core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
            mouse.setVisible(0)
            mouse.clickReset(buttons=(0, 1, 2))
        else:
            i=0
            # present fixation
            my.makeGrid(win,gridx,gridy)
            fixation.draw()
            win.flip()
            bb.sendMarker(val=40)
            core.wait(0.001)
            bb.sendMarker(val=0)
            fixationTime = clock.getTime()
            core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
            mouse.setVisible(0)
            mouse.clickReset(buttons=(0, 1, 2))
    if i in pauzetrls:
        bb.sendMarker(val=90)
        core.wait(0.001)
        bb.sendMarker(val=0)
        mouse.setPos([0, 0])
        my.fixedBreak(win, wait = 30.000, text = "Pauze!")
        bb.sendMarker(val=91)
        core.wait(0.001)
        bb.sendMarker(val=0)
        # present fixation
        my.makeGrid(win,gridx,gridy)
        fixation.draw()
        win.flip()
        bb.sendMarker(val=40)
        core.wait(0.001)
        bb.sendMarker(val=0)
        fixationTime = clock.getTime()
        core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
        mouse.setVisible(0)
        mouse.clickReset(buttons=(0, 1, 2))

    mouse.setVisible(0)
    trial = trials[i]


    # present cue
    cue.pos = locs[0,(int(trial[posColumn])-1)]
    my.makeGrid(win,gridx,gridy)
    cue.draw()
    win.flip()
    bb.sendMarker(val=45)
    core.wait(0.001)
    bb.sendMarker(val=0)
    fixationTime = clock.getTime()
    random.shuffle(cuedur)
    core.wait(cuedur[0])
    mouse.setVisible(0)
    mouse.clickReset(buttons=(0, 1, 2))
    #print(cuedur[0])
    # present stimulus text and wait a maximum of stimdur for a response
    textStimuli[i].pos = locs[0,(int(trial[posColumn])-1)]
    textTime = clock.getTime()
    bb.sendMarker(val=20)
    core.wait(0.001)
    bb.sendMarker(val=0)
    fix=True
    while clock.getTime() < (textTime + stimdur+fixdur) and mouse.getPressed(getTime=True)[0][0] == 0 and mouse.getPressed(getTime=True)[0][2] == 0:
        my.makeGrid(win,gridx,gridy)
        if clock.getTime() < (textTime + stimdur):
            textStimuli[i].draw()
        else:
            fixation.draw()
            if fix:
                bb.sendMarker(val=40)
                core.wait(0.001)
                bb.sendMarker(val=0)
            fix=False
        win.flip()
    responseTime = mouse.getPressed(getTime=True)[1][0] + mouse.getPressed(getTime=True)[1][2]  # one of the 2 is 0 always
    print(mouse.getPressed(getTime=True))
    if mouse.getPressed(getTime=True)[0][0]==1: #left
        if int(ppn)%2==0:
            click='nat'
            bb.sendMarker(val=33)
            core.wait(0.001)
            bb.sendMarker(val=0)
        else:
            click='hum'
            bb.sendMarker(val=35)
            core.wait(0.001)
            bb.sendMarker(val=0)
    elif mouse.getPressed(getTime=True)[0][2]==1: # right
        if int(ppn)%2==0:
            click='hum'
            bb.sendMarker(val=35)
            core.wait(0.001)
            bb.sendMarker(val=0)
        else:
            click='nat'
            bb.sendMarker(val=33)
            core.wait(0.001)
            bb.sendMarker(val=0)
    # continue stimulus presentation for stimdur
    while clock.getTime() < (textTime + stimdur+fixdur):
        my.makeGrid(win,gridx,gridy)
        if clock.getTime() < (textTime + stimdur):
            textStimuli[i].draw()
        else:
            fixation.draw()
            if fix:
                bb.sendMarker(val=40)
                core.wait(0.001)
                bb.sendMarker(val=0)
            fix=False
        win.flip()

    if responseTime == 0:
        click='none'
        bb.sendMarker(val=38)
        core.wait(0.001)
        bb.sendMarker(val=0)

    print("{}, text: {}, key: {}, text: {}".format( i+1, trial[wordsColumn], click, responseTime) )

    # write result to data file
    key = event.getKeys()
    if key==[]:
        key.append("none")

    if i>=practrials: # only save the experimental trials
        writer.writerow([
            ppn,
            gender,
            age,
            trial[wordsColumn],
            session,
            click,
            "{:.3f}".format(responseTime),
            trial[posColumn],
            "{:.3f}".format(fixationTime - startTime),
            cuedur[0]
            ])
        writerCSV.writerow([
            ppn,
            gender,
            age,
            trial[wordsColumn],
            session,
            click,
            "{:.3f}".format(responseTime),
            trial[posColumn],
            "{:.3f}".format(fixationTime - startTime),
            cuedur[0]
            ])

    if key[0]=='escape':
        break
    i = i+1
datafile.close()
datafileCSV.close()

bb.sendMarker(val=13)
core.wait(0.001)
bb.sendMarker(val=0)

# show goodbye screen
my.showText(win, "Einde van de leer fase")
core.wait(1.000)

## REST EEG
my.restEEG(win,bb, block_dur=59.5, number_blocks=4,marker_open=4,marker_closed=5)

mouse.setVisible(1)
## Closing Section
win.close()
core.quit()
