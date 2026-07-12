import os
import sys
import json
import requests
import datetime

def fetch_contributions(username, token):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                color
              }
            }
          }
        }
      }
    }
    """
    
    variables = {"userName": username}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code} - {response.text}")
        sys.exit(1)
        
    data = response.json()
    if "errors" in data:
        print(f"GraphQL Errors: {data['errors']}")
        sys.exit(1)
        
    return data

def generate_mock_data():
    """Generates mock data for local testing when GITHUB_TOKEN is not available."""
    print("WARNING: GITHUB_TOKEN not found. Generating mock contribution data.")
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    
    # Adjust start_date to the nearest Sunday to match GitHub's 53-week layout
    while start_date.weekday() != 6:  # 6 is Sunday
        start_date -= datetime.timedelta(days=1)
        
    weeks = []
    current_date = start_date
    import random
    
    colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
    total = 0
    
    for _ in range(53):
        days = []
        for _ in range(7):
            if current_date > today:
                break
            count = random.choices([0, 2, 5, 10, 20], weights=[0.6, 0.2, 0.1, 0.05, 0.05])[0]
            total += count
            if count == 0: color = colors[0]
            elif count <= 3: color = colors[1]
            elif count <= 6: color = colors[2]
            elif count <= 12: color = colors[3]
            else: color = colors[4]
            
            days.append({
                "contributionCount": count,
                "date": current_date.isoformat(),
                "color": color
            })
            current_date += datetime.timedelta(days=1)
        weeks.append({"contributionDays": days})
        if current_date > today:
            break
            
    return {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": total,
                        "weeks": weeks
                    }
                }
            }
        }
    }

def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    username = "navdeep-r"
    
    if token:
        print(f"Fetching contributions for {username}...")
        data = fetch_contributions(username, token)
    else:
        data = generate_mock_data()
        
    # Ensure data directory exists
    here = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(here, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    out_path = os.path.join(data_dir, "contributions.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Successfully saved contributions to {out_path}")

if __name__ == "__main__":
    main()
