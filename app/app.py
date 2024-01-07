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

app_directory = "app"
static_directory = "static"
images_directory = "images"

project_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(project_directory, "raw.h5")
output_file_path = os.path.join(project_directory, static_directory, "output.pdf")
logo = os.path.join(images_directory, "resulttemp.png")

app = Flask(__name__)
CORS(app,origins=['https://rhythmi.org'])  # Enable CORS for all routes

def add_section(pdf, title, content):
    pdf.set_font("Times", "B", size=15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(10)
    pdf.cell(200, 10, txt=title, align='L')
    pdf.ln(10)
    pdf.set_font("Times", size=12)
    pdf.set_xy(15, pdf.get_y())
    pdf.multi_cell(0, 10, txt=content, align='L')
    pdf.ln(3)

def add_contact_info(pdf):
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.set_font("Times", "B", size=15)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(10)
    pdf.cell(200, 10, txt="Contacts:", align='L')
    pdf.set_x(38)
    pdf.cell(200, 10, txt="Email: rhythmi.info@gmail.com ", align='L')
    pdf.set_x(115)
    pdf.cell(200, 10, txt="Instagram: rhythmi.co ", align='L')

def add_result_section(pdf, result_label, disease, disease_notify):
    pdf.set_xy(10, 145)
    pdf.set_font("Times", "B", size=15)
    pdf.set_xy(10, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=result_label, align='L')
    pdf.set_x(28)
    pdf.set_text_color(255,165,0)
    pdf.cell(200, 10, txt=f"{disease}", align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(55)
    pdf.cell(200, 10, txt=f" {disease_notify}", align='L')
    pdf.ln(10)

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
            message = "Heart Failure Detected"

        elif highest_count_class == int(target_names[2]):
            fig, axs = plt.subplots(3, 1, figsize=(12, 6))
            axs[0].plot(base_line_removal.iloc[0] / 200)
            axs[1].plot(base_line_removal.iloc[1] / 200)
            axs[2].plot(base_line_removal.iloc[2] / 200)
            message = "Normal Beat Detected"

        else:
            message = "No Prediction"

        pdf = FPDF(unit="mm", format=[297.01,420.03])
        # Add a page
        pdf.add_page()

        # Save the BytesIO object as a PNG file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name,format='png')

        # Use correct variable name here
        pdf.image(logo,x=0, y=0, w = 297.01 , h = 420.03)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        plt.savefig(temp_file.name, format='png')
        pdf.image(temp_file.name, x=-20, y=58, w=250, h=90, type='png', link='')


        if message == "Normal Beat Detected":

            pdf.set_xy(10, 145)
            pdf.set_font("Times", "B", size=15)
            pdf.set_xy(10, pdf.get_y())
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt="Result:", align='L')
            pdf.set_x(28)
            pdf.set_text_color(26, 148, 49)
            pdf.cell(200, 10, txt="Normal", align='L')
            pdf.set_x(47)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt="Beat", align='L')
            pdf.set_text_color(0, 0, 0)
            pdf.set_x(59)
            pdf.cell(200, 10, txt="Detected", align='L')
            pdf.ln(10)

            explanation_nrml = 'A normal ECG indicates that the heart is functioning properly. The heart rate should range from 60 to 80 beats per minute, but it may be lower in physically fit individuals.'

            recommendation_nrml = "Maintain a healthy lifestyle, which includes regular exercise and a balanced diet. Regular check-ups with your healthcare provider are also important to monitor your heart health. The heart rate should be between 50 and 100 beats per minute, with the P-wave preceding every QRS complex, and the PR interval being constant. Any significant deviations from these norms should be discussed with a healthcare provider."

            add_section(pdf, "Explanation:", explanation_nrml)
            add_section(pdf, "Recommendation:", recommendation_nrml)
            add_contact_info(pdf)

        if message == "Arrhythmia Detected":

            arrhythmia = message.split()[0]


            arr_detected = message.split()[1]

            add_result_section(pdf, "Result:", arrhythmia, arr_detected)
            
            explanation_arr = "Arrhythmias are disturbances in the normal cardiac rhythm of the heart, which occur as a result of alterations within the conduction of electrical impulses. They can be caused by various factors, including heart disease, stress, certain medications, and caffeine or nicotine use."

            recommendation_arr = "The treatment for arrhythmias depends on the type and severity of the arrhythmia. This could include medication, lifestyle changes such as reducing stress and limiting caffeine or nicotine use, or in some cases, medical procedures or surgery. Regular monitoring of the heart's electrical activity is crucial for managing arrhythmias. It's also important to identify and manage any underlying conditions that may be causing the arrhythmia, such as heart disease."

            add_section(pdf, "Explanation:", explanation_arr)
            add_section(pdf, "Recommendation:", recommendation_arr)
            add_contact_info(pdf)

        if message == "Heart Failure Detected":

            chf = message.split()[0] + message.split()[1]
            chf_detected = message.split()[2]

            # add_result_section(pdf, "Result:", chf, chf_detected)
            pdf.set_xy(10, 145)
            pdf.set_font("Times", "B", size=15)
            pdf.set_xy(10, pdf.get_y())
            pdf.set_text_color(0, 0, 0)
            pdf.cell(200, 10, txt="Result:", align='L')
            pdf.set_x(28)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(200, 10, txt="Heart", align='L')
            pdf.set_x(43)
            pdf.cell(200, 10, txt="Failure", align='L')
            pdf.set_text_color(0, 0, 0)
            pdf.set_x(61)
            pdf.cell(200, 10, txt="Detected", align='L')
            pdf.ln(10)

            explanation_chf = "Heart failure is a serious condition where the heart doesn't pump blood as well as it should. It can be caused by conditions that damage the heart, such as coronary artery disease and high blood pressure."

            recommendation_chf = "Treatment for heart failure typically involves lifestyle changes, medications, and sometimes devices or surgical procedures. Lifestyle changes could include quitting smoking, limiting salt and fluid intake, and getting regular exercise. Medications could include ACE-inhibitors or angiotensin receptor blockers for patients with left ventricular ejection fraction <=40%, and cholesterol-lowering statins for people with a history of a myocardial infarction or acute coronary syndrome5. Regular follow-ups with a healthcare provider are crucial for managing this condition.".replace('\u2264', '<=')

            add_section(pdf, "Explanation:", explanation_chf)
            add_section(pdf, "Recommendation:", recommendation_chf)
            add_contact_info(pdf)

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
