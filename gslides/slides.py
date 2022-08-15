from __future__ import print_function
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from googleapiclient import discovery

# For authorized data access, we need additional resources http and oauth2client
from httplib2 import Http
from oauth2client import file, client, tools

import os.path
import io

# SCOPES is a critical variable: it represents the set of scopes of authorization an app wants to obtain (then access) on behalf of user(s).
SLIDES_SCOPES = 'https://www.googleapis.com/auth/presentations',

# If modifying these scopes, delete the file token.json.
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIAL = 'gslides/credential.json'



def generateSlidesFromAPI(content):
    
    presentation = createSlides(content)
    success = downloadFromDrive(presentation['title'])

    if success:
        print('Slides downloaded successfully.')
    else:
        print('Slides download failed.')

    return presentation['title']


def createSlides(content):
    '''
    Create a presentation from a Google Slides template.
    Returns the presentation ID.
    '''
    # Once the user has authorized access to their personal data by your app, a special "access token" is given to your app.
    # This precious resource must be stored in storage.json here

    store = file.Storage('gslides/storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CREDENTIAL, SLIDES_SCOPES)
        # creds variables are attempting to get a valid access token with which to make an authorized API call.
        creds = tools.run_flow(flow, store)

    # To create a service endpoint for interacting with an API, authorized or otherwise.
    SLIDES = discovery.build('slides', 'v1', http=creds.authorize(Http()))

    # To create a presentation, we need to create a presentation object.
    print('** Create new slide deck')
    DATA = {'title': content["title"]}
    rsp = SLIDES.presentations().create(body=DATA).execute()

    # THis is the unique presentation id of the presentation created
    deckID = rsp['presentationId']

    titleSlide = rsp['slides'][0]

    titleID = titleSlide['pageElements'][0]['objectId']

    subtitleID = titleSlide['pageElements'][1]['objectId']

    print('** Create "main point" layout slide & add titles')
    reqs = [
        {'createSlide':
         {
             'slideLayoutReference': {
                 'predefinedLayout': 'MAIN_POINT'
             }}},
        {
            'insertText':
            {
                'objectId': titleID,
                'text': content['title'],
            }},
        {
            'insertText': {
                'objectId': subtitleID,
                'text': content["subtitle"],
            }},
    ]

    # Creating the slides one by one
    rsp = SLIDES.presentations().batchUpdate(body={'requests': reqs},
                                             presentationId=deckID).execute().get('replies')
    slideID = rsp[0]['createSlide']['objectId']

    print('** Fetch "main point" slide title (textbox) ID')
    rsp = SLIDES.presentations().pages().get(presentationId=deckID,
                                             pageObjectId=slideID).execute().get('pageElements')
    textboxID = rsp[0]['objectId']

    # text bhitra bullet points ma rakne chij rakhne ho text[0] euta sentence text[1] arko and likewise..
    text = content["slides"][0]
    noOfSentences = len(text)
    print('** Insert text & perform various formatting operations')

    def processBulletPoints(text):
        '''
        Process bullet points.
        '''
        bull = [sent+'\n' if sent != text[-1] else sent for sent in text]
        return ''.join(bull)

    bullets = processBulletPoints(text)

    # Next slide
    reqs = [
        # add 7 paragraphs
        {'insertText': {
            'text': bullets ,
            'objectId': textboxID,
        }},
        # shrink text from 48pt ("main point" textbox default) to 32pt
        {'updateTextStyle': {
            'objectId': textboxID,
            'style': {'fontSize': {'magnitude': 25, 'unit': 'PT'}},
            'textRange': {'type': 'ALL'},
            'fields': 'fontSize',
        }},
        # change word 1 in para 1 ("Bold") to bold
        {'updateTextStyle': {
            'objectId': textboxID,
            # 'style': {'bold': True},
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': 0, 'endIndex': 5},
            'fields': 'bold',
        }},
        # change word 1 in para 2 ("Ital") to italics
        {'updateTextStyle': {
            'objectId': textboxID,
            # 'style': {'italic': True},
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': 7, 'endIndex': 11},
            'fields': 'italic'
        }},
        # change word 1 in para 6 ("Mono") to Courier New
        {'updateTextStyle': {
            'objectId': textboxID,
            # 'style': {'fontFamily': 'Courier New'},
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': 36, 'endIndex': 40},
            'fields': 'fontFamily'
        }},

        # bulletize everything
        {'createParagraphBullets': {
            'objectId': textboxID,
            'textRange': {'type': 'ALL'}},
         },
    ]
    SLIDES.presentations().batchUpdate(body={'requests': reqs},
                                       presentationId=deckID).execute()

    my_presentation = SLIDES.presentations().get(presentationId=deckID).execute()
    # print(my_presentation)

    print('** Done!')

    return my_presentation


def downloadFromDrive(filename):
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gslides/token.json'):
        creds = Credentials.from_authorized_user_file(
            'gslides/token.json', DRIVE_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL, DRIVE_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gslides/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            q="name='"+filename+"'",
            spaces='drive',
            pageSize=5, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

        slideFileId = items[0]['id']

        request = service.files().export_media(
            fileId=slideFileId, mimeType='application/pdf')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download {int(status.progress() * 100)}.')

        if done:
            # write file as pdf
            # with open(f'presentation_pdfs/{filename}.pdf', 'wb') as f:
            with open(f'presentation_pdfs/slides.pdf', 'wb') as f:
                f.write(file.getvalue())

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

    return done
