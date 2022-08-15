import nltk
nltk.download('punkt')
from nltk import sent_tokenize

from model.config import *
import numpy as np
from keras_preprocessing.sequence import pad_sequences
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

def create_attention_mask(input_ids):
  attention_masks = []
  for sent in input_ids:
    att_mask = [int(token_id > 0) for token_id in sent]  # create a list of 0 and 1.
    attention_masks.append(att_mask)  # basically attention_masks is a list of list
  return attention_masks

def return_clusters(sentence_features, number_extract):
    kmeans = KMeans(n_clusters=number_extract, random_state=0).fit(sentence_features)
    cluster_centers = kmeans.cluster_centers_
    nbrs = NearestNeighbors(n_neighbors= 1,algorithm='brute').fit(sentence_features)
    distances, indices = nbrs.kneighbors(cluster_centers.reshape(number_extract,-1))
    indices = np.sort(indices.reshape(1,-1))
    return indices[0]

def extractive_sum(text):
    # Extractive summarization
    paragraph_split = sent_tokenize(text)
    input_tokens = []
    for i in paragraph_split:
        input_tokens.append(tokenizer.encode(i, add_special_tokens=True))
    
    temp = []
    for i in input_tokens:
        temp.append(len(i))

    input_ids = pad_sequences(input_tokens, maxlen=100, dtype="long", value=0, truncating="post", padding="post")
    input_masks = create_attention_mask(input_ids)
    
    #creating a tensor for input_ids and input_masks
    input_ids = torch.tensor(input_ids, dtype=torch.long)
    input_masks = torch.tensor(input_masks, dtype=torch.long)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=input_masks)

    encoder_output = outputs.encoder_last_hidden_state
    sentence_features = encoder_output[:,0,:].detach().numpy()

    topic_answer = []
    for i in return_clusters(sentence_features, 15):
        topic_answer.append(paragraph_split[i])

    return topic_answer

def abstractive_sum(text):
    # Abstractive summarization
    input_ids = tokenizer(
        text, max_length=1024,
        truncation=True, padding='max_length',
        return_tensors='pt'
    ).to(device)

    summaries = model.generate(
        input_ids=input_ids['input_ids'],
        attention_mask=input_ids['attention_mask'],
        max_length=256
    )
    decoded_summaries = [tokenizer.decode(s, skip_special_tokens=True, clean_up_tokenization_spaces=True) for s in summaries]
    return decoded_summaries

def summarize(text):
    topic_answer = extractive_sum(text)
    extracted_text = ' '.join(topic_answer)
    abstractive_answer = abstractive_sum(extracted_text)
    sentences = abstractive_answer[0].split('.')
    return sentences
    
text = """
Elon Musk's legal team on Friday made public its official response to Twitter's lawsuit attempting to force him to complete their $44 billion acquisition deal.
In the answer to Twitter's complaint, which includes counter-claims against the company, Musk's team attempts to refute the company's allegations that the Tesla CEO is unjustly trying to exit the deal. His team repeats allegations that Twitter has misstated the number of fake and spam bot accounts on its platform — a central charge Musk has made to justify terminating the acquisition agreement after originally citing a desire to "defeat the spam bots" as a reason for buying the company.
Musk's response, which was filed publicly on Friday, states that the billionaire's team conducted an analysis of fake and spam accounts on the platform using data provided by Twitter's "firehose" of tweets and a public tool called Botometer created by researchers at the University of Indiana. It did not further detail the process of that evaluation and added that its analysis was "constrained" by a lack of time and information from Twitter.
Based on that analysis, Musk alleges that during the first week of July, spam bots accounted for 33% of visible accounts on the platform and about 10% of Twitter's monetizable daily active users, or mDAU. (Twitter, for its part, has consistently reported that spam and fake bot accounts make up less than 5% of its mDAU.)
Twitter has repeatedly denied Musk's claims about the prevalence of spam bots on the platform. Twitter Board Chair Bret Taylor tweeted on Thursday evening a link to the company's response to his answer and counterclaims. (Musk's team had filed a confidential version of the answer last week to give Twitter (TWTR) time to review it for company information that should be redacted, before making it publicly available Friday.) Taylor called Musk's claims "factually inaccurate, legally insufficient, and commercially irrelevant."
In its response, Twitter takes issue with Musk's analysis of spam bots, saying that the "firehose" of data he used "reflects many Twitter accounts that are not included in mDAU" and that the Botometer tool he used relies on a different process than the company to determine whether an account may be a bot. It added that Botometer "earlier this year designed Musk himself as highly likely to be a bot."
The back-and-forth between Twitter and Musk offers a preview of the arguments each side will make when the case goes to trial, assuming they don't agree to a settlement first. A five-day trial is set to kick off on October 17, after Twitter had pressed to expedite the proceedings.
Musk last month moved to terminate his agreement to buy Twitter, accusing the company of breaching the deal by making misleading statements about the number of bot accounts on its platform and withholding information that he claims could help him evaluate the issue. Days later, Twitter filed a lawsuit against the billionaire, alleging that he'd violated the agreement and asking a court to compel him to follow through with the deal.
In addition to doubling down on concerns about bot accounts, Musk's responses also criticized Twitter's use of monetizable daily active users, a metric Twitter publicly reports to advertisers and shareholders to represent its growth.
Musk claims that his evaluations show only a small portion of the users Twitter considers mDAU actually generate significant revenue for the company by viewing and engaging with advertisements, alleging that the measure is not actually as good an indicator of future revenue growth potential and long-term performance as Twitter's public filings imply.
"Twitter also does not publish the methodology it follows to determine its mDAU count, or how it excludes nonmonetizable accounts from that metric," Musk's answer states. "Thus, it is extremely difficult for any third party to completely recreate Twitter's mDAU calculations."
Musk's answer alleges Twitter leadership has incentives to report "high mDAU numbers to stoke investor interest" and because its executive compensation structure is based partly on mDAU.
In its answer, Musk's team explains that the billionaire is concerned with the spam bot issue because "transitioning users who do not generate any revenue into more active users ... is no easy task." Musk's team adds: "A company focused on adding these active users would invest substantial resources towards trying to improve Twitter to maximize engagement, such as by effectively targeting spam or false accounts."
Twitter said in its response to Musk's counterclaims that its mDAU count has never purported to show how many users generate significant revenue by interacting with ads, but rather shows the number of real users who could be monetized by being shown ads. It also noted that Musk's mDAU-related claims were not included in his initial termination filing and "are a newly invented litigating position."
The company also continues to claim that the issue of bots is not, and has never been, germane to the completion of the acquisition deal. "Musk has received massive amounts of information from Twitter, for months, and has been unable to find a valid excuse to back out of the contract," Twitter's response states.
In a letter to Twitter employees that was included in Friday's regulatory filing, Twitter General Counsel Sean Edgett said that while Twitter had the opportunity to request redactions in Musk's answer, it chose not to. (Twitter had previously sent a letter to the judge overseeing the case asking her to ensure Musk's team would not file the public answer early so they would have enough time to review it for potential redactions.)
"We chose not to redact any information--we fully stand behind our SEC filings, the methodologies we use to calculate mDAU, and our statements about the percentage of spam accounts on our platform," Edgett said in the letter.
"""

# answer = summarize(text)
# print (answer)