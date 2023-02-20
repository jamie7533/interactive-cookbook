from youtube_search import YoutubeSearch

#returns link for first result of searched input
def search_youtube(searchStr: str) -> str:
    results = YoutubeSearch(searchStr, max_results=1).to_dict()
    link = "https://youtube.com"+results[0]['url_suffix']
    return link


