from flask import Flask, render_template, request, jsonify
import json, logging, os, atexit

#EQUIPO
#Laurie Valeria Diego Macias A01566647
#Isaac Emanuel García González A01566697
#Angel Corrales Sotelo A01562052
#Yoceline Aralí Mata Ledezma A01562116

# Model design
import agentpy as ap
import random
import numpy as np


app = Flask(__name__, static_url_path='')

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

jsonString = "["

#Agent definition


@app.route('/')
def root():
    #ControlModel(parameters).run(display = False)
    return jsonify(jsonString)
    #return jsonify([{"message":"Pruebas Tec, from IBM Cloud!"}])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
