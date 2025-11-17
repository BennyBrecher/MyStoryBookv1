from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import mvp_compatible

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'pictures/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle face image upload"""
    try:
        if 'face_image' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['face_image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully!',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate_story', methods=['POST'])
def generate_story():
    try:
        face_file = request.files.get('face_image')
        story_type = request.form.get('story')
        child_name = request.form.get('child_name', 'Hero')
        gender = request.form.get('gender', 'boy')
        
        if not face_file:
            return jsonify({'error': 'No face image uploaded'}), 400
        
        if not story_type:
            return jsonify({'error': 'No story type selected'}), 400
        
        face_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(face_file.filename))
        face_file.save(face_path)
        
        print(f"Generating: {story_type} for {child_name} ({gender})")
        
        # Generate the book
        pdf_path = mvp_compatible.generate_storybook(
            face_path=face_path,
            story_type=story_type,
            child_name=child_name,
            gender=gender
        )
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(
                pdf_path, 
                as_attachment=True,
                download_name=f"{child_name}_{story_type}_storybook.pdf"
            )
        else:
            return jsonify({'error': 'PDF generation failed'}), 500
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)