# app.py

from flask import Flask
from get_jobs_app import api_bp 

app = Flask(__name__)
app.register_blueprint(api_bp)  

@app.route('/')
def home():
    return "GlobalBridge Backend Running!"

if __name__ == '__main__':
    app.run(debug=True)
