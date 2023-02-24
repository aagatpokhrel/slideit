import parsing as parsing
import model.pipeline as pipeline
import slidegen as slidegen

from app import app
from flask import Response
from flask import jsonify
from flask import render_template, request

@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

@app.route('/')
def home():
	url = request.args.get('url')
	if (url):
		document = parsing.parse_url(url)
		document['slides'] = pipeline.get_slide_content(document['text'])
		slidegen.create_slides(document)
		return render_template('output.html', title='slideit')
        
	return jsonify({'slideit-api': 'please use url to get the slides'})






