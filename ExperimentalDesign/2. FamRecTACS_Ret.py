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

from __future__ import with_statement
from psychopy import sound
from psychopy import visual
from psychopy import core, clock, event, iohub
import csv, random
import my # import my own functions
import pip
import os
from rusocsci import buttonbox
from psychopy import prefs
# pygame has a worse latency as compared to pyo!!!
prefs.general['audioLib'] = ['pygame'] # this line probably does not do anything (change it manually in psychopy)
import numpy as np
import threading
import sys
import math

## Setup Section

win = visual.Window([800,600], fullscr=True, monitor="testMonitor", units='norm',allowGUI=False)
#win = visual.Window([800,600], fullscr=False, monitor="testMonitor")

#VARIABLES
blocks = 3
sourcedur = 5
vasdur = 5
fixdur = [.4,.45,.5,.55,.6]
practrials = 20
rettrials = 400
pauzetrls = np.arange(practrials+1,rettrials+practrials,rettrials/blocks)
pauzetrls = pauzetrls[1:]
#freq = 3.5 # in hetz (of the lights)
gridx = 4
gridy = 4
#mymarker = visual.TextStim(win,text='|',units='norm',color="black")
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

# get info for this participant
session = my.getString(win, "Please enter session number:")
ppn = my.getString(win, "Please enter participant number:")
curstim = my.getString(win, "Please enter stimulation code")
gender = my.getString(win, "Please enter participant gender:")
age = my.getString(win, "Please enter participant age:")

# determine inputfile
inputfile = "SubjectFiles/" + ppn + "_session" + session + "_ret.csv"

# read stimuli file
trials = my.getStimulusInputFile(inputfile)
wordsColumn = 0     #number = trials[trialNumber][numberColumn]
classColumn = 2       #name = trials[trialNumber][nameColumn]
stimulationColumn = 3       #name = trials[trialNumber][nameColumn]
posColumn = 4     #number = trials[trialNumber][posColumn]

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

# mouse set-up
mouse = event.Mouse(visible=True, newPos=None, win=None)

# open data output file
datafile = my.openDataFile(ppn + "_session_" + session + "_ret")
datafileCSV = my.openCSVFile(ppn + "_session_" + session + "_ret")
libraryfile = my.openDataFile(ppn + "_session_" + session + "_ret" + "_library")
# connect it with a csv writer
writer = csv.writer(datafile, delimiter=";")
writerCSV = csv.writer(datafileCSV, delimiter=";")
tempwriter = csv.writer(libraryfile, delimiter=";")
# create output file header
writerCSV.writerow([
    "ppn",
    "gender",
    "age",
    "word",
    "ret_ses",
    "ONclass",
    "VAS_rating",
    "VAS_RT",
    "OldNew_Accuracy",
    'sourceRT',
    'sourcePos',
    'sourceErr',
    'sourceStartposition',
    "stim",
    "enc_pos",
    "ret_pos",
    "enc_coor",
    "ret_coor",
    "CoorError",
    "fixationTime",
    "VAS_history"
    ])
writer.writerow([
    "ppn",
    "gender",
    "age",
    "word",
    "Retrieval_Session",
    "ONclass",
    "VAS_rating",
    "VAS_RT",
    "OldNew_Accuracy",
    'sourceRT',
    'sourcePos',
    'sourceErr',
    'sourceStartposition',
    "Stimulation",
    "EncodingPosition",
    "RetrievalPosition",
    "EncCoor",
    "RetCoor",
    "CoorError",
    "fixationTime",
    "VAS_history"
    ])
tempwriter.writerow([__file__])
for pkg in pip.get_installed_distributions():
    tempwriter.writerow([pkg.key, pkg.version])

## Experiment Section

# show welcome screen
my.introScreen(win, "U geeft aan op de schaal of u het woord eerder heeft gezien of niet, rekening houdend met hoe zeker u bent van uw keuze.\n\nindien nodig vragen wij u om aan te geven waar u het woord heeft gezien op het scherm.")
locs = []
locs = my.getGridloc(win,gridx,gridy,locs)
boundx=locs[1]
boundy=locs[2]
locs=locs[0]
startTime = clock.getTime() # clock is in seconds

