import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import warnings
from datetime import datetime
import cloudscraper

warnings.simplefilter(action='ignore')

class PingPocketQuery(object):

    CLUB = '08940073'  # USFTT 08940073 / Longvic: 02210081
    ONLINE = True
    SCRAPER = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )

    @staticmethod
    def run():
        if PingPocketQuery.ONLINE:
            df_joueurs = PingPocketQuery._get_joueurs_classements()
            df_joueurs.to_csv('out.csv') 
        else:
            df_joueurs = pd.read_csv('out.csv', index_col=0)

        df_competiteurs = df_joueurs[df_joueurs['typeLicence'] == 'C']
        df_competiteurs.loc[df_competiteurs["progressionMensuelle"] == "x", "progressionMensuelle"] = 0
        df_competiteurs.loc[df_competiteurs["progressionGenerale"] == "x", "progressionGenerale"] = 0
        df_competiteurs[['progressionMensuelle', 'progressionGenerale']] = df_competiteurs[['progressionMensuelle', 'progressionGenerale']].apply(pd.to_numeric)
        df_competiteurs.sort_values(by=['progressionMensuelle'], inplace=True, ascending=False)
        
        # All
        all_h = PingPocketQuery._filter_by_categorie(df_competiteurs, '', 'H')
        all_f = PingPocketQuery._filter_by_categorie(df_competiteurs, '', 'F')

        # Poussin
        poussin_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Poussin', 'H')
        poussin_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Poussin', 'F')

        # Benjamin
        benjamin_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Benjamin', 'H')
        benjamin_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Benjamin', 'F')

        # Minime
        minime_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Minime', 'H')
        minime_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Minime', 'F')

        # Cadet
        cadet_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Cadet', 'H')
        cadet_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Cadet', 'F')

        # Junior
        junior_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Junior', 'H')
        junior_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Junior', 'F')

        # Senior H
        senior_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Sénior', 'H')
        senior_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Sénior', 'F')

        # Vétéran
        veteran_h = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Vétéran', 'H')
        veteran_f = PingPocketQuery._filter_by_categorie(df_competiteurs, 'Vétéran', 'F')
        
        with pd.ExcelWriter('progressionMensuelle.xlsx') as writer:
            all_f.to_excel(writer, sheet_name='All F')
            all_h.to_excel(writer, sheet_name='All H')
            
            poussin_f.to_excel(writer, sheet_name='Poussin F')
            poussin_h.to_excel(writer, sheet_name='Poussin H')
            benjamin_f.to_excel(writer, sheet_name='Benjamin F')
            benjamin_h.to_excel(writer, sheet_name='Benjamin H')
            minime_f.to_excel(writer, sheet_name='Minime F')
            minime_h.to_excel(writer, sheet_name='Minime H')
            cadet_f.to_excel(writer, sheet_name='Cadet F')
            cadet_h.to_excel(writer, sheet_name='Cadet H')
            junior_f.to_excel(writer, sheet_name='Junior F')
            junior_h.to_excel(writer, sheet_name='Junior H')
            senior_f.to_excel(writer, sheet_name='Senior F')
            senior_h.to_excel(writer, sheet_name='Senior H')
            veteran_f.to_excel(writer, sheet_name='Veteran F')
            veteran_h.to_excel(writer, sheet_name='Veteran H')

    @staticmethod
    def get_publication_date():
        """
        Get the publication date for non-premium users from the FFTT website.
        Returns the date as a string in the format 'DD Month' (e.g., '13 Mai').
        """
        # Mapping of months to column indices (0-based)
        MONTH_TO_COLUMN = {
            1: 4,   # Janvier -> 5ème colonne
            2: 5,   # Février -> 6ème colonne
            3: 6,   # Mars -> 7ème colonne
            4: 7,   # Avril -> 8ème colonne
            5: 8,   # Mai -> 9ème colonne
            6: 9,   # Juin -> 10ème colonne
            7: 10,  # Juillet -> 11ème colonne
            8: 11,  # Août -> 12ème colonne
            9: 12,  # Septembre -> 13ème colonne
            10: 1,  # Octobre -> 2ème colonne
            11: 2,  # Novembre -> 3ème colonne
            12: 3   # Décembre -> 4ème colonne
        }
        
        # Get the webpage content
        url = 'https://www.fftt.com/site/articles/calendrier-publications'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table with publication dates
        table = soup.find('table')
        if table:
            # Get current month
            current_month = datetime.now().month
            
            # Find all rows in the table
            rows = table.find_all('tr')
            for row in rows:
                # Look for the row containing 'Non Premium'
                if 'Non Premium' in row.text:
                    # Get all cells in this row
                    cells = row.find_all('th')
                    # Get the column index for current month
                    column_index = MONTH_TO_COLUMN.get(current_month)
                    if column_index is not None and len(cells) > column_index:
                        date_cell = cells[column_index]
                        if date_cell:
                            date_text = date_cell.text.strip()
                            # Extract just the number (e.g., '13 Mai' -> '13')
                            date_text = date_text.split()[0].strip()
                            # Format day with 2 digits (e.g., '5' -> '05')
                            date_text = date_text.zfill(2)
                            # Convert month to string and format with 2 digits
                            current_month = str(current_month).zfill(2)
                            return f"{datetime.now().year}-{current_month}-{date_text}"
        return None
    
    @staticmethod
    def _filter_by_categorie(df, categorie, sex):
        print()
        print('***** ' + categorie + ' - ' + sex)

        df_out = df[(df['categorie'].str.contains(categorie)) & (df['sex'] == sex)]
        df_out.drop(columns=['typeLicence', 'sex'], inplace=True)
        print(df_out[['name', 'pointsDebutPhase', 'pointsMensuels', 'progressionMensuelle', 'progressionGenerale']].head(10).to_string(index=False))

        return df_out


    @staticmethod
    def _get_joueurs_classements():
        joueurs = []
        for licence in PingPocketQuery._get_list_licences():
            detail = PingPocketQuery._get_licence_details(licence['id'], licence['sex'])
            if detail:  # Only add if we successfully got the details
                joueurs.append(detail)
            time.sleep(2)

        if not joueurs:
            print("No valid player data found")
            return pd.DataFrame()

        df_joueurs = pd.DataFrame.from_dict(joueurs)
        df_joueurs.set_index('licence', inplace=True)

        return df_joueurs

    @staticmethod
    def _get_list_licences():
        soup = PingPocketQuery._api_call('clubs/'+ PingPocketQuery.CLUB +'/licencies?SORT=CATEGORY')
        innerContent = soup.find('ul', class_="edgetoedge")
        
        res = []
        for link in innerContent.findAll('a'):
            match = re.search(r'licencies/(\d+)', link['href'])
            res.append({
                'id': match.group(1),
                'sex': link.find('div', class_='icon').find('i')['class'][1][3:]
            })

        return res
    

    @staticmethod
    def _get_licence_details(licenceId, sex):
        soup = PingPocketQuery._api_call('licencies/'+licenceId+'?CLUB_ID='+PingPocketQuery.CLUB)
        if not soup:
            print(f"Failed to get details for licence {licenceId}")
            return None

        try:
            name = soup.find('h1').text.strip()
            spans = soup.find('div', class_='info border').findAll('span')

            categorie = spans[0].text.strip()
            typeLicence = spans[4].text.strip()

            innerContent = soup.find('ul', class_="rounded").findAll('li')
            
            # Helper function to safely get text from small tag
            def get_safe_text(element, index):
                if element and len(element) > index:
                    small = element[index].find('small')
                    return small.text.strip() if small else None
                return None

            pointsMensuels = get_safe_text(innerContent, 1)
            pointsDebutPhase = get_safe_text(innerContent, 2)
            progressionMensuelle = get_safe_text(innerContent, 3)
            progressionGenerale = get_safe_text(innerContent, 4)

            return {
                'licence': licenceId,
                'typeLicence': typeLicence,
                'sex': 'F' if sex == 'female' else 'H',
                'name': name,
                'categorie': categorie,
                'pointsDebutPhase': pointsDebutPhase,
                'pointsMensuels': pointsMensuels,
                'progressionMensuelle': progressionMensuelle,
                'progressionGenerale': progressionGenerale
            }
        except Exception as e:
            print(f"Error processing licence {licenceId}: {str(e)}")
            return None
            

    @staticmethod
    def _api_call(url, max_retries=3, initial_delay=1):
        print(f"Calling API: {url}")
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.pingpocket.fr/app/fftt/"
        }
        print(f"Using headers: {headers}")
        
        for attempt in range(max_retries):
            try:
                
                response = PingPocketQuery.SCRAPER.get('https://www.pingpocket.fr/app/fftt/' + url, 
                                  headers=headers)
                
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {response.headers}")
                
                if response.status_code == 200:
                    return BeautifulSoup(response.text, 'html.parser')
                else:
                    print(f"Erreur lors de la récupération de la page : {response.status_code}")
                    print(f"Response content: {response.text}")
                    
                    if attempt < max_retries - 1:
                        delay = initial_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        print("Max retries reached. Giving up.")
                        return None
                        
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Giving up.")
                    return None


if __name__ == '__main__':
    PingPocketQuery().run()