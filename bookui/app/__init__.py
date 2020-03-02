from flask import Flask

app = Flask(__name__)
book = [
    {
        'title': "Dummy Chapter",
        'content': ["This is a <phrase> dummy</phrase> chapter. "*50]
    },
    {
        'title': 'I didn\'t mean to call you a dummy',
        'content': ["I "+ "really"*i + " didn't. Please believe <phrase>me</phrase>. Please " + ' Please'*50 for i in range(5)]
    }
]
from bookui.app import routes

