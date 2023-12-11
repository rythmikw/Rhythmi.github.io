from flask import Flask, render_template, request, jsonify, send_file
from scipy import signal
from flask_cors import CORS
from keras.models import load_model
from datetime import datetime
import numpy as np
import pandas as pd
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt

app_directory = "app"
static_directory = "static"
images_directory = "images"

project_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(project_directory, "raw.h5")
output_file_path = os.path.join(project_directory, static_directory, "output.pdf")
logo = os.path.join(os.path.dirname(project_directory), images_directory, "rhythmilogo.png")

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

        if highest_count_class == int(target_names[0]):
            fig, axs = plt.subplots(3, 1, figsize=(12, 6))
            axs[0].plot(base_line_removal.iloc[0] / 200)
            axs[1].plot(base_line_removal.iloc[1] / 200)
            axs[2].plot(base_line_removal.iloc[2] / 200)
            message = "Arrhythmia Detected"

        elif highest_count_class == int(target_names[1]):
            fig, axs = plt.subplots(3, 1, figsize=(12, 6))
            axs[0].plot(base_line_removal.iloc[0] / 200)
            axs[1].plot(base_line_removal.iloc[1] / 200)
            axs[2].plot(base_line_removal.iloc[2] / 200)
            message = "Congestive Heart Failure Detected"

        elif highest_count_class == int(target_names[2]):
            fig, axs = plt.subplots(3, 1, figsize=(12, 6))
            axs[0].plot(base_line_removal.iloc[0] / 200)
            axs[1].plot(base_line_removal.iloc[1] / 200)
            axs[2].plot(base_line_removal.iloc[2] / 200)
            message = "Normal Beat Detected"

        else:
            message = "No Prediction"

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=15)
        # Header section
        pdf.image(logo, x=10, y=10, w=0, h=30)
        image_width = 30
        line_start_x = 12 + image_width + 20
        line_y_start = 10
        # pdf.line(line_start_x, 10, line_start_x, 40)
        pdf.line(line_start_x, line_y_start, line_start_x, line_y_start + 30)
        text_line_y = 12
        today_date = datetime.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        pdf.text(line_start_x + 2, text_line_y, "Rhythmi.co")
        pdf.text(line_start_x + 2, text_line_y + 10, f"Date: {today_date}")
        pdf.text(line_start_x + 2, text_line_y + 20, f"Time: {current_time}")
        # End of header section
        pdf.set_font("Times", "B", size=15)
        pdf.set_xy(10, 45)
        pdf.cell(200, 10, txt="RHYTHMI's ECG Test", ln=2, align='C')

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name, format='png')
        pdf.image(temp_file.name, x=-20, y=60, w=250, h=100, type='png', link='')

        if message == "Normal Beat Detected":
            pdf.set_font("Times", "B", size=15)
            pdf.set_text_color(0, 255, 0)
            pdf.set_xy(0, 150)
            pdf.cell(200, 10, txt=message.split()[0], ln=1, align='C')

            pdf.set_xy(15, 150)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=" ".join(message.split()[1:2]), ln=3, align='C')

            pdf.set_xy(31, 150)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=message.split()[2], ln=1, align='C')

            explanation_nrml = 'Explanation: A normal ECG indicates that the heart is functioning properly. The heart rate should range from 60 to 80 beats per minute, but it may be lower in physically fit individuals.'

            recommendation_nrml = "Recommendation: Maintain a healthy lifestyle, which includes regular exercise and a balanced diet. Regular check-ups with your healthcare provider are also important to monitor your heart health. The heart rate should be between 50 and 100 beats per minute, with the P-wave preceding every QRS complex, and the PR interval being constant. Any significant deviations from these norms should be discussed with a healthcare provider."

            pdf.set_font("Times", size=12)

            pdf.multi_cell(0, 10, txt=explanation_nrml, align='L')
            pdf.ln(5)
            pdf.multi_cell(0, 10, txt=recommendation_nrml, align='L')

        if message == "Arrhythmia Detected":
            pdf.set_font("Times", "B", size=15)
            pdf.set_text_color(255, 0, 0)
            pdf.set_xy(0, 150)
            pdf.cell(200, 10, txt=message.split()[0], ln=1, align='C')

            pdf.set_xy(25, 150)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=message.split()[1], ln=3, align='C')

            explanation_arr = 'Explanation: Arrhythmias are disturbances in the normal cardiac rhythm of the heart, which occur as a result of alterations within the conduction of electrical impulses. They can be caused by various factors, including heart disease, stress, certain medications, and caffeine or nicotine use.'

            recommendation_arr = "Recommendation: The treatment for arrhythmias depends on the type and severity of the arrhythmia. This could include medication, lifestyle changes such as reducing stress and limiting caffeine or nicotine use, or in some cases, medical procedures or surgery. Regular monitoring of the heart's electrical activity is crucial for managing arrhythmias. It's also important to identify and manage any underlying conditions that may be causing the arrhythmia, such as heart disease."

            pdf.set_font("Times", size=12)

            pdf.multi_cell(0, 10, txt=explanation_arr, align='L')
            pdf.ln(5)
            pdf.multi_cell(0, 10, txt=recommendation_arr, align='L')

        if message == "Congestive Heart Failure Detected":
            pdf.set_font("Times", "B", size=15)
            pdf.set_text_color(255, 0, 0)
            pdf.set_xy(0, 150)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=message.split()[0], ln=1, align='C')
            pdf.set_xy(33, 150)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(200, 10, txt=" ".join(message.split()[1:3]), ln=3, align='C')
            pdf.set_xy(65, 150)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt=message.split()[3], ln=3, align='C')

            explanation_chf = 'Explanation: Heart failure is a serious condition where the heart doesn’t pump blood as well as it should. It can be caused by conditions that damage the heart, such as coronary artery disease and high blood pressure.'

            recommendation_chf = "Recommendation: Treatment for heart failure typically involves lifestyle changes, medications, and sometimes devices or surgical procedures. Lifestyle changes could include quitting smoking, limiting salt and fluid intake, and getting regular exercise. Medications could include ACE-inhibitors or angiotensin receptor blockers for patients with left ventricular ejection fraction (LVEF) ≤40%, and cholesterol-lowering statins for people with a history of a myocardial infarction or acute coronary syndrome5. Regular follow-ups with a healthcare provider are crucial for managing this condition. It’s also important to fully vaccinate against respiratory illnesses including COVID-19."

            pdf.set_font("Times", size=12)

            pdf.multi_cell(0, 10, txt=explanation_chf, align='L')
            pdf.ln(5)
            pdf.multi_cell(0, 10, txt=recommendation_chf, align='L')

        pdf.output(output_file_path)

        temp_file.close()

        os.unlink(temp_file.name)

        return {'result': result, 'output_file': output_file_path}

    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

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
