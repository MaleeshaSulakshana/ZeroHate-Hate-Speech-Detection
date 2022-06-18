# pip install ktrain

import pandas as pd
import ktrain
from ktrain import text

# from google.colab import drive
# drive.mount('/content/drive')

# Read csv data
data_train = pd.read_csv('dataset/data_train.csv', encoding='latin-1')
data_test = pd.read_csv('dataset/data_test.csv', encoding='latin-1')

X_train = data_train.Input.tolist()
X_test = data_test.Input.tolist()

y_train = data_train.Label.tolist()
y_test = data_test.Label.tolist()

data = data_train.append(data_test, ignore_index=True)


class_names = ['yes', 'no']

print('size of training set: %s' % (len(data_train['Input'])))
print('size of validation set: %s' % (len(data_test['Input'])))
print(data.Label.value_counts())

data.head(10)

encoding = {
    'yes': 0,
    'no': 1,
}


# Integer values for each class
y_train = [encoding[x] for x in y_train]
y_test = [encoding[x] for x in y_test]

(x_train, y_train), (x_test, y_test), preproc = text.texts_from_array(x_train=X_train, y_train=y_train,
                                                                      x_test=X_test, y_test=y_test,
                                                                      class_names=class_names,
                                                                      preprocess_mode='bert',
                                                                      maxlen=350,
                                                                      max_features=35000)


# Model initializing
model = text.text_classifier(
    'bert', train_data=(x_train, y_train), preproc=preproc)

learner = ktrain.get_learner(model, train_data=(x_train, y_train),
                             val_data=(x_test, y_test),
                             batch_size=6)

# Train model
learner.fit_onecycle(2e-5, 1)

learner.validate(val_data=(x_test, y_test), class_names=class_names)

predictor = ktrain.get_predictor(learner.model, preproc)
predictor.get_classes()

# Save model
predictor.save('checkpoint')
