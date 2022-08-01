import json
from pprint import pprint
import random

from flask import Flask


app = Flask(__name__)

def make_url(title, link):
    return f"""<a href="{link}">{title}</a>"""

with open('./wiki.json') as f:
    ALL_RESULTS = json.loads(f.read())['articles']
with open('index.html') as f:
    ONE_PAGE = f.read()
ABOUT = f"""<small>
The {make_url("list of unusual articles", "https://en.wikipedia.org/wiki/Wikipedia:Unusual_articles")} on Wikipedia
    contains over <i>two thousand</i> entries on fascinating places, objects and individuals, but the layout does
    not help with aimless discovery.<br><br>

    This page showcases many of these, as well as some I've stumbled across along the way—which I should probably
    add to the wiki.
    </small>
"""

LEN_ARTICLES = len(ALL_RESULTS)
print(f"Serving {LEN_ARTICLES} articles...")




@app.route('/')
def hello():
    n = random.randint(0, LEN_ARTICLES-1)
    title = ALL_RESULTS[n]['title']
    desc = ALL_RESULTS[n]['desc']
    url = ALL_RESULTS[n]['url']
    return (ONE_PAGE
        .replace('%%HEADING%%', make_url(title, url))
        .replace('%%DESC%%', desc))


@app.route('/about')
def about():
    return (
        ONE_PAGE
            .replace('%%HEADING%%', "About")
            .replace('%%DESC%%', ABOUT)
            .replace("Articles on Wikipedia</h2>", f"Articles on Wikipedia<br>// Made by {make_url('nk412', 'https://nk412.github.io')}</h2>")
            .replace("another!", "one!")
    )