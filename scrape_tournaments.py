import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from pprint import pprint
import sys
import googlemaps

# Configuration
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

def calculate_distance_from_fontenay(destination):
    try:
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        
        # Get distance matrix
        result = gmaps.distance_matrix("Fontenay-sous-bois, 94120, France", destination, mode="driving")
        
        # Extract duration and distance
        if result['status'] == 'OK':
            element = result['rows'][0]['elements'][0]
            if element['status'] == 'OK':
                duration = element['duration']['text']
                distance = element['distance']['text']
                return f"{distance} ({duration})"
    except Exception as e:
        print(f"Error calculating distance: {e}")
    return "Distance non disponible"

def scrape_tournaments():
    url = "https://apiv2.fftt.com/api/tournament_requests"
    
    # Calculate dates
    today = datetime.now()
    six_months_later = today + timedelta(days=180)  # exactly 6 months
    
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
                'name': tournament.get('name').replace(',', ''),
                'startDate': tournament.get('startDate'),
                'endDate': tournament.get('endDate'),
                'type': tournament.get('type'),
                'postalCode': tournament.get('address').get('postalCode'),
                'location': tournament.get('address').get('addressLocality'),
                'rules': tournament.get('rules').get('url') if tournament.get('rules') is not None else '',
                'distance': ''  # Initialize empty distance
            }
            tournaments.append(tournament_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(tournaments)
        
        # Check for existing tournaments
        new_tournaments = []
        if os.path.exists('csv/tournois.csv'):
            existing_df = pd.read_csv('csv/tournois.csv')
            existing_ids = set(existing_df['id'])
            new_tournaments = df[~df['id'].isin(existing_ids)]
            
            # Calculate distances only for new tournaments
            if len(new_tournaments) > 0:
                # Add distance information to new tournaments
                new_tournaments['distance'] = new_tournaments.apply(
                    lambda row: calculate_distance_from_fontenay(
                        f"{row['location']}, {row['postalCode']}, France"
                    ),
                    axis=1
                )
                
                # Save new tournaments to a separate file
                new_tournaments.to_csv('csv/new_tournaments.csv', index=False)
                print(f"Found {len(new_tournaments)} new tournaments")
                
                # Update distances in the main DataFrame
                df.loc[new_tournaments.index, 'distance'] = new_tournaments['distance']
        
        # Save all tournaments
        df.to_csv('csv/tournois.csv', index=False)
        print(f"Successfully saved {len(tournaments)} tournaments to tournois.csv")
        
        # Return 2 if new tournaments were found, 0 otherwise
        exit_code = 2 if len(new_tournaments) > 0 else 0
        print(f"Exiting with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)  # Exit with error code 1

if __name__ == "__main__":
    sys.exit(scrape_tournaments())  # Exit with the return code from scrape_tournaments 