import os
import urllib.request
import json
from datetime import datetime

# GitHub GraphQL API URL
URL = "https://api.github.com/graphql"

def get_stats():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not found in environment!")
        return None
        
    username = "Imkumar80"
    current_year = datetime.now().year
    
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          totalPullRequestContributions
          totalIssueContributions
          totalRepositoryContributions
          restrictedContributionsCount
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    
    variables = {
        "username": username,
        "from": f"{current_year}-01-01T00:00:00Z",
        "to": f"{current_year}-12-31T23:59:59Z"
    }
    
    req_data = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    
    req = urllib.request.Request(
        URL,
        data=req_data,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "StatsUpdater"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "errors" in res_data:
                print("GraphQL errors:", res_data["errors"])
                return None
            return res_data["data"]["user"]["contributionsCollection"]
    except Exception as e:
        print("Error fetching stats:", e)
        return None

def update_svg(stats):
    if not stats:
        print("No stats data available to write.")
        return
        
    current_year = datetime.now().year
    total = stats["contributionCalendar"]["totalContributions"]
    commits = stats["totalCommitContributions"]
    prs = stats["totalPullRequestContributions"]
    issues = stats["totalIssueContributions"]
    private = stats["restrictedContributionsCount"]
    
    template_path = "assets/gh-stats.template.svg"
    svg_path = "assets/gh-stats.svg"
    
    # Ensure paths are correct relative to workspace
    # If run from root, we find them directly, else we look up
    if not os.path.exists(template_path):
        # try relative to script
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, "assets", "gh-stats.template.svg")
        svg_path = os.path.join(base_dir, "assets", "gh-stats.svg")
        
    if not os.path.exists(template_path):
        print(f"Template file {template_path} not found!")
        return
        
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    content = content.replace("{{YEAR}}", str(current_year))
    content = content.replace("{{TOTAL_CONTRIBS}}", str(total))
    content = content.replace("{{COMMITS}}", str(commits))
    content = content.replace("{{PRS}}", str(prs))
    content = content.replace("{{ISSUES}}", str(issues))
    content = content.replace("{{PRIVATE}}", str(private))
    
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Successfully updated {svg_path} with: Total={total}, Commits={commits}, PRs={prs}, Issues={issues}, Private={private}")

if __name__ == "__main__":
    stats = get_stats()
    update_svg(stats)
