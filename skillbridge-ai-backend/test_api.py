import requests
import json
try:
    health = requests.get('http://127.0.0.1:8000/health')
    res = requests.post('http://127.0.0.1:8000/generate-roadmap', json={'user_id': 'test_user_from_gui', 'job_id': '003', 'hours_per_day': 2.0})
    data = res.json()
    for skill in data.get('skills', []):
        print("Skill:", skill['skill'])
        print("Summary:", skill['summary'][:100], "...")
        print("---")
except Exception as e:
    print('Failed:', e)
