import ktrain
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# For getting prediction
def get_prediction(message):
    predictor = ktrain.load_predictor(APP_ROOT + '/checkpoint')
    prediction = predictor.predict(message)

    return prediction
