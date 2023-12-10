import pandas as pd
from scipy import signal
from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

app_directory = "app"
static_directory = "static"

project_directory = os.path.dirname(os.path.abspath(__file__))
pdf_file_path = os.path.join(project_directory, "23.txt")
model_path = os.path.join(project_directory, "raw.h5")
output_file_path = os.path.join(project_directory, static_directory, "output.pdf")

def process_ecg_file(file_path):
    try:
        file_content = pd.read_csv(file_path, comment='#', delimiter='\t', header=None)
        selected_data = file_content.iloc[:, 5]
        df = pd.DataFrame(selected_data)
        df = df[5]

        original_fs = 1000
        target_fs = 128
        resampling_ratio = target_fs / original_fs
        resampled_data = signal.resample(df, int(len(df) * resampling_ratio))

        window_size = 500
        signals = pd.DataFrame(resampled_data)
        segmented_signals = []

        num_segments = len(signals) // window_size

        for i in range(num_segments):
            start_index = i * window_size
            end_index = start_index + window_size
            segment = signals.iloc[start_index:end_index]

            if len(segment) == window_size:
                flattened_segment = segment.values.flatten().tolist()
                segmented_signals.append(flattened_segment)

        final_df = pd.DataFrame(segmented_signals)

        WS = 128
        Wc = 8 * (np.pi)
        fo = 4
        wc_low = 1
        wc_high = 50
        nyquist = 0.5 * WS
        wc_low /= nyquist
        wc_high /= nyquist

        q, e = signal.butter(fo, Wc / (0.5 * WS), btype='low')
        noise_removal = signal.filtfilt(q, e, final_df, axis=1)

        b, a = signal.butter(fo, [wc_low, wc_high], btype='band')
        base_line_removal = signal.filtfilt(b, a, noise_removal, axis=1)

        base_line_removal = pd.DataFrame(base_line_removal)

        # model_path = 'raw.h5'
        model = load_model(model_path)

        X_new = base_line_removal / 200
        y_pred = model.predict(X_new)
        y_pred_classes = np.argmax(y_pred, axis=1)

        target_names = ['0', '1', '2']
        Predication = pd.Series(y_pred_classes)
        counts = Predication.value_counts()
        highest_count_class = counts.idxmax()
        average_probability = np.mean(y_pred[:, highest_count_class])

        if highest_count_class == int(target_names[0]):
            result = "Arrhythmia Detected"
        elif highest_count_class == int(target_names[1]):
            result = "Congestive Heart Failure Detected"
        elif highest_count_class == int(target_names[2]):
            result = "Normal Beat Detected"
        else:
            result = "No Prediction"
        
        # Print the corresponding message
        if highest_count_class == int(target_names[0]):
            fig, axs = plt.subplots(3, 1, figsize=(12,6))
            axs[0].plot(base_line_removal.iloc[0]/200)
            axs[1].plot(base_line_removal.iloc[1]/200)
            axs[2].plot(base_line_removal.iloc[2]/200)
            message = "Arrhythmia Detected"
            
        elif highest_count_class == int(target_names[1]):
            fig, axs = plt.subplots(3, 1, figsize=(12,6))
            axs[0].plot(base_line_removal.iloc[0]/200)
            axs[1].plot(base_line_removal.iloc[1]/200)
            axs[2].plot(base_line_removal.iloc[2]/200)
            message = "Congestive Heart Failure Detected"

        elif highest_count_class == int(target_names[2]):
            fig, axs = plt.subplots(3, 1, figsize=(12,6))
            axs[0].plot(base_line_removal.iloc[0]/200)
            axs[1].plot(base_line_removal.iloc[1]/200)
            axs[2].plot(base_line_removal.iloc[2]/200)
            message = "Normal Beat Detected"

        else:
            message = "No Prediction"

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=15)
        pdf.cell(200, 10, txt="RHYTHMI Health CO. ", ln=1, align='L')
        pdf.set_font("Times", "B", size=15)
        pdf.set_xy(10, 30)
        pdf.cell(200, 10, txt="RHYTHMI's ECG Test Result", ln=2, align='C')

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name, format='png')
        pdf.image(temp_file.name, x=-20, y=50, w=250, h=100, type='png', link='')

        if message == "Normal Beat Detected" : 
            pdf.set_font("Times","B", size = 15)
            pdf.set_text_color(0,255,0)
            pdf.set_xy(0, 150)  
            pdf.cell(200, 10, txt = message.split()[0], ln = 1, align = 'C')

            pdf.set_xy(15, 150)
            pdf.set_text_color(0, 0, 0)  # RGB values for blue color
            pdf.cell(200, 10, txt = " ".join(message.split()[1:2]), ln = 3, align = 'C')

            pdf.set_xy(31, 150)
            pdf.set_text_color(0, 0, 0)  # RGB values for blue color
            pdf.cell(200, 10, txt = message.split()[2], ln = 1, align = 'C')

        if message == "Arrhythmia Detected" : 
            pdf.set_font("Times","B", size = 15)
            pdf.set_text_color(255,0,0)
            pdf.set_xy(0, 150) 
            pdf.cell(200, 10, txt = message.split()[0], ln = 1, align = 'C')
            
            pdf.set_xy(25, 150)
            pdf.set_text_color(0, 0, 0)  # RGB values for blue color
            pdf.cell(200, 10, txt = message.split()[1], ln = 3, align = 'C')

            explanation_arr = 'Explanation: Arrhythmias are disturbances in the normal cardiac rhythm of the heart, which occur as a result of alterations within the conduction of electrical impulses. They can be caused by various factors, including heart disease, stress, certain medications, and caffeine or nicotine use.'

            recommendation_arr = "Recommendation: The treatment for arrhythmias depends on the type and severity of the arrhythmia. This could include medication, lifestyle changes such as reducing stress and limiting caffeine or nicotine use, or in some cases, medical procedures or surgery. Regular monitoring of the heart's electrical activity is crucial for managing arrhythmias. It's also important to identify and manage any underlying conditions that may be causing the arrhythmia, such as heart disease."

            pdf.set_font("Times", size=12)
            
            pdf.multi_cell(0, 10, txt=explanation_arr, align='L')
            pdf.ln(5)
            pdf.multi_cell(0, 10, txt=recommendation_arr, align='L')

        if message == "Congestive Heart Failure Detected" : 
            pdf.set_font("Times","B", size = 15)
            pdf.set_text_color(255,0,0)
            pdf.set_xy(0, 150)  
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt = message.split()[0], ln = 1, align = 'C')
            # Change 160 to adjust the vertical position of the message

            pdf.set_xy(33, 150)
            pdf.set_text_color(255, 0, 0)  # RGB values for blue color
            pdf.cell(200, 10, txt = " ".join(message.split()[1:3]), ln = 3, align = 'C')
            
            pdf.set_xy(65, 150)
            pdf.set_text_color(0, 0, 0)  # RGB values for blue color
            pdf.cell(200, 10, txt = message.split()[3], ln = 3, align = 'C')

        # output_file_path = 'output.pdf'
        pdf.output(output_file_path)

        temp_file.close()

        return {'result': result, 'output_file': output_file_path}

    except Exception as e:
        return {'error': str(e)}

# Example usage
output = process_ecg_file(pdf_file_path)
print(output)
