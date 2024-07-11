# -*- coding: utf-8 -*-
"""watering_system.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UuW69T-fxUnvVw2aXlVDH3kFGRW8x5Si

# Model with TF
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelBinarizer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import MinMaxScaler
from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.models import load_model

app = Flask(__name__)
CORS(app)

df = pd.read_csv('TARP.csv')
df = df.drop(['Time', 'Wind gust', 'Wind speed', 'Pressure', 'rainfall', 'N', 'P', 'K'], axis =1)
df = df.sample(n=10000, random_state=42)

encoder = LabelBinarizer()
df['Status'] = encoder.fit_transform(df['Status'])
df.info()

# handling missing data
imputer = IterativeImputer(random_state=46, verbose=True)
data = imputer.fit_transform(df)
data = pd.DataFrame(data, columns = df.columns)

# data normalization from -1 to 1
scaler = MinMaxScaler((-1,1))
sdf = scaler.fit_transform(data.iloc[:,:-1], data.iloc[:,-1])
scaled_df = pd.DataFrame(sdf, columns = data.iloc[:,:-1].columns)
# tidak mengubah kolom status
scaled_df['Status'] = data['Status']

# plt.hist(scaled_df['Status'])
# plt.show()
#
# x = scaled_df.iloc[:,:-1]
# y = scaled_df.iloc[:,-1]
#
# x_train,x_test,y_train,y_test = train_test_split(x, y, test_size=0.2, random_state=7)
#
# print('X_train shape : ',  x_train.shape)
# print('y_train shape : ',  y_train.shape)
# print('X_test shape : ',  x_test.shape)
# print('y_test shape : ',  y_test.shape)

# model = tf.keras.Sequential([
#     tf.keras.layers.Dense(64, input_shape=(6,)),
#     tf.keras.layers.Dense(16, activation='relu'),
#     tf.keras.layers.Dense(8, activation='relu'),
#     tf.keras.layers.Dense(1, activation='sigmoid')
# ])
#
# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
#
# history = model.fit(x_train, y_train, epochs=20, batch_size=32, validation_data=(x_test, y_test))
#
# model.save("model_iot.h5")

# # preprocessing datanya belum bener!
# data_1 = (22.0, 41.0, 56.0, 24.330292, 57.696575, 6.501160)
# data_2 = (28.0, 25.0, 48.0, 24.157220, 59.301666, 6.473901)
#
# def preprocessing_data(data):
#   input_data_as_array = np.asarray(data)
#   input_data_reshaped = input_data_as_array.reshape(1,-1)
#   std_data = scaler.transform(input_data_reshaped)
#   pred = model.predict(std_data)
#   if pred > 0.5:
#       print("ON")
#   else:
#       print("OFF")
#
# preprocessing_data(data_1)
# preprocessing_data(data_2)

model = load_model("model_iot.h5")

@app.route("/predict", methods= ["POST"])
def preprocessing_data():
    user_input = request.get_json(force=True)
    data = user_input.get('data')
    # Convert list to tuple
    data = tuple(data)
    input_data_as_array = np.asarray(data)
    input_data_reshaped = input_data_as_array.reshape(1,-1)
    std_data = scaler.transform(input_data_reshaped)
    pred = model.predict(std_data)
    response = {
        "status": "ON" if pred > 0.5 else "OFF"
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)