i=0
while i < len(trials):
    if i == 0:
        print("start practice")
        bb.sendMarker(val=99)
        core.wait(0.001)
        bb.sendMarker(val=0)
    if i == practrials:
        my.blankScreen(win)
        answer = my.getCharacter(win, "Dit is het einde van het oefenblok, wilt u nog een keer oefenen? [j/n]")
        if answer[0] == "j":
            i=0
        elif answer[0] == "n":
            i=i
            bb.sendMarker(val=50)
            core.wait(0.001)
            bb.sendMarker(val=0)
            core.wait(1.000)
        else:
            i=0
    if i in pauzetrls:
        bb.sendMarker(val=90)
        core.wait(0.001)
        bb.sendMarker(val=0)
        my.fixedBreak(win, wait = 30.000, text = "Pauze!")
        bb.sendMarker(val=91)
        core.wait(0.001)
        bb.sendMarker(val=0)

    trial = trials[i]

    # present fixation
    random.shuffle(fixdur)
    fixation.draw()
    win.flip()
    bb.sendMarker(val=80)
    core.wait(0.001)
    bb.sendMarker(val=0)
    fixationTime = clock.getTime()
    core.wait(fixdur[0]) # note how the real time will be very close to a multiple of the refresh time
    #print(fixdur[0])
    mouse.setPos([0, -.4])
    print('')
    print("old (1) / new (2): {}".format(trial[classColumn]))
    # present stimulus text and wait a maximum of 5 second for a response
    VAS = visual.RatingScale(win,
        #mouseOnly=True,
        labels=("heel zeker oud","heel zeker nieuw"),
        textColor="black",
        markerColor="black",
        #marker=mymarker,
        #marker=visual.TextStim(win,text='|',units='norm',font_color=[1, 1, 1]),
        marker=visual.Line(
            win=win,
            start=(0,-.04),
            end=(0,.04),
            units="norm",
            lineColor=[-1, -1, -1],
        ),
        precision=100,
        scale=None,
        textSize = .5,
        showValue=False,
        low=0,
        high=100,
        markerStart = 5,
        maxTime = vasdur,
        tickMarks = 0.0,
        tickHeight=0.0 # hide ticks
        )
    #VAS.marker.opacity=0
    mouse.setVisible(1)
    textStimuli[i].pos = [0,0]
    if trial[classColumn] == "1":
        bb.sendMarker(val=53)
        core.wait(0.001)
        bb.sendMarker(val=0)
    elif trial[classColumn] == "2":
        bb.sendMarker(val=55)
        core.wait(0.001)
        bb.sendMarker(val=0)
    while VAS.noResponse:
        textStimuli[i].draw()
        VAS.draw()
        win.flip()
    key = event.getKeys()
    vasRating = VAS.getRating()
    vasRT = VAS.getRT()
    vashist=VAS.getHistory()
    print('history')
    print(vashist)

    if (trial[classColumn] == "1" and vasRating<50): #old & old
        acc = 11 #hit
    elif (trial[classColumn] == "1" and vasRating>50): #old & new
        acc = 12 #miss
    elif (trial[classColumn] == "2" and vasRating<50): #new & old
        acc = 21 # false alarm
    elif (trial[classColumn] == "2" and vasRating>50): #new & new
        acc = 22 #correct rejection
    else:
        acc = 99 # no response

    print("{}, text: {}, {}, rating: {} RT: {} acc: {}".format( i+1, trial[wordsColumn], trial[classColumn],  vasRating, vasRT, acc) )

    if key==[]:
        key.append("none")
    elif key[0]=='escape':
        break

    encPosGrid=[0,0]
    if trial[posColumn]!="":
        print(trial[posColumn])
        encPos = float(trial[posColumn])
        gridx = float(gridx)
        if encPos/gridx==int(encPos/gridx):
            encPosGrid[0]=((encPos/gridx-int(encPos/gridx))+1)*4
        else:
            encPosGrid[0]=(encPos/gridx-int(encPos/gridx))*4
        encPosGrid[1]=math.ceil(encPos/gridx)

    # source test
    if vasRating < 40:
        print("encoding position: {}".format(trial[posColumn]))
        # present fixation
        mouse.setVisible(0)
        random.shuffle(fixdur)
        fixation.draw()
        win.flip()
        bb.sendMarker(val=80)
        core.wait(0.001)
        bb.sendMarker(val=0)
        fixationTime = clock.getTime()
        core.wait(fixdur[0]) # note how the real time will be very close to a multiple of the refresh time
        #print(fixdur[0])
        startpos = locs[0,random.randrange(0,16)]
        startpos2=[0,0]
        startpos2[0]=startpos[0]
        startpos2[1]=startpos[1]
        startpos=startpos2

        mouse.setPos(newPos=(startpos))
        mouse.clickReset(buttons=(0, 1, 2))
        textTime = clock.getTime()
        bb.sendMarker(val=70)
        core.wait(0.001)
        bb.sendMarker(val=0)
        while clock.getTime() < (textTime + sourcedur) and mouse.getPressed(getTime=True)[0][0] == 0:
            textStimuli[i].pos = mouse.getPos()
            textStimuli[i].draw()
            my.makeGrid(win,gridx,gridy)
            win.flip()
        sourceRT = mouse.getPressed(getTime=True)[1][0]
        sourcePos = mouse.getPos()
        sourcePos2 = [0,0]
        sourcePos2[0]=sourcePos[0]
        sourcePos2[1]=sourcePos[1]
        sourcePos=sourcePos2

        sourcePosGridx=0
        for b in range(0,len(boundx)):
            if sourcePosGridx == 0:
                if sourcePos[0]<boundx[b]:
                    sourcePosGridx=b
        sourcePosGridy=0
        for b in range(0,len(boundy)):
            if sourcePosGridy == 0:
                if sourcePos[1]>boundy[b]:
                    sourcePosGridy=b

        sourcePosGrid=[sourcePosGridx,sourcePosGridy]
        sourcePosGrid2=(gridx*(sourcePosGridy-1))+sourcePosGridx

        sourceErrGrid=[0,0]
        if encPosGrid!=[0,0]:
            sourceErrGrid = np.subtract(encPosGrid,sourcePosGrid)
        else:
            sourceErrGrid=99

        # no responses
        if sourceRT == 0:
            sourcePos = 0
            sourceErr = 0
            sourcePosGrid2=0
            sourcePosGrid=0
            sourceErrGrid=99
        elif trial[posColumn]!="":
            sourceErr = sourcePos-locs[0,(int(trial[posColumn])-1)]
            sourceErr2=[0,0]
            sourceErr2[0]=sourceErr[0]
            sourceErr2[1]=sourceErr[1]
            sourceErr=sourceErr2
        else:
            sourceErr = 0
    else:
        sourceRT = 0
        sourcePos = 0
        sourceErr = 0
        startpos = 0
        sourcePosGrid2=0
        sourcePosGrid=0
        sourceErrGrid=99
    key = event.getKeys()

    print("sourceError: {}, sourceRT: {}".format( sourceErrGrid, sourceRT ))

    if i>=practrials: # only save the experimental trials
        writer.writerow([
            ppn,
            gender,
            age,
            trial[wordsColumn],
            session,
            trial[classColumn],
            vasRating,
            vasRT,
            acc,
            sourceRT,
            sourcePos,
            sourceErr,
            startpos,
            curstim,
            trial[posColumn],
            sourcePosGrid2,
            encPosGrid,
            sourcePosGrid,
            sourceErrGrid,
            fixationTime,
            vashist
            ])
        writerCSV.writerow([
            ppn,
            gender,
            age,
            trial[wordsColumn],
            session,
            trial[classColumn],
            vasRating,
            vasRT,
            acc,
            sourceRT,
            sourcePos,
            sourceErr,
            startpos,
            curstim,
            trial[posColumn],
            sourcePosGrid2,
            encPosGrid,
            sourcePosGrid,
            sourceErrGrid,
            fixationTime,
            vashist
            ])

    if key==[]:
        key.append("none")
    elif key[0]=='escape':
        break
    i = i+1
datafile.close()
datafileCSV.close()

bb.sendMarker(val=93)
core.wait(0.001)
bb.sendMarker(val=0)

# show goodbye screen
my.showText(win, "Einde van de herinner fase.\nAlleen nog de laatste rustmeting")
core.wait(3.000)

## REST EEG
my.restEEG(win,bb, block_dur=59.5, number_blocks=4,marker_open=6,marker_closed=7)

# show goodbye screen
my.showText(win, "Einde van het experiment \n\nBedankt voor het meedoen!")
core.wait(5.000)

## Closing Section
win.close()
core.quit()
