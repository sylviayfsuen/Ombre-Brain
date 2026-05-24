import os
import base64
import json
import tarfile
import tempfile
from datetime import datetime
import urllib.request
import urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_BACKUP_TOKEN", "")
GITHUB_REPO = "sylviayfsuen/ombre-brain-backup"
BUCKETS_DIR = "/app/buckets"

def github_api(method, path, data=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())

def backup():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.tar.gz"

    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = os.path.join(tmpdir, filename)
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(BUCKETS_DIR, arcname="buckets")

        with open(archive_path, "rb") as f:
            content = base64.b64encode(f.read()).decode()

    existing = github_api("GET", f"contents/{filename}")
    sha = existing.get("sha") if "sha" in existing else None

    payload = {
        "message": f"backup {timestamp}",
        "content": content,
    }
    if sha:
        payload["sha"] = sha

    result = github_api("PUT", f"contents/{filename}", payload)
    if "content" in result:
        print(f"备份成功: {filename}")
    else:
        print(f"备份失败: {result}")

if __name__ == "__main__":
    backup()
