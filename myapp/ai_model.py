import os
try:
    import numpy as np
    from keras.models import load_model
    from keras.preprocessing.image import load_img, img_to_array
except ImportError:
    pass

# Get absolute path to the model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'myapp', 'models', 'plant_disease_model.h5')

# Ensure the model exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found at: {MODEL_PATH}")

# Load model
model = load_model(MODEL_PATH)

# Dynamically extract class labels
CLASS_LABELS = [
    "Apple_scab", "Apple_black_rot", "Apple_cedar_apple_rust", "Apple_healthy",
    "Background_without_leaves", "Blueberry_healthy", "Cherry_powdery_mildew", "Cherry_healthy",
    "Corn_gray_leaf_spot", "Corn_common_rust", "Corn_northern_leaf_blight", "Corn_healthy",
    "Grape_black_rot", "Grape_black_measles", "Grape_leaf_blight", "Grape_healthy",
    "Orange_haunglongbing", "Peach_bacterial_spot", "Peach_healthy",
    "Pepper_bacterial_spot", "Pepper_healthy", "Potato_early_blight", "Potato_healthy",
    "Potato_late_blight", "Raspberry_healthy", "Soybean_healthy", "Squash_powdery_mildew",
    "Strawberry_healthy", "Strawberry_leaf_scorch", "Tomato_bacterial_spot", "Tomato_early_blight",
    "Tomato_healthy", "Tomato_late_blight", "Tomato_leaf_mold", "Tomato_septoria_leaf_spot",
    "Tomato_spider_mites_two-spotted_spider_mite", "Tomato_target_spot", "Tomato_mosaic_virus",
    "Tomato_yellow_leaf_curl_virus"
]

def predict_disease(image_path):
    """
    Function to predict plant disease using the pre-trained AI model.
    Dynamically extracts class labels.
    """
    img = load_img(image_path, target_size=(160, 160))  # Resize
    img_array = img_to_array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction, axis=1)[0]
    
    disease_name = CLASS_LABELS[predicted_class] if predicted_class < len(CLASS_LABELS) else "Unknown Disease"

    return {
        "Plant Type": disease_name.split()[0] if " " in disease_name else "Unknown",
        "Disease Detected": disease_name,
        "Confidence Level": f"{max(prediction[0]) * 100:.2f}%",
        "Plant Health Bar": int((1 - max(prediction[0])) * 100)  # Lower confidence means worse health
    }
