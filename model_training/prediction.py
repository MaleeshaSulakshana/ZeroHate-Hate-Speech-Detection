import ktrain
# from ktrain import text
import time

predictor = ktrain.load_predictor('checkpoint')

print(f"{predictor.get_classes()}")

message = 'ubata pissud ballo'

start_time = time.time()
prediction = predictor.predict(message)

print('predicted: {} ({:.2f})'.format(prediction, (time.time() - start_time)))
