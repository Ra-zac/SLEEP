# Import packages
import yasa
import mne
import numpy as np
import pandas as pd
import os.path
import csv
import glob
import os
from mne.io.constants import FIFF

# Concatenate data from all subjects and all sessions
mycwd = os.getcwd()

path = r'/home/amoran/YASA/extra_controls/'
all_files = [ f.name+g.name+".csv" for f in os.scandir(path) if f.is_dir() for g in os.scandir(path+f.name) if g.is_dir() ] 

#path = r'/home/kanthida/SWSdata'
#os.chdir(path)
#all_files = glob.glob("*.csv")

path = r'/home/amoran/YASA/SWSdata/all'
os.chdir(path)
files_done = glob.glob("*.csv")
files_done.append('S07S1.csv')
files_done.append('E16S5.csv')
files_done.append('E29S1.csv')
files_done.append('C19S1.csv')
files_done.append('C27S1.csv')
files_done.append('C37S1.csv')
files_done.append('C43S1.csv')

all_files = [x for x in all_files if x not in files_done]

os.chdir(mycwd)

sf = 100

# Files
for i, ppsext in enumerate(all_files):
    pps = os.path.splitext(ppsext)[0] #'C23S4
    hypnogram = '/home/amoran/YASA/extra_controls/' + pps[:3] + '/' + pps[3:] + '/sleep/hypnogram.csv'
    arfile = '/home/amoran/YASA/extra_controls/' + pps[:3] + '/' + pps[3:] + '/sleep/arousal.csv'
    edffile = '/home/amoran/YASA/extra_controls/' + pps[:3] + '/' + pps[3:] + '/sleep/'
    syst = 'NEW'
    if not os.path.exists(hypnogram):
        syst = 'OLD'
        hypnogram = '/home/kanthida/Documents/' + pps.lower() + '.txt'
        edffile = '/archive/hstein/RawData/RawEEG/' + pps[:3] + '/' + pps[3:] + '/sleep/'
    else:
        if not os.path.exists(edffile):
            edffile = '/home/amoran/YASA/extra_controls/' + pps[:3] + '/' + pps[3:] + '/sleep/'
            edffile = glob.glob(edffile+'*.EDF')[0]

    if not os.path.exists(hypnogram):
        syst = None
        print('skipping session: '+pps)
        continue


    output = '/home/amoran/YASA/SWSdata/all/' + pps +'.csv'

    if syst=='NEW':
    ## Load EEG + preprocessing
    #raw = mne.io.read_raw_edf('/archive/hstein/RawData/RawEEG/C22/S1/sleep/file6.EDF', preload=True)
        edffile=glob.glob(edffile + '*.EDF')[0]
        try:
            raw = mne.io.read_raw_edf(edffile, preload=True)
        except:
            raw = mne.io.read_raw_edf(edffile, preload=True,  encoding="utf-16")
        raw.resample(sf, npad='auto')
    # Rereferencing and selecting EEG electrodes
        raw = raw.set_eeg_reference(ref_channels=[raw.ch_names[6], raw.ch_names[7]])
