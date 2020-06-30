import pickle
import json
from flask import Flask,request,render_template
from flask import jsonify, make_response
from preprocess import preprocess
app = Flask(__name__)

@app.route('/',methods = ['GET'])
def home():
    return render_template('index.html')

@app.route('/predict' , methods = ['POST'])
def predict():

    data = request.get_json(force=True)
    print(data)
    df = preprocess(data)
    with open('./models/RandomForestModel.pickle','rb') as file:
        model = pickle.load(file)
    prediction = model.predict(df)

    json_data = { 
        "prediction" : prediction[0]
    }

    print(json_data)
    res = make_response(jsonify(json_data), 200)

    return res

if __name__ == "__main__":
    app.run(debug=True, port=9000)