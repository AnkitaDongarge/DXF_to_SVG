from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from dxf_parser import parse_dxf
from svg_converter import convert_to_svg

app = Flask(__name__)
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({"error": str(error)}), 500
# Set upload and SVG folders
UPLOAD_FOLDER = 'uploads/'
SVG_FOLDER = 'saved_svgs/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SVG_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SVG_FOLDER'] = SVG_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

parsed_data_file = 'parsed_data.json'
if os.path.exists(parsed_data_file):
    open(parsed_data_file, 'w').close()

def clear_parsed_data():
    with open(parsed_data_file, 'w') as f:
        f.write('')

def delete_old_svgs():
    for file_name in os.listdir(app.config['UPLOAD_FOLDER']):
        if file_name.endswith('.svg'):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    for file_name in os.listdir(app.config['SVG_FOLDER']):
        if file_name.endswith('.svg'):
            os.remove(os.path.join(app.config['SVG_FOLDER'], file_name))

@app.route('/')
def index():
    clear_parsed_data()
    delete_old_svgs()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.dxf'):
        clear_parsed_data()
        delete_old_svgs()

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        min_x, max_x, min_y, max_y, classified_data = parse_dxf(file_path)

        with open(parsed_data_file, 'w') as f:
            json.dump(classified_data, f)

        svg_filename = f"output_{os.path.splitext(file.filename)[0]}.svg"
        svg_output = os.path.join(app.config['UPLOAD_FOLDER'], svg_filename)

        convert_to_svg(parsed_data_file, svg_output, min_x, max_x, min_y, max_y)

        saved_svg_path = os.path.join(app.config['SVG_FOLDER'], svg_filename)
        os.rename(svg_output, saved_svg_path)

        with open(saved_svg_path, 'r') as svg_file:
            svg_content = svg_file.read()

        return jsonify({
            "svg": svg_content,
            "saved_svg_path": saved_svg_path,
            "classified_data": classified_data,
            "download_url": f"/download/{svg_filename}"
        }), 200
    else:
        return jsonify({"error": "Invalid file format. Please upload a DXF file."}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_path = os.path.join(app.config['SVG_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