#        raw = raw.set_eeg_reference(ref_channels=['EEG A1','EEG A2'])
    #raw = raw.set_eeg_reference(ref_channels=['A1','A2'])
    # Start EEG file at same time as hypnogram
    #    raw = raw.pick(['EEG Fp1', 'EEG Fpz', 'EEG Fp2', 'EEG AF7', 'EEG AFz', 'EEG AF8', 'EEG F7', 'EEG F3', 'EEG Fz', 
    #            'EEG F4', 'EEG F8', 'EEG FT7', 'EEG FC3', 'EEG FCz', 'EEG FC4', 'EEG FT8', 'EEG A1', 'EEG T7', 
    #            'EEG C5', 'EEG C3', 'EEG Cz', 'EEG C4', 'EEG C6', 'EEG T8', 'EEG A2', 'EEG TP7', 'EEG CP3', 'EEG CPz', 
    #            'EEG CP4', 'EEG TP8', 'EEG P7', 'EEG P3', 'EEG Pz', 'EEG P4', 'EEG P8', 'EEG PO7', 'EEG PO3', 'EEG POz', 
    #            'EEG PO4', 'EEG PO8', 'EEG O1', 'EEG Oz', 'EEG O2'])
    #raw = raw.pick(['Fp1', 'Fpz', 'Fp2', 'AF7', 'AFz', 'AF8', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FT7', 'FC3', 'FCz', 'FC4', 'FT8',
    #'A1', 'T7', 'C5', 'C3', 'Cz', 'C4', 'C6', 'T8', 'A2', 'TP7', 'CP3', 'CPz', 'CP4', 'TP8', 'P7', 'P3', 'Pz', 'P4', 'P8',
    #'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'O1', 'Oz', 'O2'])
        raw = raw.pick(raw.ch_names[:6])

    ### CHECK THAT HYPNOGRAM AND AROUSAL FILE ARE BOTH IN UTF-8
    ## Create hypnogram list (in seconds)
    # Load hypnogram file
    
        try: 
            with open(hypnogram, 'r') as csvfile:    
                if pps in ['C23S1', 'C21S4', 'E20S2', 'S11S4', 'S12S4']:
                    hypfile = csv.reader(csvfile, delimiter = ',') #C21S4 E20S2 S11S4 S12S4
                elif pps=='C14S4':
                    hypfile = csv.reader(csvfile, delimiter = ';') #C14S4
                else:
                    hypfile = csv.reader(csvfile, delimiter = '\t')
                c = 0
                hyp = []
                for row in hypfile:
                    # Add zeros so hypnogram, arousal, and EEG data start at the same time
                    if c == 0:
                        for i in range(30 * (int(row[0])+1)):
                            hyp.append(0)
                    # Notate sleep stages
                    for j in range(30):
                        if row[1] == 'WAKE':
                            hyp.append(0)
                        elif row[1] == 'N1':
                            hyp.append(1)
                        elif row[1] == 'N2':
                            hyp.append(2)
                        elif row[1] == 'N3':
                            hyp.append(3)
                        else: # REM
                            hyp.append(4)
                    c += 1
            csvfile.close()
        except:
            with open(hypnogram, 'r',encoding="utf-16") as csvfile:    
                if pps in ['C23S1', 'C21S4', 'E20S2', 'S11S4', 'S12S4']:
                    hypfile = csv.reader(csvfile, delimiter = ',') #C21S4 E20S2 S11S4 S12S4
                elif pps=='C14S4':
                    hypfile = csv.reader(csvfile, delimiter = ';') #C14S4
                else:
                    hypfile = csv.reader(csvfile, delimiter = '\t')
                c = 0
                hyp = []
        
                for row in hypfile:
                    # Add zeros so hypnogram, arousal, and EEG data start at the same time
                    if c == 0:
                        for i in range(30 * (int(row[0])+1)):
                            hyp.append(0)
                    # Notate sleep stages
                    for j in range(30):
                        if row[1] == 'WAKE':
                            hyp.append(0)
                        elif row[1] == 'N1':
                            hyp.append(1)
                        elif row[1] == 'N2':
                            hyp.append(2)
                        elif row[1] == 'N3':
                            hyp.append(3)
                        else: # REM
                            hyp.append(4)
                    c += 1
            csvfile.close()

        ## Create arousal list (in seconds)
        # Load arousal file
        #ar = pd.read_csv(arfile, sep = ',', header = 0)
        try:
            ar = pd.read_csv(arfile, index_col = False, sep = '\t|,', header = 0)
        except:
            ar = pd.read_csv(arfile, index_col = False, sep = '\t|,', header = 0, encoding="utf-16")


        # Get columns and convert from us to s
        time = [ar['Start time relative (total µs)'].tolist(), ar['Duration (total µs)'].tolist()]
        x = len(time[0])
        time = np.reshape([round(time[i][j] / 1e6) for i in range(len(time)) for j in range(x)], (2,x))

        # No arousal = 0
        # Arousal = 1
        arousal = np.zeros(len(hyp))

        for i in range(x):
            for j in range(time[1][i]):
                arousal[time[0][i]-1+j] = 1

        ## New hypnogram: every epoch with N2/N3 AND with arousal will be set as N1
        hyp2 = np.zeros([len(hyp),1])

        for i in range(len(hyp)):
            if (hyp[i] == 2 or hyp[i] == 3) and arousal[i] == 1:
                hyp2[i] = 1
            else:
                hyp2[i] = hyp[i]
        # Upsample hypnogram to data
        hyp_yasa = yasa.hypno_upsample_to_data(hyp2, sf_hypno = 1, data = raw)

    if syst=='OLD':
        path = edffile
        files=sorted(glob.glob(path + '*.EDF'))

        for i, fl in enumerate(files):
            # Check for lower or uppercase files
            raw = mne.io.read_raw_edf(fl, preload = True, encoding= 'latin1')
            raw.resample(sf, npad='auto')
            
            # Concatenate files
            if i == 0:
                raw_con = raw.copy()
            else:
                raw_con.append(raw, preload=True)

        # Rereferencing and selecting EEG electrodes
        raw_con = raw_con.set_eeg_reference(ref_channels=['EEG A1','EEG A2'])
        # Start EEG file at same time as hypnogram
        #raw_con = raw_con.crop(tmin = 180)

        if pps[:3]=='E01':
            raw_con = raw_con.pick(['EEG F3', 'EEG F4',])
        else:
            raw_con = raw_con.pick(['EEG F3', 'EEG F4',])

        # Load hypnogram
        hypno = np.loadtxt(hypnogram, usecols = (2,4))

        # New hypnogram: every epoch with arousal will be set as N1
        hypno2 = np.append(hypno, np.zeros([len(hypno),1]), axis =1)

        for i in range(len(hypno)):
            if (hypno2[i][0] == 2 or hypno2[i][0] == 3) and hypno2[i][1] == 1:
                hypno2[i][2] = 1
            else:
                hypno2[i][2] = hypno2[i][0]

        # Upsample hypnogram to data
        hyp_yasa = yasa.hypno_upsample_to_data(hypno2[:,2], sf_hypno = 1/30, data = raw_con)

        raw = raw_con
    
       
    print('now starts detection')
    # SW detection with hypno and outlier detection
    kwargs = {"hypno": hyp_yasa, "remove_outliers":True, "include":(2,3)}
    #kwargs = {"hypno": hyp_yasa, "remove_outliers":True, "include":(2,3)}
    #sw = yasa.sw_detect_multi(raw, **kwargs)
    sp = yasa.sw_detect(raw, **kwargs) 

    print(sp.summary().shape[0], 'SWS detected.')

    # Export file
    sp.summary().to_csv(output)
