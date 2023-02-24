import nltk
nltk.download('punkt')
from nltk import sent_tokenize, word_tokenize
import math

from model.config import *
import numpy as np
from keras_preprocessing.sequence import pad_sequences
from sklearn.cluster import KMeans
from scipy.spatial.distance import cosine

def create_attention_mask(input_ids):
  attention_masks = []
  for sent in input_ids:
    att_mask = [int(token_id > 0) for token_id in sent]  # create a list of 0 and 1.
    attention_masks.append(att_mask)  # basically attention_masks is a list of list
  return attention_masks

def get_sentence_features(text):
    paragraph_split = sent_tokenize(text)
    input_tokens = []
    for i in paragraph_split:
        input_tokens.append(tokenizer.encode(i, add_special_tokens=True))
    
    temp = []
    for i in input_tokens:
        temp.append(len(i))

    input_ids = pad_sequences(input_tokens, maxlen=100, dtype="long", value=0, truncating="post", padding="post")
    input_masks = create_attention_mask(input_ids)
    
    ##--For CPU --##
    input_ids = torch.tensor(input_ids, dtype=torch.long)
    input_masks = torch.tensor(input_masks, dtype=torch.long)

    ##--For GPU --##
    # input_ids = torch.tensor(input_ids, dtype=torch.long).to(device)
    # input_masks = torch.tensor(input_masks, dtype=torch.long).to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=input_masks)

    encoder_output = outputs.encoder_last_hidden_state

    ## -- For CPU --## Because it is assumed to be on CPU .cpu() function is not used
    sentence_features = encoder_output[:,0,:].detach().numpy()

    ## -- For GPU --## Because it is assumed to be on GPU .cpu() function is used
    # sentence_features = encoder_output[:,0,:].detach().cpu().numpy()

    return sentence_features

def clustering(text, features, number_extract=3):
    text = sent_tokenize(text)
    kmeans = KMeans(n_clusters=number_extract, 
                    random_state=0).fit(features)
    feature_space = {}
    cluster_space = {}
    for k, (i, j)  in enumerate(zip(kmeans.labels_, text)):
        cluster_space.setdefault(i, []).append(j)
        feature_space.setdefault(i, []).append(features[k]) #this might be the culprit
    cluster_centers = kmeans.cluster_centers_
    return cluster_space, feature_space, cluster_centers

def extractive_sum(cluster_center, sentence_list, feature_list):
    # Extractive summarization
    sentences = ''.join(sentence_list)
    word_count = len(word_tokenize(sentences))
    if (word_count < 400):
        yank = 0.8
    else:
        yank = 400/word_count

    similarity_index = [cosine(cluster_center, sentence_feature) for sentence_feature in feature_list]
    
    ranked_sent = np.argsort(similarity_index)
    extracted_sent = math.floor(yank * len(sentence_list))
    ranked_and_yanked = ranked_sent[:extracted_sent]
    new_sent = [sentence_list[i] for i in ranked_and_yanked]
    sentences= ''.join(new_sent)
    return sentences

def abstractive_sum(text):
    # Abstractive summarization
    input_ids = tokenizer(
        text, max_length=400,
        truncation=True, padding='max_length',
        return_tensors='pt'
    ).to(device)

    ## -- For CPU --## 
    summaries = model.generate(
        input_ids=input_ids['input_ids'],
        attention_mask=input_ids['attention_mask'],
        max_length=200,
        min_length=100
    )

    ## -- For GPU --##
    # summaries = model.cuda().generate(
    # input_ids=input_ids['input_ids'],
    #    attention_mask=input_ids['attention_mask'],
    #    max_length=200,
    #    min_length=100
    #)

    decoded_summaries = [tokenizer.decode(s, skip_special_tokens=True, clean_up_tokenization_spaces=True) for s in summaries]
    return decoded_summaries[0]

def get_slide_content(text):
    topics = ['Background', 'Details', 'Conclusion']
    sent_per_slide = 3
    slide_content = {'Background': None, 'Details': None, 'Conclusion': None}
    total_slides = 0

    sentence_features = get_sentence_features(text)
    cluster_space, feature_space, cluster_centers = clustering(text, sentence_features)

    for label, sentences in cluster_space.items():
        extracted_text = extractive_sum(cluster_centers[label], sentences, feature_space[label])
        abstractive_answer = abstractive_sum(extracted_text)
        sentences = sent_tokenize(abstractive_answer)
        num_of_slides = math.ceil(len(sentences)/sent_per_slide)
        section_slides = {}
        for i in range(num_of_slides):
            section_slides[i] = sentences[k:k+sent_per_slide]
            k=k+sent_per_slide

        slide_content[topics[label]] = section_slides

    return slide_content
