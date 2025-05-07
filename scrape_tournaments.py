import requests
import pandas as pd
from datetime import datetime
import os

def scrape_tournaments():
    url = "https://monclub.fftt.com/tournaments/search"
    params = {
        "page": 1,
        "itemsPerPage": 25,
        "order[startDate]": "asc",
        "startDate[after]": "2025-05-07T23:59:32",
        "endDate[before]": "2025-12-31T23:59:59"
    }
    
    try:
        response = requests.get(url, params=params)
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