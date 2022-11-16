from flask import Flask, render_template, url_for, request
# import pandas as pd
import pickle
import slidegen as slidegen # gslides\slides.py
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
		print ("hello")
		request_data = json.loads(request.data.decode('utf-8'))
		raw_data = request_data['data']

		selected_sentences = pipeline.summarize(raw_data)
		print(selected_sentences)
		presentationContent = {
			"title": "Our first slide",
			"subtitle": "This is our first slide",
			"slides": selected_sentences,
		}
		
		# presentationContent = {
		# 	"title": "Our first slide",
		# 	"subtitle": "This is our first slide",
		# 	"slides": [
		# 		"Hello this is somebody", "Elon musk is a great person", "I love him"
		# 	],
		# }
		slidegen.generateSlides(presentationContent)

		return jsonify({'message': "you now get the slides pdf"})

	if request.method == 'GET':
		return jsonify({'message': 'Please use the POST method'})	


test_text = """After Tesla and SpaceX CEO Elon Musk took ownership of Twitter last week, the social networking giant embarked on a steep reduction in its workforce. The cuts affected a total of 983 employees in California, its home state, according to three letters of notice that the company sent to regional authorities, which were obtained by CNBC.
The company’s new owner, CEO and sole director Musk, wrote in a tweet on Friday afternoon, “Regarding Twitter’s reduction in force, unfortunately there is no choice when the company is losing over $4M/day. Everyone exited was offered 3 months of severance, which is 50% more than legally required.” 
Twitter’s reduction in force extended beyond California, and CNBC could not immediately confirm whether Musk’s description is accurate. A loss of $4 million per day at the company would represent an annual loss around $1.5 billion. The federal Worker Adjustment and Retraining Notification (WARN) Act requires employers to provide advance notice, generally within 60 days, of mass layoffs or plant closings in California.
According to the letters from Twitter, shared by the California Employment Development Department, Twitter notified affected employees on Nov. 4. Many of those workers described losing access to email, and other internal systems at Twitter, overnight on Nov. 3 in public posts on social media, including on Twitter itself. This kind of arrangement may serve as “payment in lieu of notice,” in California depending on specific terms of employment. Permanent terminations are expected to begin Jan. 2023, according to the WARN notices.
In three different California WARN notice letters, signed by the Twitter Human Resources Department but no individual executives, the company wrote: “Affected employees will be paid all wages and other benefits to which they are entitled through their date of termination.”
According to the WARN notice, Twitter cut approximately 784 workers in San Francisco, including nine executive and senior level officials or managers, 147 mid-level employees who typically reported directly to top execs, 592 other professionals and 36 sales and administrative support workers combined.
At the company’s satellite locations in Santa Monica, Twitter cut approximately 93 employees including 17 mid-level officials and managers, 66 professionals and 10 combined sales and administrative support workers, the WARN notice showed. At a San Jose office, Twitter cut approximately 106 employees, including one executive or senior-level official or manager, 18 mid-level officials and managers, 85 professionals and two administrative support workers, according to the WARN notice. Twitter was sued Thursday by former employees in a proposed class action filed by worker’s rights attorney Shannon Liss Riordan and others who were concerned that employees were not given proper notice, under federal and California law, that they would be terminated in the mass layoffs.
Shannon Liss-Riordan, a worker’s rights attorney representing the terminated Twitter employees, did not immediately respond to a request for comment."""