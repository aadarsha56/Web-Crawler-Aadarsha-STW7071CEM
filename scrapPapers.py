import requests
from bs4 import BeautifulSoup
import json
import time

def getAuthorsAndOtherDocumentInformation(paperInfo):
    source = requests.get(paperInfo['link']).text
    paperSoup = BeautifulSoup(source, "html.parser")
    if paperSoup.select_one("div.doi a") is not None:
        paperInfo['doi'] = paperSoup.select_one("div.doi a")['href']
    persons = paperSoup.select_one("p.relations.persons")
    if persons is not None:
        paperInfo['authors'] = list(map(
                lambda x : x.strip(), 
                persons.text.split(','))
            )
    paperInfo['tags'] = [span.text for span in 
            paperSoup.select("li.userdefined-keyword")]
    paperInfo['coventryAuthors'] = [a['href'] for a in 
            persons.select('a', attrs = { 'rel' : 'Person'})]
    abstract = paperSoup.select_one(".rendering_researchoutput_abstractportal")
    paperInfo['abstract'] = None
    if abstract:
        paperInfo['abstract'] = abstract.text
# function to scrape coventry publications page
def scrapPapers(start_page = 1, page_limit = 1000):

    page = start_page
    url = f"https://pureportal.coventry.ac.uk/en/publications/?format=&page={page}"
    papers = []
    while page < page_limit:
        try:
            pageSource = requests.get(url).text
            soup = BeautifulSoup(pageSource, "html.parser")
            paperLists = soup.select(".list-result-item")
            if len(paperLists) == 0:
                break
            for paper in paperLists:
                paperInfo = {}
                paperInfo['link'] = paper.select_one('h3.title a')['href']
                paperInfo['title'] = paper.select_one('h3.title a').text
                journal = paper.select_one('a', attrs = {'rel' : 'Journal'})
                paperInfo['journal'] = journal.text
                paperInfo['journalLink'] = journal['href']
                cols = ['date', 'volume', 'pages', 'numberofpages', 'type_classification']
                for x in cols:
                    try:
                        paperInfo[x] = paper.select_one(f'span.{x}').text
                        if x == 'numberofpages':
                            paperInfo[x] = int(paperInfo[x][:-2])
                        elif x == 'pages':
                            paperInfo[x] = paperInfo[x][3:]
                        elif x == 'volume':
                            paperInfo[x] = int(paperInfo[x])
                    except:
                        pass
                getAuthorsAndOtherDocumentInformation(paperInfo)
                papers.append(paperInfo)
            print(f"Finished {page} ")
            page += 1
            url = f"https://pureportal.coventry.ac.uk/en/publications/?format=&page={page}"
        except: 
            break
    with open(f"./scrapedData/papers-{time.ctime()}.json", "w") as f:
        f.write(json.dumps(papers))
    return papers

if __name__ == '__main__':
    scrapeAuthors()