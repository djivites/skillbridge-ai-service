import requests
from pprint import pprint
import isodate
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def format_duration(duration):   
    return str(isodate.parse_duration(duration))
# ==============================
# 🎥 YOUTUBE FETCH
# ==============================
def get_youtube_videos(skill):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet",
        "q": skill,
        "key": YOUTUBE_API_KEY,
        "maxResults": 3,
        "type": "video"
    }

    try:
        res = requests.get(search_url, params=params)



        if res.status_code != 200:
            return {"error": f"YouTube HTTP {res.status_code}"}

        data = res.json()

        if "error" in data:
            return {"error": data["error"]["message"]}

        items = data.get("items", [])
        if not items:
            return []

        video_ids = [item["id"]["videoId"] for item in items]

        # Fetch duration
        params2 = {
            "part": "contentDetails",
            "id": ",".join(video_ids),
            "key": YOUTUBE_API_KEY
        }

        res2 = requests.get(video_url, params=params2)
        data2 = res2.json()

        videos = []
        for item, detail in zip(items, data2.get("items", [])):
            video_id = item["id"]["videoId"]
            videos.append({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": format_duration(detail["contentDetails"]["duration"])
                  })

        return videos

    except Exception as e:
        return {"error": str(e)}


# ==============================
#  GITHUB FETCH
# ==============================
def get_github_repos(skill):
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    search_url = "https://api.github.com/search/repositories"

    params = {
        "q": f"{skill} roadmap",
        "sort": "stars",
        "order": "desc",
        "per_page": 3
    }

    try:
        res = requests.get(search_url, headers=headers, params=params)

        data = res.json()

        if "items" not in data:
            return {"error": data}

        repos_data = []

        for repo in data["items"]:
            repo_name = repo["full_name"]

            # Fetch workflows
            workflow_url = f"https://api.github.com/repos/{repo_name}/actions/workflows"
            wf_res = requests.get(workflow_url, headers=headers).json()

            workflows = []
            if "workflows" in wf_res:
                for wf in wf_res["workflows"]:
                    workflows.append(wf["name"])

            repos_data.append({
                "workflows": workflows if workflows else []
                  })

        return repos_data

    except Exception as e:
        return {"error": str(e)}


# ==============================
#  WIKIPEDIA FULL CONTENT
# ==============================
def get_wikipedia_full(skill):
    url = "https://en.wikipedia.org/w/api.php"

    headers = {
        "User-Agent": "SkillBridgeAI/1.0"
    }

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": skill,
        "explaintext": True,
        "redirects": 1
    }

    try:
        res = requests.get(url, headers=headers, params=params)

        if res.status_code != 200:
            return {"error": f"Wiki HTTP {res.status_code}"}

        data = res.json()
        pages = data.get("query", {}).get("pages", {})

        for page_id in pages:
            page = pages[page_id]
            if "extract" in page and page["extract"]:
                return page.get("extract")

        return {"error": "No content found"}

    except Exception as e:
        return {"error": str(e)}


# ==============================
#  MAIN FUNCTION
# ==============================
def fetch_all(skill):
    print(f"\n🔍 Fetching data for: {skill}\n")

    return {
        "youtube": get_youtube_videos(skill),
        "github": get_github_repos(skill),
        "wikipedia": get_wikipedia_full(skill)
    }


# ==============================
# ▶ RUN
# ==============================
if __name__ == "__main__":
    skill = input("Enter skill: ")
    data = fetch_all(skill)

    print("\n===== FINAL OUTPUT =====\n")
    pprint(data)