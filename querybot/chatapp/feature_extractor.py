import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input

tf.config.run_functions_eagerly(True)  
tf.keras.backend.clear_session()

model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_tensor = image.img_to_array(img)
    
    img_tensor = tf.convert_to_tensor(img_tensor, dtype=tf.float32)
    
    img_tensor = tf.expand_dims(img_tensor, axis=0)
    img_tensor = preprocess_input(img_tensor)

    @tf.function
    def run_model(input_tensor):
        return model(input_tensor)

    features = run_model(img_tensor)
    features = tf.reshape(features, [-1])

    print("Extracted Features Shape:", features.shape)  # Debugging print
    return features