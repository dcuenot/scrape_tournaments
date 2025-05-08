import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from pprint import pprint

def scrape_tournaments():
    url = "https://apiv2.fftt.com/api/tournament_requests"
    
    # Calculate dates
    today = datetime.now()
    six_months_later = today + timedelta(days=180)  # approximately 6 months
    
    params = {
        "page": 1,
        "itemsPerPage": 200,
        "order[startDate]": "asc",
        "startDate[after]": today.strftime("%Y-%m-%dT00:00:00"),
        "endDate[before]": six_months_later.strftime("%Y-%m-%dT00:00:00")
    }
    
    headers = {
        'Referer': 'https://monclub.fftt.com/'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract tournament data
        tournaments = []
        for tournament in data.get('hydra:member', []):
            tournament_data = {
                'id': tournament.get('id'),
                'name': tournament.get('name'),
                'startDate': tournament.get('startDate'),
                'endDate': tournament.get('endDate'),
                'type': tournament.get('type'),
                'postalCode': tournament.get('address').get('postalCode'),
                'location': tournament.get('address').get('addressLocality'),
                'rules': tournament.get('rules').get('url') if tournament.get('rules') is not None else ''
            }
            tournaments.append(tournament_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(tournaments)
        
        # Save to CSV
        df.to_csv('tournois.csv', index=False)
        print(f"Successfully saved {len(tournaments)} tournaments to tournois.csv")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    scrape_tournaments() 