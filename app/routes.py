from flask import Flask, render_template, url_for, request
# import pandas as pd
import pickle
import gslides.slides as slides # gslides\slides.py
import model.pipeline as pipeline # model\pipeline.py

import json
from flask import jsonify
from app import app
from flask import Response

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

@app.route('/')
def home():
	return jsonify({'message': 'Welcome to the SlideIt-API'})


@app.route('/predict', methods=['POST', 'GET'])
def predict():

	if request.method == 'POST':
		# extract the prediction from the model
		request_data = json.loads(request.data.decode('utf-8'))
		raw_data = request_data['data']

		selected_sentences = pipeline.summarize(raw_data)
		print(selected_sentences)
		presentationContent = {
			"title": "Our first slide",
			"subtitle": "This is our first slide",
			"slides": [
				selected_sentences
			],
		}
		

		generatedSlides = slides.generateSlidesFromAPI(presentationContent)
		print(generatedSlides)

		return jsonify({'message': "you now get the slides pdf"})

	if request.method == 'GET':
		return jsonify({'message': 'Please use the POST method'})	
