import json
import requests

# Set the API key
API_KEY = "AIzaSyCRHHSb8Mqw22QlcILOoWwypjHs2FqBrR0"

# Set the URL for the Google Cloud Natural Language Processing API
API_URL = "https://language.googleapis.com/v1/documents:classifyText?key=" + API_KEY

# define keyword itself
keyword = "FC-Bayern"
# Set the text to be analyzed full of fillwords
text = f"{keyword} and ourselves as herserf for each all above into through nor me and then by doing and and or and as she her and or"

# Set the document to be sent to the API
document = {
    "type": "PLAIN_TEXT",
    "content": text
}

# Set the request headers
headers = {
    "Content-Type": "application/json"
}

# Set the request body
body = {
    "document": document
}

# Send a POST request to the API
response = requests.post(API_URL, json=body, headers=headers)

# Check the response status code
if response.status_code == 200:
    # Parse the response JSON
    response_json = response.json()

    # Loop through the categories in the response
    for category in response_json["categories"]:
        # Print the name and confidence level of the category
        print(f"Category: {category['name']}, Confidence: {category['confidence']}")
else:
    # Print the error message
    print(f"Error: {response.text}")
