from flask import Flask
from flask import render_template, request, redirect, url_for
import sqlite3

from werkzeug.utils import secure_filename
import numpy as np
from tensorflow.keras.preprocessing import image
import numpy as np
from keras.models import load_model

def predict(filepath):
    # img = Image.open(io.BytesIO(img))
    img = image.load_img(filepath, target_size=(300, 300))
    img = image.img_to_array(img)
    img = np.asarray(img)/255
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img)

    print(pred)

    if(pred[0]<=1 and pred[0]>0.085):
        return "Tuber Detected","Exposure stage: Short-term hospitalization"
    elif(pred[0] <= 0.085 and pred[0] > 0.07):
        return "Tuber Detected","Latent Stage: For latent TB which is newly diagnosed usually a 6 to 12 month course of antibiotic called isoniazid will be given to kill of the TB organism in the body. Some people with latent TB maybe treated a shorter course of tweo antibiotics for only three months"
    elif(pred[0] <= 0.07 and pred[0] > 0.05):
        return "Tuber Detected","Active TB Stage: For active TB your health provider may prescribe three or more antibiotics in combination for 6 to 9 months or longer examples include isonized rifampin, pyrazinamid, and ethambutol. people usually begins to improve within a few weeks of the start of the treatment after several weeks of treatments with the correct medicine the person is usually no longer contagious if treatment is carried through to the end as prescribed by a health care provider."
    else:
        return "No Tubor","No Treatment"

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("detection.sqlite")
    except sqlite3.error as e:
        print(e)
    return conn

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
model = load_model('model.h5')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER    


@app.route('/', methods=['POST', 'GET'])
def home():
    conn = db_connection() 
    cursor = conn.cursor()
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        data1 = cursor.execute("SELECT * FROM Users WHERE username=?",(username,))
        data1 = cursor.fetchall()
        if data1:
            print("User Already Exists")
        else:
            cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            print("User Created")
            return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    conn = db_connection() 
    cursor = conn.cursor()
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM Users WHERE username=? AND password=?", (username,password))
        data = cursor.fetchall()
        if data:
            return redirect(url_for('home_page'))
        else:
            return render_template("login.html")
    return render_template("login.html")

@app.route('/home', methods=['POST', 'GET'])
def home_page():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(app.config['UPLOAD_FOLDER']+"/"+filename)
        result,description=predict(app.config['UPLOAD_FOLDER']+"/"+filename)        
        return render_template("home.html", result=result,description=description)
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)