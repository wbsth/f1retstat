import requests
import json
import os
from misc import build_season_list


def download_season_list(api_address):
    """gets season list from API, and saves it locally to JSON. Returns file name"""
    r = requests.get(api_address)
    file_name = 'seasons.json'
    with open(file_name, 'wb') as f:
        f.write(r.content)
    print("Season list downloaded")
    return file_name


def download_race_list(api_address, season_list):
    """getting race list in every season"""
    for year in season_list:
        print(f"Downloading {year} race list")
        # getting year json from API
        r = requests.get(f"{api_address}/{year}.json")

        # creating directory
        directory = f"season/{year}"
        os.makedirs(directory, exist_ok=True)

        # writing file
        with open(f'{directory}/{year}.json', 'wb') as f:
            f.write(r.content)


def download_race_results(season_list):
    """saving race result from every season to json"""
    for i in season_list:
        print(f"Downloading races results from {i}")
        url = f'season/{i}'
        with open(f"{url}/{i}.json", encoding='utf-8') as f:
            data = json.load(f)
            for j in data['MRData']['RaceTable']['Races']:
                race_url = f"http://ergast.com/api/f1/{i}/{j['round']}/results.json?limit=60"
                r = requests.get(race_url)
                with open(f"{url}/{j['round']}.json", 'wb') as g:
                    g.write(r.content)


def main():
    # getting data downloaded
    seasons_filename = download_season_list('http://ergast.com/api/f1/seasons.json?limit=100')
    season_years = build_season_list(seasons_filename)
    download_race_list('http://ergast.com/api/f1', season_years)
    download_race_results(season_years)


if __name__ == '__main__':
    main()
