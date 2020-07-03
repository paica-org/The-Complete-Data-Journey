import pickle
import json
import uuid
import seaborn as sns
sns.set(font_scale=1.5)
import matplotlib.pyplot as plt
from config import ACCESS_KEY,SECRET_KEY
import boto3
import os
import pandas as pd
from flask import Flask,request,render_template
from flask import jsonify, make_response
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from preprocess import preprocess


########################################################
#                      CONFIG                          #
########################################################
engine = create_engine("postgresql://postgres:Prince@99@localhost:5432/Sales")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

#Setting DB configurations
app.secret_key = '12345678' 
#Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#Setting AWS S3
bucket_name = "graph-sales"

s3 = boto3.resource(
   "s3",
   aws_access_key_id=ACCESS_KEY,
   aws_secret_access_key=SECRET_KEY
)
bucket_resource = s3

########################################################
#                      ROUTES                          #
########################################################

@app.route('/',methods = ['GET'])
def home():
    #read from db and draw graphs
    df = pd.read_sql_table('sales',engine)
    print(df)

    ##################################
    #             PLOT 1             #
    ##################################
    print("Started plot 1")
    tag = 'sales-outletType-years'

    try:
        result = db.execute("SELECT url from graphs where tag = :tag",
          { "tag" : tag})

        db.commit()
        for r in result:
            full_url = r[0]

        delete_image = full_url.split('/')[::-1][0]
        print("Deleting")
        s3.Object(bucket_name, delete_image).delete()
    except Exception as err:
        print(err)

    fig, axes = plt.subplots(2,1,figsize=(10,10))

    out_type = df.groupby(["outlet_type"]).sales.sum().reset_index()
    axes[0].bar(out_type.outlet_type,out_type.sales,color="orange")
    axes[0].set_xlabel("Outlet_Type",fontsize=15)
    axes[0].set_ylabel("Mean Sales",fontsize=15)

    establish = df.groupby(["esta_years"]).sales.mean().reset_index()
    axes[1].bar(establish.esta_years,establish.sales,color="black")
    axes[1].set_xlabel("Outlet_Establishment_Year",fontsize=15)
    axes[1].set_ylabel("Mean Sales",fontsize=15)
    id = uuid.uuid4()
    image_name = str(id)+".png"
    plt.savefig("static/graphs/" + image_name)
    with open("static/graphs/" + image_name, "rb") as img_data:
        s3.Bucket(bucket_name).put_object(Key=image_name, 
                                    Body=img_data, 
                                    ContentType="image/png", 
                                    ACL="public-read")

    plot_one_url = "http://" + bucket_name + ".s3.amazonaws.com/" + image_name
    try:
        db.execute("UPDATE graphs SET url = :url where tag = :tag",
                    {"url": plot_one_url, "tag": tag})
        db.commit()
    except:
        print("Error in plot 1")
    print("Finished plot 1")
    ##################################
    #             PLOT 2             #  
    ##################################
    print("Started plot 2")
    tag = 'visi-sales-outlet'

    try:
        result = db.execute("SELECT url from graphs where tag = :tag",
          { "tag" : tag})

        db.commit()
        for r in result:
            full_url = r[0]

        delete_image = full_url.split('/')[::-1][0]
        s3.Object(bucket_name, delete_image).delete()
    except:
        print("Error in deleting operation 2")

    fig,axes=plt.subplots(2,1,figsize=(10,10))
    sns.scatterplot(x='visi',y='sales',data=df,ax = axes[0], hue="outlet", color = "magenta",s=100)
    sns.scatterplot(x='mrp',y='sales',data=df,ax = axes[1], hue="outlet", color = "black",s=100)

    id = uuid.uuid4()
    image_name = str(id)+".png"
    plt.savefig("static/graphs/" + image_name)
    with open("static/graphs/" + image_name, "rb") as img_data :
        s3.Bucket(bucket_name).put_object(Key=image_name, 
                                    Body=img_data, 
                                    ContentType="image/png", 
                                    ACL="public-read")

    plot_two_url = "http://" + bucket_name + ".s3.amazonaws.com/" + image_name

    try:
        db.execute("UPDATE graphs SET url = :url where tag = :tag",
                    {"url": plot_two_url, "tag": tag})
        db.commit()
    except:
        print("Error in plot 2")

    print("Finished plot 2")

    ##################################
    #             PLOT 3             #  
    ##################################
    print("Started plot 2")
    tag = 'sales-dist'

    try:
        result = db.execute("SELECT url from graphs where tag = :tag",
          { "tag" : tag})

        db.commit()
        for r in result:
            full_url = r[0]

        delete_image = full_url.split('/')[::-1][0]
        s3.Object(bucket_name, delete_image).delete()
    except:
        print("Error in deleting operation 3")

    plt.figure(figsize=(12,6))
    sns.distplot(df.sales)
    plt.title("Outlet_sales_Distribution")

    id = uuid.uuid4()
    image_name = str(id)+".png"
    plt.savefig("static/graphs/" + image_name)
    with open("static/graphs/" + image_name, "rb") as img_data :
        s3.Bucket(bucket_name).put_object(Key=image_name, 
                                    Body=img_data, 
                                    ContentType="image/png", 
                                    ACL="public-read")

    plot_dis = "http://" + bucket_name + ".s3.amazonaws.com/" + image_name

    try:
        db.execute("UPDATE graphs SET url = :url where tag = :tag",
                    {"url": plot_dis, "tag": tag})
        db.commit()

        # s3.Object(bucket_name, image_name).delete()
    except:
        print("Error in plot 3")

    print("Finished plot 3")

    return render_template('index.html' , 
        plot_one_url = plot_one_url,
        plot_two_url = plot_two_url,
        plot_dis = plot_dis
        )

@app.route('/predict' , methods = ['POST'])
def predict():

    data = request.get_json(force=True)
    print(data)

    mrp = float(data['mrp'])
    outlet_type = data['outlet_type']
    outlet = data['outlet']
    esta_years = int(data['esta_years'])
    visi = float(data['visi'])

    df = preprocess(data)
    with open('./models/RandomForestModel.pickle','rb') as file:
        model = pickle.load(file)
    prediction = model.predict(df)

    try:
        print("Inserting into Sales Table............")
        db.execute( "INSERT INTO sales (outlet,outlet_type,mrp,esta_years,visi,sales) VALUES (:outlet,:outlet_type,:mrp,:esta_years,:visi,:sales)",
                        {"outlet": outlet, "outlet_type": outlet_type, "mrp":mrp, "esta_years":esta_years, "visi": visi, "sales":prediction[0]}
                    ) 
        db.commit()
        print("Done inserting into Sales Table............")
    except:
        print("Error in inserting..........")


    json_data = { 
        "prediction" : prediction[0]
    }

    print(json_data)
    res = make_response(jsonify(json_data), 200)

    return res



if __name__ == "__main__":
    app.run(debug=True, port=9000)