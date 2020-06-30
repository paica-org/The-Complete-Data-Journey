import pickle
import json
from flask import Flask
from flask import request
from preprocess import preprocess
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is a Flask API'

@app.route('/predict' , methods = ['POST'])
def predict():

    data = request.get_json(force=True)
    print(data)
    df = preprocess(data)
    with open('./models/RandomForestModel.pickle','rb') as file:
        model = pickle.load(file)
    prediction = model.predict(df)

    return json.dumps(prediction[0])

if __name__ == "__main__":
    app.run(debug=True, port=9000)