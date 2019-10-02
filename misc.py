import json
import pandas as pd

def import_race_statuses(file_adr):
    """imports possible race finish statuses"""
    statuses_csv = pd.read_csv(file_adr, sep=";")
    print('Race statuses imported')
    return statuses_csv


def build_season_list(file_name):
    """from season list, returns list of season years"""
    with open(file_name, 'r', encoding='utf-8') as f:
        season_years = []
        seasons_data = json.load(f)
        for i in seasons_data['MRData']['SeasonTable']['Seasons']:
            season_years.append(int(i['season']))
    return season_years


def build_dataframe():
    """builds dataframe skeleton"""
    column_names = ['year', 'race', 'country', 'track', 'date', 'started', 'retired_overall', 'retired_mech',
                    'retired_accident',
                    'retired_misc']
    df = pd.DataFrame(columns=column_names)
    df = df.astype({'year': int, 'race': int, 'country': object, 'track': object, 'date': object, 'started': int,
                    'retired_overall': int,
                    'retired_mech': int, 'retired_accident': int, 'retired_misc': int})
    return df


def fill_dataframe(df, season_list, statuses):
    """fills the dataframe with data loaded from json files"""
    for i in season_list:
        # iterating through seasons
        url = f'season/{i}'
        with open(f"{url}/{i}.json", encoding='utf-8') as f:
            data = json.load(f)
            for j in range(1, len(data['MRData']['RaceTable']['Races'])):
                # iterating through races in particular season
                with open(f"{url}/{j}.json", encoding='utf-8') as g:
                    race_result_data = json.load(g)['MRData']['RaceTable']
                    race_df = pd.DataFrame(columns=df.columns)
                    try:
                        # assigning text values to race dataframe
                        started = 0  # number of drivers who started race
                        finished = 0  # numb of driver who finished race
                        ret_mech = 0  # number of drivers who retired by mechanical failure
                        ret_acc = 0  # number of drivers who retired due to accident
                        ret_dnf = 0  # number of drivers who retired due to other reasons
                        dns = 0  # number of drivers who did not start the race
                        for k in race_result_data['Races'][0]['Results']:
                            status = k['status']
                            if status in statuses['finish'].values:
                                started += 1
                                finished += 1
                            elif status in statuses['mech'].values:
                                started += 1
                                ret_mech += 1
                            elif status in statuses['acc'].values:
                                started += 1
                                ret_acc += 1
                            elif status in statuses['dnf'].values:
                                started += 1
                                ret_dnf += 1
                            elif status in statuses['dns'].values:
                                dns += 1

                        ret_ov = ret_mech + ret_acc + ret_dnf

                        race_df.loc[0, 'year'] = race_result_data['season']
                        race_df.loc[0, 'race'] = race_result_data['Races'][0]['round']
                        race_df.loc[0, 'country'] = race_result_data['Races'][0]['raceName']
                        race_df.loc[0, 'track'] = race_result_data['Races'][0]['Circuit']['circuitName']
                        race_df.loc[0, 'date'] = race_result_data['Races'][0]['date']
                        race_df.loc[0, 'started'] = started
                        race_df.loc[0, 'retired_overall'] = ret_ov
                        race_df.loc[0, 'retired_mech'] = ret_mech
                        race_df.loc[0, 'retired_accident'] = ret_acc
                        race_df.loc[0, 'retired_misc'] = ret_dnf

                        df = pd.concat([df, race_df], ignore_index=True)
                    except IndexError:
                        pass
    return df


def print_df(dataframe):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(dataframe)