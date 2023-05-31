import pandas as pd
from flask import Flask, render_template, request
import time
import json
import re

app = Flask(__name__)

def loadJson(x):
    if x is not None:
        return json.loads(x)
    return []

def reScrape():
    # TO-DO: rescrape after a certain time
    pass

def loadData():
    start = time.time()
    papers = pd.read_json("./scrapedData/papers.json")
    authors = pd.read_json("./scrapedData/authors.json")

    print(f"Loaded files in {time.time() - start} seconds")
    return papers, authors

PAPERS, AUTHORS = loadData()

@app.route('/')
def home():
    return render_template('index.html')


def search_papers(query):
    pattern = r'(?i){}'.format(re.escape(query))
    filtered_papers = []

    # main search handler
    for index, row in PAPERS.iterrows():
        try:
            if len(row['coventryAuthors']) == 0: 
                continue
            
            if re.search(pattern, row['title'], flags=re.IGNORECASE):
                filtered_papers.append(row)
                continue
            if isinstance(row['tags'], list):
                if any(re.search(pattern, tag, flags=re.IGNORECASE) for tag in row['tags']):
                    filtered_papers.append(row)
                    continue

            if isinstance(row['authors'], list):
                if any(re.search(pattern, author, flags=re.IGNORECASE) for author in row['authors']):
                    filtered_papers.append(row)
        except:
            pass

    papers = pd.DataFrame(filtered_papers)
    return papers.to_dict('records')


@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')  # Get the search query from the form
    matchingPapers = search_papers(query)  # Call the function to search for papers
    return render_template('results.html', papers=matchingPapers, query=query)


if __name__ == '__main__':
    app.run(debug=True)