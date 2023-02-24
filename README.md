# slideit
creating slides from url articles

Clone the repository
Its always wise to first create a virtual environment
Then install marp-cli and extract it to the root directory of the project
Then `pip install -r requirements.txt`
Finally hit `python main.py` and run the api

Different ways to use:
1. Connect the frontend(make your own) to the api and use it by sending text/URL to predict route
2. In routes.py update the test_text variable and run the api
3. Embed the URL of article in after '/' route method to generate the slide from that URL (example: localhost:5000/?url='cnn.com/article')
