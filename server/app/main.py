from flask import Flask, request
from flask_cors import CORS, cross_origin
from tools.errtool import catchnoauth
from storage import quietcatch


# Flask variables (global).
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#   --  Endpoints   --  #
"""
Creates a new user document.
"""
@app.route('/create', methods=['POST'])
@cross_origin()
def create_endpoint() -> dict:
    
    return catchnoauth("create", request.json)

"""
Adds a dog to a user's document.
"""
@app.route('/registerdog', methods=['POST'])
@cross_origin()
def register_dog() -> dict:
    
    return quietcatch("registerdog", request)

"""
Endpoint to handle login requests.
"""
@app.route('/login', methods=['POST'])
@cross_origin()
def login() -> dict:
    
    #return quietcatch(_login, request)
    return snapshot(request.json)

"""
Endpoint to add a schedule to a dog.
"""
@app.route('/scheduledog', methods=['POST'])
@cross_origin()
def schedule_dog() -> dict:
    
    return quietcatch("scheduledog", request)

@app.route('/snapshot', methods=['POST'])
@cross_origin()
def snapshot():
    
    return snapshot(request.json)

#extra thing for quietcatch
@app.route('/deletedog', methods=['POST'])
@cross_origin()
def delete_dog():
    
    return quietcatch("deletedog", request)

#extra thing for quietcatch
@app.route('/deleteschedule', methods=['POST'])
@cross_origin()
def delete_schedule():
    return quietcatch("deleteschedule", request)