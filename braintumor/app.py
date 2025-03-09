from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
import os
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__, template_folder='templates')

# upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# load model
try:
    model = tf.keras.models.load_model('braintumor.h5')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

image_size = 224
class_names = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary Tumor']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    try:
        img = cv2.imread(image_path)
        img = cv2.resize(img,(image_size,image_size))
        img_array = np.array(img)
        img_array = img_array.reshape(1,image_size,image_size,3)
        return img_array
    except Exception as e:
        print(f"Error in preprocessing: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            processed_image = preprocess_image(filepath)
            
            if processed_image is None:
                return jsonify({'error': 'Error processing image'}), 500
            
            prediction = model.predict(processed_image)
            
            # debug
            print("Raw prediction output:", prediction)
            print("Shape of prediction:", prediction.shape)
            
            predicted_class = np.argmax(prediction[0])
            
            print("Predicted class index:", predicted_class)
            print("Prediction probabilities:", prediction[0])
            
            confidence = float(prediction[0][predicted_class]) * 100
            result = class_names[predicted_class]

            prediction_result = {
                'prediction': result,
                'confidence': round(confidence, 2),
                'probabilities': {
                    class_names[i]: float(prediction[0][i]) * 100 
                    for i in range(len(class_names))
                }
            }

            return jsonify(prediction_result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
