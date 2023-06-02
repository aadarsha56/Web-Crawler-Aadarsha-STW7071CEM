import pandas as pd
from flask import Flask, render_template, request
import time
import json
import nltk.stem as stemmer
import pickle
import schedule
from scrapAuthors import scrapeAuthors
from scrapPapers import scrapPapers
import re
app = Flask(__name__)

def loadJson(x):
    if x is not None:
        return json.loads(x)
    return []

def reScrape():
    scrapPapers()
    scrapeAuthors()

def scheduleNextScrape():
    # Schedule the next scrape after 1 week
    schedule.every(1).weeks.do(reScrape)

    # Write the scheduled time to a persistent storage (e.g., a file)
    next_scrape_time = schedule.next_run().strftime("%Y-%m-%d %H:%M:%S")
    with open("last_scrape.txt", "w") as file:
        file.write(next_scrape_time)

# Load the last scrape time from the persistent storage
def loadLastScrapeTime():
    try:
        with open("last_scrape.txt", "r") as file:
            last_scrape_time = file.read().strip()
            return last_scrape_time
    except FileNotFoundError:
        return None

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