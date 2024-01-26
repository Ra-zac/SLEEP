# Import packages
import yasa
import mne
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os.path
import csv
import glob
import os
import shutil

# Concatenate data from all subjects and all sessions
mycwd = os.getcwd()

path = r'/archive/hstein/RawData/RawEEG/'
all_files = [ f.name+g.name+".csv" for f in os.scandir(path) if f.is_dir() for g in os.scandir(path+f.name) if g.is_dir() ] 

os.chdir(mycwd)

sf = 100
missing_hyp = []
missing_edf = []
found_old = []
found_new = []

# Files
for i, ppsext in enumerate(all_files):
    pps = os.path.splitext(ppsext)[0] #'C23S4
    hypnogramNEW = '/home/kanthida/Documents/Exports NMDA_PIE/' + pps + '_Hyp.csv'
    arfileNEW = '/home/kanthida/Documents/Exports NMDA_PIE/' + pps + '_Ar.csv'
    edffile = '/archive/hstein/RawData/RawEEG/' + pps[:3] + '/' + pps[3:] + '/sleep/'
    syst = 'NEW'
    if not os.path.exists(edffile):
        syst = None
        missing_edf.append(pps)
    else:
        if not os.path.exists(hypnogramNEW):
            syst = 'OLD'
            hypnogramOLD = '/home/kanthida/Documents/' + pps.lower() + '.txt'
            if not os.path.exists(hypnogramOLD):
                    syst = None
                    missing_hyp.append(pps)
    if syst == None:
        print('skipping session: '+pps + ', total missing: ' + str(len(missing_hyp)))
    elif syst == 'OLD': 
        shutil.copy2(hypnogramOLD, '/archive/hstein/RawData/RawEEG/' + pps[:3] + '/' + pps[3:] + '/sleep/hypnogram.txt')
        found_old.append(pps)
    elif syst == 'NEW':
        shutil.copy2(arfileNEW, '/archive/hstein/RawData/RawEEG/' + pps[:3] + '/' + pps[3:] + '/sleep/arousal.csv')
        shutil.copy2(hypnogramNEW, '/archive/hstein/RawData/RawEEG/' + pps[:3] + '/' + pps[3:] + '/sleep/hypnogram.csv')
        found_new.append(pps)
    
print('SUMMARY ---------')
print('OLD SYSTEM COPIED: ' + str(len(found_old)))
print('NEW SYSTEM COPIED: ' + str(len(found_new)))
print('MISSING EDFS: ' + str(len(missing_edf)))
print('MISSING HYPNOS: ' + str(len(missing_hyp)))

print(missing_hyp)

    


    