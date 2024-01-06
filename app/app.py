from flask import Flask, render_template, request, jsonify, send_file
from scipy import signal
from flask_cors import CORS
from keras.models import load_model
from datetime import datetime
import pytz
import numpy as np
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt
import biosppy.signals.ecg as ecg
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app_directory = "app"
static_directory = "static"
images_directory = "images"

project_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(project_directory, "raw.h5")
output_file_path = os.path.join(project_directory, static_directory, "output.pdf")


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

        ecg_signal= base_line_removal/200

        def HR(ecg_signal):
            R_peaks = []
            heart_rates = []
            times_list = []

            str_heart_rates = str(heart_rates)[1:-1]

            # 'ecg_signal' is your DataFrame
            for index, row in ecg_signal.iterrows():
                rpeaks = ecg.engzee_segmenter(signal=row, sampling_rate=128)[0]
                R_peaks.append(rpeaks)
            for Rpeaks in R_peaks:
                times = Rpeaks / 128
                times_list.append(times)
                # Calculate the differences between successive times
                RR_intervals = np.diff(times)
                # Calculate the mean of the RR intervals
                mean_RR_interval = np.mean(RR_intervals)
                # Calculate the heart rate from mean RR interval
                # mean_RR_interval should be in seconds
                heart_rate = int(60 / mean_RR_interval)

                heart_rates.append(heart_rate)

            Max_HR = int(np.mean(heart_rates))
            str_heart_rates = str(Max_HR)
            return str_heart_rates, times_list

        model = load_model(model_path)

        X_new = base_line_removal / 200
        y_pred = model.predict(X_new)
        y_pred_classes = np.argmax(y_pred, axis=1)

        target_names = ['0', '1', '2']
        Predication = pd.Series(y_pred_classes)
        counts = Predication.value_counts()
        highest_count_class = counts.idxmax()
    
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

        # Convert plot to PNG image bytes
        buf = io.BytesIO()
        canvas = FigureCanvas(fig)
        canvas.print_png(buf)

        # Create a new PDF with FPDF
        pdf = FPDF(unit="mm", format=[297.01,420.03])
        # Add a page
        pdf.add_page()

        # Save the BytesIO object as a PNG file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name,format='png')

        # Use correct variable name here
        pdf.image("D:\\application\\Rhythmi.github.io-main\\images\\result_temp.png",x=0, y=0, w = 297.01 , h = 420.03)

        kuwait_timezone = pytz.timezone("Asia/Kuwait")

        kuwait_time = datetime.now(kuwait_timezone)

        today_date_kuwait = kuwait_time.strftime('%Y-%m-%d')

        current_time_kuwait = kuwait_time.strftime('%I:%M:%S %p')


        pdf.set_font("Arial","B", size=15)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(97.5,22)
        pdf.cell(200, 10, txt="Date:", align='L')

        pdf.set_font("Arial","B", size=15)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(113,22)
        pdf.cell(200, 10, txt=today_date_kuwait, align='L')
        pdf.ln(10)

        pdf.set_font("Arial","B", size=15)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(97.5,30)
        pdf.cell(200, 10, txt="Time:", align='L')

        pdf.set_font("Arial","B", size=15)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(113,30)
        pdf.cell(200, 10, txt=current_time_kuwait, align='L')
        pdf.ln(10)

        # add the plot
        pdf.image(temp_file.name,x = 20, y = 92, w= 251 , h = 100, type = 'png', link = '')


        if message == "Normal Beat Detected" : 

            heart_rate = HR(ecg_signal)

            pdf.set_font("Arial","B", size = 22)

            pdf.set_xy(50, 207)  
            pdf.set_text_color(26, 148, 49)
            pdf.cell(9, 11, txt="Normal", align='L')

            pdf.set_xy(79,207)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(9, 11, txt="Beat", align='L')

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(98, 207)
            pdf.cell(9, 11, txt="Detected", align='L')

            pdf.set_text_color(167, 14, 14)
            pdf.set_xy(245,207)
            pdf.cell(100, 11, txt= heart_rate[0], align='L')
            pdf.ln(10)

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(256,207)
            pdf.cell(100, 11, txt= "bpm", align='L')


            pdf.set_font("Arial","B", size = 15)
            pdf.set_text_color(0, 0, 0)

            pdf.set_xy(20, 236)

            exp_norm = 'A normal ECG indicates that the heart is functioning properly. The heart rate should typically range from 60 to 100 beats per minute, but it may be lower in physically fit individuals.'
            pdf.multi_cell(0, 10, txt=exp_norm)


            pdf.set_xy(20, 300)
            rec_norm = "Maintain a healthy lifestyle, which includes regular exercise and a balanced diet. Regular check-ups with your healthcare provider are also important to monitor your heart health. The heart rate should be between 60 and 100 beats per minute."
            pdf.multi_cell(0, 10, txt=rec_norm)

        if message == "Arrhythmia Detected":

            heart_rate = HR(ecg_signal)

            pdf.set_font("Arial","B", size = 22)

            pdf.set_xy(50, 207)  
            pdf.set_text_color(255, 165, 0)
            pdf.cell(9, 11, txt="Arrhythmia", align='L')

            pdf.set_xy(94,207)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(9, 11, txt="Detected", align='L')

            pdf.set_text_color(167, 14, 14)
            pdf.set_xy(245,207)
            pdf.cell(100, 11, txt= heart_rate[0], align='L')
            pdf.ln(10)

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(256,207)
            pdf.cell(100, 11, txt= "bpm", align='L')
                
            
            r1="The treatment for arrhythmias depends on the type and severity of the arrhythmia. it can be medication, lifestyle changes such"
            r2="as reducing stress and limiting caffeine or nicotine use, or in some cases, medical procedures or surgery. Regular monitoring of" 
            r3="The heart's electrical activity is crucial for managing arrhythmias as well as any underlying conditions such as heart disease."
            
            rrr= r1 + "" + r2 + "" + r3 + ""

            pdf.set_font("Arial","B", size = 15)
            pdf.set_text_color(0, 0, 0)

            pdf.set_xy(20, 235)

            exp_arr= 'Arrhythmias are disturbances in the normal cardiac rhythm of the heart, which occur as a result of'
            

            pdf.set_xy(20, 247)

            exp_arr2 = "alterations within the conduction of electrical impulses. They can be They can be caused by various"
            

            pdf.set_xy(20, 260)

            exp_arr3 = "factors, including heart disease, stress, certain medications, and caffeine or nicotine use."
            
        
            eee = exp_arr + "" + exp_arr2 + "" + exp_arr3 + ""

            pdf.set_font("Arial","B", size = 15)
            pdf.set_text_color(0, 0, 0)

            pdf.set_xy(20, 235)
            pdf.multi_cell(0, 10, txt = eee)


            pdf.set_font("Arial","B", size = 15)
            pdf.set_text_color(0, 0, 0)

            pdf.set_xy(18, 300)
            pdf.multi_cell(0, 9, txt = rrr)
            
        if message == "Congestive Heart Failure Detected":

            heart_rate = HR(ecg_signal)

            pdf.set_font("Arial","B", size = 22)

            pdf.set_xy(50, 207)  
            pdf.set_text_color(255, 0, 0)
            pdf.cell(9, 11, txt="Heart", align='L')
            pdf.set_xy(72,207)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(9, 11, txt="Failure", align='L')

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(100, 207)
            pdf.cell(9, 11, txt="Detected", align='L')
            
            pdf.set_text_color(167, 14, 14)
            pdf.set_xy(245,207)
            pdf.cell(100, 11, txt= heart_rate[0], align='L')
            pdf.ln(10)

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(259,207)
            pdf.cell(100, 11, txt= "bpm", align='L')

            pdf.set_font("Arial","B", size = 15)
            pdf.set_text_color(0, 0, 0)

            pdf.set_xy(20, 236)
            explanation_chf = "Heart failure is a serious condition where the heart doesn't pump blood as well as it should. It can be caused by conditions that damage the heart, such as coronary artery disease and high blood pressure."

            pdf.multi_cell(0, 10, txt=explanation_chf)

            pdf.set_xy(20, 300)
            recommendation_chf = "Treatment for heart failure typically involves lifestyle changes, medications, and sometimes devices or surgical procedures. Lifestyle changes could include quitting smoking, limiting salt and fluid intake, and getting regular exercise. Medications could include ACE-inhibitors or angiotensin receptor blockers for patients with left ventricular ejection fraction <=40%, and cholesterol-lowering statins for people with a history of a myocardial infarction or acute coronary syndrome5. Regular follow-ups with a healthcare provider are crucial for managing this condition.".replace('\u2264', '<=')

            pdf.multi_cell(0, 10, txt=recommendation_chf)

        pdf.output(output_file_path)

        temp_file.close()

        os.unlink(temp_file.name)

        return {'result': result, 'output_file': output_file_path}

    except Exception as e:
        return {'error': str(e)}

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        if file:
            file_path = os.path.join(project_directory, file.filename)
            file.save(file_path)
            result = process_ecg_file(file_path)
            return jsonify(result)
        else:
            return jsonify({'error': 'No file uploaded'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download/<filename>')
def download(filename):
    return send_file(output_file_path, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)