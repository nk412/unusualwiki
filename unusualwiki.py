import json
from pprint import pprint
import random

from flask import Flask


app = Flask(__name__)

with open('./wiki.json') as f:
    all_results = json.loads(f.read())['articles']
with open('index.html') as f:
    page = f.read()

LEN_ARTICLES = len(all_results)
print(f"Serving {LEN_ARTICLES} articles...")


def make_url(title, link):
    return f"""<a href="{link}">{title}</a>"""

@app.route('/')
def hello():
    n = random.randint(0, LEN_ARTICLES-1)
    title = all_results[n]['title']
    desc = all_results[n]['desc']
    url = all_results[n]['url']
    return (page
        .replace('%%HEADING%%', make_url(title, url))
        .replace('%%DESC%%', desc))
