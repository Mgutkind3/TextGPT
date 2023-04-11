import os
import requests
from twilio.rest import Client
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/text', methods=['GET','POST'])
def getText():
    # Change the api endpoint here (exposed via the command ngrok http 5000) :
    print('incoming text: ',)
    if request.method == 'GET':
        data = {'message': 'This is a simple Flask API.'}
        return jsonify(data)
    elif request.method == 'POST':
        # content = request.json

        # Parse response from POST request - get body and sender
        incoming_message = request.values.get('Body', '')
        sender_phone_number = request.values.get('From', '')
        print('Received message from', sender_phone_number, ':', incoming_message)
        # data = {'message': 'You sent: {}'.format(incoming_message)}

        # Call Chat GPT with Question
        question = incoming_message
        response = callGPT(question)
        jresp = json.loads(response)
        # print(response)
        for choice in jresp['choices']:
            print(choice['message']['content'])
            answer = choice['message']['content']

        sendText(answer)

        data = {'message': 'Message Returned...'}
        return jsonify(data)

    # To test:
    #curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, Flask!"}' http://localhost:5000/text
    #curl -X POST -H "Content-Type: application/json" -d '{"message": "Hello, Flask!"}' https://4e1a-71-125-84-62.ngrok.io/text


def sendText(response):
    print('sending response')

    account_sid = os.environ.get("TWILIO_ACCT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    fromNum = os.environ.get("FROM_NUMBER")
    toNum = os.environ.get("TO_NUMBER")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=response,
        from_=fromNum,
        to=toNum
    )
    # print(message.sid)



def callGPT(question):
    print('Calling GPT')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.environ.get("OPENAI_API_KEY"),
    }

    json_data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'user',
                'content': question,
            },
        ],
        'temperature': 0.7,
    }

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=json_data)
    return(response.text)


if __name__ == '__main__':
    app.run(debug=True)