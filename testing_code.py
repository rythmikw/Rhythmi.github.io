import numpy as np
import pandas as pd
from keras.models import Model

data = pd.read_csv('a2.txt', comment='#', delimiter='\t', header=None)

data.reset_index(drop=True, inplace=True)

selected_data = data.iloc[:, 5]

data_new = np.array(selected_data)

df = pd.DataFrame(data)

df= df[5]

from scipy import signal

original_fs = 1000

target_fs = 128

resampling_ratio = target_fs / original_fs

res = signal.resample(df, int(len(df) * resampling_ratio))

res = pd.DataFrame(res)

window_size = 500  

signals = res 

# Initialize an empty list to store the segmented signals
segmented_signals = []

num_segments = len(signals) // window_size

for i in range(num_segments):
    # Calculate the start and end indices for this segment
    start_index = i * window_size
    end_index = start_index + window_size

    # Extract the segment from the signal
    segment = signals.iloc[start_index:end_index]

    if len(segment) == window_size:
        # Flatten the segment and append it to the list of segmented signals
        flattened_segment = segment.values.flatten().tolist()
        segmented_signals.append(flattened_segment)

# Create a DataFrame from the segmented signals
final_df = pd.DataFrame(segmented_signals)

WS = 128 

Wc = 8*(np.pi)  

fo = 4  

wc_low = 1  

wc_high = 50 

nyquist = 0.5 * WS

wc_low = wc_low / nyquist

wc_high = wc_high / nyquist

q, e = signal.butter(fo, Wc / (0.5 * WS), btype='low')

noise_removal = signal.filtfilt(q, e, final_df, axis=1)

b, a = signal.butter(fo, [wc_low, wc_high], btype='band')

base_line_removal = signal.filtfilt(b, a, noise_removal, axis=1)

base_line_removal = pd.DataFrame(base_line_removal)


import warnings
warnings.filterwarnings("ignore")

import pandas as pd

from scipy.fft import fft

import keras

from sklearn.preprocessing import StandardScaler

from sklearn.metrics import confusion_matrix ,accuracy_score,r2_score,f1_score,precision_score,recall_score

import numpy as np

from scipy import signal


model = keras.models.load_model('raw.h5')

print("-------------------------------------------------------------------")

print("Predicting new data")

from scipy import signal

# Preprocess the new data

X_new = base_line_removal/150

y_pred = model.predict(X_new)

y_pred_classes = np.argmax(y_pred, axis=1)

target_names = ['0', '1', '2']

# Create a Series with the predicted classes
Predication = pd.Series(y_pred_classes)

# Get the value counts
counts = Predication.value_counts()

# Find the class with the highest count
highest_count_class = counts.idxmax()

average_probability = np.mean(y_pred[:, highest_count_class])

# Print the corresponding message
if highest_count_class == int(target_names[0]):
    print(f"Arrhythmia Detected with probability of {100*average_probability:.2f}")
elif highest_count_class == int(target_names[1]):
    print(f"Congestive Heart Failure Detected with probability of {100*average_probability:.2f}")
elif highest_count_class == int(target_names[2]):
    print(f"Normal Beat Detected with probability of {100*average_probability:.2f}")
else:
    print("No Prediction")