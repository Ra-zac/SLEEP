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

# Concatenate data from all subjects and all sessions
mycwd = os.getcwd()

path = r'/home/kanthida/SWSdata'
os.chdir(path)
all_files = glob.glob("*.csv")

os.chdir(mycwd)

# NEW SYSTEM
# Files
for i, ppsext in enumerate(all_files):
    pps = os.path.splitext(ppsext)[0] #'C23S4'
    hypnogram = '/home/kanthida/Documents/Exports NMDA_PIE/' + pps + '_Hyp.csv'
    arfile = '/home/kanthida/Documents/Exports NMDA_PIE/' + pps + '_Ar.csv'
    output = './SWSdata/' + pps +'.csv'

## Load EEG + preprocessing
#raw = mne.io.read_raw_edf('/archive/hstein/RawData/RawEEG/C22/S1/sleep/file6.EDF', preload=True)
    raw = mne.io.read_raw_edf('/home/kanthida/Documents/missing EDF/C23_S4.EDF', preload=True)
# Rereferencing and selecting EEG electrodes
    raw = raw.set_eeg_reference(ref_channels=['EEG A1','EEG A2'])
#raw = raw.set_eeg_reference(ref_channels=['A1','A2'])
# Start EEG file at same time as hypnogram
    raw = raw.pick(['EEG Fp1', 'EEG Fpz', 'EEG Fp2', 'EEG AF7', 'EEG AFz', 'EEG AF8', 'EEG F7', 'EEG F3', 'EEG Fz', 
            'EEG F4', 'EEG F8', 'EEG FT7', 'EEG FC3', 'EEG FCz', 'EEG FC4', 'EEG FT8', 'EEG A1', 'EEG T7', 
            'EEG C5', 'EEG C3', 'EEG Cz', 'EEG C4', 'EEG C6', 'EEG T8', 'EEG A2', 'EEG TP7', 'EEG CP3', 'EEG CPz', 
            'EEG CP4', 'EEG TP8', 'EEG P7', 'EEG P3', 'EEG Pz', 'EEG P4', 'EEG P8', 'EEG PO7', 'EEG PO3', 'EEG POz', 
            'EEG PO4', 'EEG PO8', 'EEG O1', 'EEG Oz', 'EEG O2'])
#raw = raw.pick(['Fp1', 'Fpz', 'Fp2', 'AF7', 'AFz', 'AF8', 'F7', 'F3', 'Fz', 'F4', 'F8', 'FT7', 'FC3', 'FCz', 'FC4', 'FT8',
#'A1', 'T7', 'C5', 'C3', 'Cz', 'C4', 'C6', 'T8', 'A2', 'TP7', 'CP3', 'CPz', 'CP4', 'TP8', 'P7', 'P3', 'Pz', 'P4', 'P8',
#'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'O1', 'Oz', 'O2'])

### CHECK THAT HYPNOGRAM AND AROUSAL FILE ARE BOTH IN UTF-8
## Create hypnogram list (in seconds)
# Load hypnogram file
    with open(hypnogram, 'r') as csvfile:
        hypfile = csv.reader(csvfile, delimiter = '\t')
        #hypfile = csv.reader(csvfile, delimiter = ',') #C21S4 E20S2 S11S4 S12S4
        #hypfile = csv.reader(csvfile, delimiter = ';') #C14S4
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
    ar = pd.read_csv(arfile, sep = '\t', header = 0)

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

    # SW detection with hypno and outlier detection
    kwargs = {"hypno": hyp_yasa, "remove_outliers":True}
    sw = yasa.sw_detect_multi(raw, **kwargs)
    print(sw.shape[0], 'slow-waves detected.')

    # Export file
    sw.to_csv(output)
