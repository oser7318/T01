import numpy as np 
import matplotlib.pyplot as plt
import itertools


import os
from gpuutils import GpuUtils
GpuUtils.allocate(gpu_count=1, framework='keras')

import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
for device in physical_devices:
    tf.config.experimental.set_memory_growth(device, True) 

from tensorflow import keras
from generator import list_of_file_ids_test, n_events_per_file, n_files_train, n_files_val, batch_size, TestDataset
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(cm, classes,
                        normalize=True,
                        title='Confusion matrix',
                        cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    fig=plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = 100 * cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        cm = cm.astype('float').round(decimals=2)
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')
    
    np.set_printoptions(precision=2)
    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f'{cm[i, j]}%',
            horizontalalignment="center",
            color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()

    plt.savefig(f'{title.replace(" ", "_")}.png')


test_data, true_category = TestDataset(noise=True)

true_category=np.argmax(true_category,axis=1) #what index the max value is at. 1 means [0,1], 0 means [1,0]

#Load saved model
model=keras.models.load_model('/mnt/md0/oericsson/NuRadio/saved_models/NuFlavorCNN4_2_NoisyData/model_best.h5')

#Let model make predictions on validation dataset
category_predictions = model.predict(test_data, batch_size=batch_size)
category_predictions = np.argmax(category_predictions, axis=1) #what index the max value is at. 1 means [0,1] (e cc), 0 means [1,0] (NCs and mu/tau cc)

comp_true_category = true_category
comp_predicted_category = category_predictions


#Create confusion matrix using scikit learn built in confusion matrix function
cm = confusion_matrix(y_true=comp_true_category, y_pred=comp_predicted_category)
cm_plot_labels = ['The rest', 'e CC']

#Plot the confusion matrix
plot_confusion_matrix(cm=cm, classes=cm_plot_labels, title='Confusion matrix NuFlavorCNN 4.2 Noisy')