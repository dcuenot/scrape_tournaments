import requests
import pandas as pd
from datetime import datetime
import os
from pprint import pprint

def scrape_tournaments():
    url = "https://apiv2.fftt.com/api/tournament_requests"
    params = {
        "page": 1,
        "itemsPerPage": 200,
        "order[startDate]": "asc",
        "startDate[after]": "2025-05-07T00:00:00",
        "endDate[before]": "2025-12-31T00:00:00"
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
                'location': tournament.get('location'),
                'category': tournament.get('category'),
                'status': tournament.get('status')
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