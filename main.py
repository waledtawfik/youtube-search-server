from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

app = Flask(__name__)

def search_youtube(query):
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup.find_all("script"):
        if "var ytInitialData" in script.text:
            start = script.text.find("var ytInitialData") + len("var ytInitialData = ")
            end = script.text.rfind("};") + 1
            json_str = script.text[start:end]
            break
    else:
        return None

    try:
        data = json.loads(json_str)
        videos = data['contents']['twoColumnSearchResultsRenderer']['primaryContents'] \
                     ['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
        
        for video in videos:
            if "videoRenderer" in video:
                vid = video["videoRenderer"]
                video_id = vid["videoId"]
                title = vid["title"]["runs"][0]["text"]
                thumbnail = vid["thumbnail"]["thumbnails"][-1]["url"]
                url = f"https://www.youtube.com/watch?v={video_id}"
                return {"title": title, "url": url, "thumbnail": thumbnail}
    except:
        return None

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    result = search_youtube(query)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "No video found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
