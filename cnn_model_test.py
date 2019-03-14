import keras
from keras import backend as K
from keras.models import load_model
from keras.models import model_from_json

from mnist import MNIST
from sklearn.model_selection import train_test_split
import numpy as np
import cv2

import argparse
import os.path

args = None
def load_model():
    # Load trained model
    if args.verbose:
        print("Loading cnn model from disk.............", end="")

    # Load JSON model
    if args.old:
        json_file = open('cnn_model-0.json', 'r')
    else:
        json_file = open('cnn_model.json', 'r')
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)

    # Load model weights
    if args.old:
        model.load_weights("cnn_model_weights-0.h5")
    else:
        model.load_weights("cnn_model_weights.h5")
    if args.verbose:
        print("...finished.")
    return model

def test_model(model):
    # Setting variables
    if args.verbose:
        print("Setting constants.......................", end="")
    batch_size = 128
    num_classes = 26 + 26 + 10  # 26 lower, 26 upper, 10 digits
    epochs = 10
    img_rows, img_cols = 28, 28 # image dimensions (28 x 28 pixels)
    if args.verbose:
        print("...finished.")

    # Load EMNIST-byclass data
    if args.verbose:
        print("Loading EMNIST byclass-training data....", end="")
    emnist = MNIST(path='data', return_type='numpy')
    emnist.select_emnist('byclass')
    X, y =  emnist.load_training()
    if args.verbose:
        print("...finished.")

    # Split test data into training data and evaluation data
    if args.verbose:
        print("Split data: training and test(eval).....", end="")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20, random_state=111)
    if args.verbose:
        print("...finished.")
    #print("\tTraining Shape:", y_train.shape)
    #print("\tTesting Shape:", y_test.shape)

    # Restructuring data (batch, steps, channels)
    if args.verbose:
        print("Restructuring data...", end="")
    input_shape = None
    if K.image_data_format() == 'channels_first':
        X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
        X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
        if args.verbose:
            print("...Channels first...", end="")
    else:
        X_train = X_train.reshape(X_train.shape[0], img_rows, img_cols, 1)
        X_test = X_test.reshape(X_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
        if args.verbose:
            print("...Channels last...", end="")

    # Change pixel information type
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')

    # Remap [0,255] image values to [0,1]
    X_train /= 255
    X_test /= 255

    # Convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    if args.verbose:
        print("...finished.")

    # Compile model
    if args.verbose:
        print("Compiling model.........................", end="")
    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer=keras.optimizers.Adadelta(),
                  metrics=['accuracy'])
    if args.verbose:
        print("...finished.")

    # Evaluate the model using Accuracy and Loss
    # score : ['loss', 'output_1_loss', 'output_2_loss',
    # 'output_1_mean_absolute_error', 'output_2_mean_absolute_error']
    if args.verbose:
        print("Evaluating model........................", end="")
    score = model.evaluate(X_test, y_test, verbose=0)
    if args.verbose:
        print("...finished.")
    print('\tTest loss:', score[0])
    print('\tTest accuracy:', score[1])

def predict_model(model, filename):
    print(filename)
    image = cv2.imread(filename, 0)
    new_image = cv2.resize(image, (28, 28))
    prediction = model.predict(new_image.reshape(1,28,28,1))[0]
    prediction = np.argmax(prediction)
    return prediction

def plot_model():
    # Load training history
    if args.verbose:
        print("Loading model history from disk.........", end="")
    f = open('cnn_model_history.pckl', 'rb')
    history = pickle.load(f)
    f.close()
    if args.verbose:
        print("...finished.")

    # Summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

    # Summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()

# https://stackoverflow.com/questions/11540854/file-as-command-line-argument-for-argparse-error-message-if-argument-is-not-va
def is_valid_file(filename):
    if not os.path.exists(filename):
        print("The file %s does not exist!")
        return False
    else:
        return True


if __name__ == "__main__":
    # Set commandline flags
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", 
        action="store_true")
    parser.add_argument("-p", "--plot", help="plot training accuracy and loss",
        action="store_true")
    parser.add_argument("-t", "--test", help="run model on test data",
        action="store_true")
    parser.add_argument("-o", "--old", help="use old model cnn-model-0",
        action="store_true")
    parser.add_argument("-i", "--input", help="input image file", nargs=1)

    args = parser.parse_args()
    if args.verbose:
        print("Turned on: verbosity")
    if args.plot:
        print("Turned on: plot")
    if args.test:
        print("Turned on: test")
    if args.old:
        print("Turned on: old")
    if args.input:
        print("Turned on: input")

    letters = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9',
10:'A', 11:'B', 12:'C', 13:'D', 14:'E', 15:'F', 16:'G', 17:'H', 18:'I', 19:'J',
20:'K', 21:'L', 22:'M', 23:'N', 24:'O', 25:'P', 26:'Q', 27:'R', 28:'S', 29:'T',
30:'U', 31:'V', 32:'W', 33:'X', 34:'Y', 35:'Z', 36:'a', 37:'b', 38:'c', 39:'d',
40:'e', 41:'f', 42:'g', 43:'h', 44:'i', 45:'j', 46:'k', 47:'l', 48:'m', 49:'n',
50:'o', 51:'p', 52:'q', 53:'r', 54:'s', 55:'t', 56:'u', 57:'v', 58:'w', 59:'x',
60:'y', 61:'z'}

    if args.plot:
        plot_model()

    if args.test or args.input:
        model = load_model()
        if args.test:
            test_model(model)
        #if args.input:
            # [0-9: digits][10-36: uppercase][37-62: lowercase]
            #prediction = predict_model(model, args.input[0])
            #print(prediction)
            #print(letters[int(prediction)])
    model = load_model()
    print(letters[int(predict_model(model, 'input_images/img-0.png'))])
    print(letters[int(predict_model(model, 'input_images/img-1.png'))])
    print(letters[int(predict_model(model, 'input_images/img-2.png'))])
    print(letters[int(predict_model(model, 'input_images/img-3.png'))])
    print(letters[int(predict_model(model, 'input_images/img-4.png'))])
    print(letters[int(predict_model(model, 'input_images/img-5.png'))])





