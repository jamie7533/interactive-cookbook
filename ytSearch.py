from youtube_search import YoutubeSearch
import requests
from bs4 import BeautifulSoup

#returns link for first result of searched input
def search_youtube(searchStr: str) -> str:
    results = YoutubeSearch(searchStr, max_results=1).to_dict()
    link = "https://youtube.com"+results[0]['url_suffix']
    return link

#returns link for first result of searched input
def search_google(query: str) -> str:
    query = query.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}&num=1"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    link = soup.find('div', {"class": "egMi0 kCrYT"}).a['href']
    link = link.split("&")[0]
    link = link.split("=")[1]
    return link


