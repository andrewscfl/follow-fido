from flask import Flask, request
from flask_cors import CORS, cross_origin
from fido.error import catchnoauth
from fido.storage import ep_action, create


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
    
    return create(request.json)

"""
Adds a dog to a user's document.
"""
@app.route('/registerdog', methods=['POST'])
@cross_origin()
def register_dog() -> dict:
    
    return ep_action("registerdog", request)

"""
Endpoint to handle login requests.
"""
@app.route('/login', methods=['POST'])
@cross_origin()
def login() -> dict:
    
    return ep_action("login", request)

"""
Endpoint to add a schedule to a dog.
"""
@app.route('/scheduledog', methods=['POST'])
@cross_origin()
def schedule_dog() -> dict:
    
    return ep_action("scheduledog", request)

@app.route('/snapshot', methods=['POST'])
@cross_origin()
def snapshot():
    
    return ep_action("snapshot", request)

#extra thing for ep_action
@app.route('/deletedog', methods=['POST'])
@cross_origin()
def delete_dog():
    
    return ep_action("deletedog", request)

#extra thing for ep_action
@app.route('/deleteschedule', methods=['POST'])
@cross_origin()
def delete_schedule():
    
    return ep_action("deleteschedule", request)