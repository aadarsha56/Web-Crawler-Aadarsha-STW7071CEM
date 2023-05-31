import requests
from bs4 import BeautifulSoup
import csv
import time
import json
import re

def getProfileURLorNone(url):
    if "no-content" in url:
        return None
    pattern = r"^(\/[^?]+)"
    path_match = re.match(pattern, url)
    path = None
    if path_match:
        path = path_match.group(1)
    return path    
# function to scrape coventry persons page
def scrapeAuthors(start_page = 1, page_limit = 1000):
    page = start_page
    url = f"https://pureportal.coventry.ac.uk/en/persons/?format=&page={page}"
    authors = []
    while page < page_limit:
        try:
            pageSource = requests.get(url).text
            soup = BeautifulSoup(pageSource, "html.parser")
            authorList = soup.select("li.grid-result-item div.result-container")
            if len(authorList) == 0:
                break
            for author in authorList:
                try:
                    authorInfo = {}
                    authorInfo['picUrl'] = getProfileURLorNone(
                            author.select_one("img")['src']
                    )
                    if authorInfo['picUrl'] is not None:
                        authorInfo['picUrl'] = 'https://pureportal.coventry.ac.uk/' + authorInfo['picUrl'] 
                    name = author.select_one("a", attrs = { 'rel' : 'Person'})
                    authorInfo['name'] = name.text
                    authorInfo['profileLink'] = name['href']
                    dept = author.select_one(".relations.organisations a", 
                            attrs = { 'rel' : 'Organisation'})
                    authorInfo['department'] = dept.text
                    authorInfo['deptLink'] = dept['href']
                    authors.append(authorInfo)
                except:
                    pass
            print(f"Finished {page} ")
            page += 1
            url = f"https://pureportal.coventry.ac.uk/en/persons/?format=&page={page}"
        except: 
            break
    with open(f"./scrapedData/authors-{time.ctime()}.json", "w") as f:
        f.write(json.dumps(authors))
    return authors

if __name__ == '__main__':
    scrapeAuthors()