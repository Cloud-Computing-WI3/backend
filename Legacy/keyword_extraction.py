from keybert import KeyBERT
import yake
import requests
""""""
text1 = ["Hugo Lloris has said France are primed for a ‘big battle’ with England as the countries prepare for Saturday’s World Cup quarter-final" ]
doc = """

Hugo Lloris has said France are primed for a ‘big battle’ with England as the countries prepare for Saturday’s World Cup quarter-final


"""
kw_model = KeyBERT()
keywords = kw_model.extract_keywords(doc)
print(keywords)

kw_extractor = yake.KeywordExtractor(top=5, n=2)

keywords = kw_extractor.extract_keywords(doc)
print(keywords)




def extract_keywords(text):
    # Set the API key for the Google Natural Language Processing API
    api_key = 'AIzaSyCRHHSb8Mqw22QlcILOoWwypjHs2FqBrR0'
    # Set the text to analyze

    # Set the API endpoint URL
    api_url = 'https://language.googleapis.com/v1/documents:analyzeEntities?key=' + api_key

    # Set the request payload
    payload = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': text
        },
        'encodingType': 'UTF8'
    }

    # Make the request to the API
    response = requests.post(api_url, json=payload)

    # Parse the response dictionary
    response_dict = response.json()

    # Get the list of entities from the response
    entities = response_dict['entities']

    # make sure that its not more than 10 and sort by salience, highest salience first
    top_entities = [entity for entity in sorted(entities, key=lambda x: x['salience'], reverse=True)][
                   :min(10, len(entities))]
    # make into a list and remove duplicates
    entities_list = list({entry['name'] for entry in top_entities})
    return entities_list

keywords = extract_keywords(doc)
print(keywords)