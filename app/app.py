from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from keras.models import Model
from scipy import signal
import warnings
warnings.filterwarnings("ignore")
import keras
from io import StringIO
import requests
import configparser
import os
from keras.models import load_model

app = Flask(__name__)

CORS(app)  # This will enable CORS for all routes

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Read the file into a StringIO object
        file_content = StringIO(file.read().decode('utf-8'))

        # Your new code starts here
        data = pd.read_csv(file_content, comment='#', delimiter='\t', header=None)
        
        data.reset_index(drop=True, inplace=True)

        selected_data = data.iloc[:, 5]

        df = pd.DataFrame(selected_data)

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

        app_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the model file
        model_path = os.path.join(app_dir, 'raw.h5')

        # Load the model
        model = load_model(model_path)
    
        #model = keras.models.load_model('D:\application\Rhythmi.github.io-main\app\raw.h5')

        from scipy import signal

        # Preprocess the new data

        X_new = base_line_removal/200

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
            result = f"Arrhythmia Detected with probability of {100*average_probability:.2f}"
        elif highest_count_class == int(target_names[1]):
            result = f"Congestive Heart Failure Detected with probability of {100*average_probability:.2f}"
        elif highest_count_class == int(target_names[2]):
            result = f"Normal Beat Detected with probability of {100*average_probability:.2f}"
        else:
            result = "No Prediction"
        return jsonify(result)

if __name__ == '__main__':
    app.config['DEBUG'] = True
