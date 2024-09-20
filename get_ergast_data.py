import fastf1
import pandas as pd
import re
import F1_Quali

from fastf1.core import Laps
from fastf1.ergast import Ergast


num_races = [19, 19, 21, 20]

average_grid_positions = { # indexed based on order in the 2024 calendar (Bahrain, Jeddah, ... Abu Dhabi + additionals now (any circuit from 2018 - 2024))
    "VER": {"Bahrain": 5.64, "Jeddah": 5.75, "Australia": 4.13, "Suzuka": 4.38, "China": 8.17, "Miami": 4.33, "Imola": 2.0, "Monaco": 7.78, "Canada": 5.63, "Spain": 3.4, "Austria": 2.92, "Silverstone": 4.0, "Hungary": 5.1, "Spa-Francorchamps": 7.2, "Zandvoort": 1.0, "Monza": 8.78, "Baku": 4.43, "Singapore": 5.57, "Austin": 7.25, "Mexico": 3.25, "Brazil": 3.63, "Las Vegas": 2.0, "Qatar": 4.0, "Abu Dhabi": 3.89, "France": 2.75, "Hockenheim": 3.33, "Russia": 10.71, "Turkey": 2.0, "Portugal": 3.0, "Nürburgring": 3.0},
    "PER": {"Bahrain": 9.21, "Jeddah": 2.5, "Australia": 12.5, "Suzuka": 8.5, "China": 10.0, "Miami": 3.0, "Imola": 6.75, "Monaco": 11.17, "Canada": 12.27, "Spain": 10.0, "Austria": 10.54, "Silverstone": 12.31, "Hungary": 11.57, "Spa-Francorchamps": 6.38, "Zandvoort": 10.67, "Monza": 10.15, "Baku": 5.29, "Singapore": 12.09, "Austin": 9.91, "Mexico": 8.38, "Brazil": 11.25, "Las Vegas": 11.0, "Qatar": 15.5, "Abu Dhabi": 9.15, "France": 8.5, "Hockenheim": 10.8, "Russia": 8.13, "Turkey": 8.0, "Portugal": 4.5, "Nürburgring": 12.33},
    "HAM": {"Bahrain": 3.94, "Jeddah": 7.75, "Australia": 4.06, "Suzuka": 4.14, "China": 5.5, "Miami": 9.0, "Imola": 6.25, "Monaco": 5.47, "Canada": 2.47, "Spain": 4.33, "Austria": 4.23, "Silverstone": 4.05, "Hungary": 3.5, "Spa-Francorchamps": 4.0, "Zandvoort": 6.33, "Monza": 4.65, "Baku": 4.14, "Singapore": 2.93, "Austin": 2.45, "Mexico": 2.88, "Brazil": 5.19, "Las Vegas": 10.0, "Qatar": 2.0, "Abu Dhabi": 2.67, "France": 2.0, "Hockenheim": 7.29, "Russia": 3.25, "Turkey": 6.29, "Portugal": 1.5, "Nürburgring": 4.0},
    "RUS": {"Bahrain": 9.71, "Jeddah": 7.5, "Australia": 8.5, "Suzuka": 10.75, "China": 12.5, "Miami": 8.33, "Imola": 10.5, "Monaco": 10.6, "Canada": 7.75, "Spain": 12.0, "Austria": 10.5, "Silverstone": 11.5, "Hungary": 13.33, "Spa-Francorchamps": 8.33, "Zandvoort": 6.67, "Monza": 10.6, "Baku": 11.75, "Singapore": 13.33, "Austin": 11.75, "Mexico": 11.25, "Brazil": 11.0, "Las Vegas": 3.0, "Qatar": 8.5, "Abu Dhabi": 12.2, "France": 13.33, "Hockenheim": 17.0, "Russia": 11.0, "Turkey": 16.5, "Portugal": 12.5, "Nürburgring": 17},
    "LEC": {"Bahrain": 5.75, "Jeddah": 5.0, "Australia": 7.0, "Suzuka": 5.2, "China": 9.67, "Miami": 3.33, "Imola": 4.0, "Monaco": 2.25, "Canada": 11.2, "Spain": 8.14, "Austria": 7.56, "Silverstone": 5.75, "Hungary": 6.86, "Spa-Francorchamps": 7.43, "Zandvoort": 5.33, "Monza": 6.33, "Baku": 4.8, "Singapore": 4.5, "Austin": 6.0, "Mexico": 5.2, "Brazil": 6.8, "Las Vegas": 1.0, "Qatar": 9.0, "Abu Dhabi": 5.83, "France": 4.75, "Hockenheim": 9.5, "Russia": 9.25, "Turkey": 7.5, "Portugal": 6.0, "Nürburgring": 4.0},
    "SAI": {"Bahrain": 8.64, "Jeddah": 7.33, "Australia": 8.13, "Suzuka": 9.5, "China": 10.5, "Miami": 2.67, "Imola": 7.25, "Monaco": 6.89, "Canada": 11.25, "Spain": 7.0, "Austria": 9.0, "Silverstone": 9.0, "Hungary": 8.1, "Spa-Francorchamps": 10.1, "Zandvoort": 5.0, "Monza": 9.89, "Baku": 9.14, "Singapore": 7.71, "Austin": 8.13, "Mexico": 7.13, "Brazil": 10.63, "Las Vegas": 12.0, "Qatar": 8.5, "Abu Dhabi": 10.33, "France": 9.25, "Hockenheim": 10.0, "Russia": 9.86, "Turkey": 17.0, "Portugal": 6.0, "Nürburgring": 10.0},
    "NOR": {"Bahrain": 10.71, "Jeddah": 10.75, "Australia": 7.0, "Suzuka": 6.0, "China": 9.5, "Miami": 5.0, "Imola": 5.75, "Monaco": 7.2, "Canada": 8.0, "Spain": 7.0, "Austria": 4.75, "Silverstone": 5.57, "Hungary": 4.83, "Spa-Francorchamps": 10.67, "Zandvoort": 7.33, "Monza": 7.4, "Baku": 8.5, "Singapore": 6.33, "Austin": 5.75, "Mexico": 12.75, "Brazil": 6.75, "Las Vegas": 15.0, "Qatar": 7.0, "Abu Dhabi": 5.0, "France": 6.0, "Hockenheim": 19.0, "Russia": 5.33, "Turkey": 10.5, "Portugal": 7.5, "Nürburgring": 8.0},
    "PIA": {"Bahrain": 13.0, "Jeddah": 6.5, "Australia": 10.5, "Suzuka": 4.0, "China": 5.0, "Miami": 12.5, "Imola": 5.0, "Monaco": 6.5, "Canada": 6.0, "Spain": 9.0, "Austria": 10.0, "Silverstone": 4.0, "Hungary": 3.0, "Spa-Francorchamps": 5.0, "Zandvoort": 8.0, "Monza": 7.0, "Baku": 10.0, "Singapore": 17.0, "Austin": 10.0, "Mexico": 7.0, "Brazil": 10.0, "Las Vegas": 18.0, "Qatar": 6.0, "Abu Dhabi": 3.0, "France": 7.94, "Hockenheim": 7.94, "Russia": 7.94, "Turkey": 7.94, "Portugal": 7.94, "Nürburgring": 7.94},
    "ALO": {"Bahrain": 8.0, "Jeddah": 6.5, "Australia": 8.42, "Suzuka": 10.33, "China": 6.31, "Miami": 9.33, "Imola": 10.38, "Monaco": 8.1, "Canada": 6.37, "Spain": 7.29, "Austria": 14.08, "Silverstone": 9.05, "Hungary": 7.29, "Spa-Francorchamps": 9.63, "Zandvoort": 9.0, "Monza": 9.35, "Baku": 11.33, "Singapore": 7.31, "Austin": 11.3, "Mexico": 13.29, "Brazil": 8.8, "Las Vegas": 9.0, "Qatar": 3.5, "Abu Dhabi": 9.69, "France": 10.67, "Hockenheim": 7.55, "Russia": 12.83, "Turkey": 5.88, "Portugal": 13.0, "Nürburgring": 7.56},
    "STR": {"Bahrain": 13.56, "Jeddah": 11.5, "Australia": 13.83, "Suzuka": 15.33, "China": 13.75, "Miami": 13.0, "Imola": 13.25, "Monaco": 15.57, "Canada": 15.33, "Spain": 13.0, "Austria": 11.9, "Silverstone": 13.11, "Hungary": 13.25, "Spa-Francorchamps": 13.63, "Zandvoort": 11.0, "Monza": 10.0, "Baku": 13.0, "Singapore": 17.0, "Austin": 13.67, "Mexico": 17.33, "Brazil": 14.0, "Las Vegas": 19.0, "Qatar": 14.0, "Abu Dhabi": 13.57, "France": 17.5, "Hockenheim": 16.0, "Russia": 11.6, "Turkey": 4.5, "Portugal": 14.5, "Nürburgring": 13.56},
    "RIC": {"Bahrain": 8.69, "Jeddah": 13.0, "Australia": 10.0, "Suzuka": 11.36, "China": 7.22, "Miami": 17.0, "Imola": 6.5, "Monaco": 7.73, "Canada": 7.4, "Spain": 9.5, "Austria": 9.75, "Silverstone": 10.21, "Hungary": 10.71, "Spa-Francorchamps": 10.29, "Zandvoort": 13.5, "Monza": 10.92, "Baku": 8.5, "Singapore": 9.9, "Austin": 8.27, "Mexico": 7.63, "Brazil": 12.75, "Las Vegas": 14.0, "Qatar": 14.0, "Abu Dhabi": 10.62, "France": 8.0, "Hockenheim": 10.2, "Russia": 8.0, "Turkey": 12.5, "Portugal": 13.0, "Nürburgring": 11.33},
    "TSU": {"Bahrain": 13.5, "Jeddah": 13.0, "Australia": 11.0, "Suzuka": 10.67, "China": 19.0, "Miami": 12.0, "Imola": 13.0, "Monaco": 11.0, "Canada": 15.67, "Spain": 15.25, "Austria": 12.8, "Silverstone": 14.5, "Hungary": 14.75, "Spa-Francorchamps": 16.75, "Zandvoort": 13.33, "Monza": 15.33, "Baku": 7.67, "Singapore": 12.5, "Austin": 13.33, "Mexico": 16.0, "Brazil": 17.0, "Las Vegas": 20.0, "Qatar": 9.5, "Abu Dhabi": 8.33, "France": 14.0, "Hockenheim": 13.31, "Russia": 12.0, "Turkey": 9.0, "Portugal": 14.0, "Nürburgring": 13.31},
    "HUL": {"Bahrain": 11.25, "Jeddah": 14.0, "Australia": 10.91, "Suzuka": 12.55, "China": 11.0, "Miami": 10.5, "Imola": 10.0, "Monaco": 11.64, "Canada": 9.73, "Spain": 13.45, "Austria": 8.75, "Silverstone": 9.31, "Hungary": 10.73, "Spa-Francorchamps": 12.73, "Zandvoort": 14.0, "Monza": 11.9, "Baku": 14.8, "Singapore": 10.5, "Austin": 10.0, "Mexico": 8.83, "Brazil": 8.6, "Las Vegas": 13.0, "Qatar": 14.0, "Abu Dhabi": 9.0, "France": 12.5, "Hockenheim": 7.83, "Russia": 10.33, "Turkey": 17.0, "Portugal": 10.8, "Nürburgring": 15.0},
    "MAG": {"Bahrain": 13.4, "Jeddah": 12.0, "Australia": 12.0, "Suzuka": 14.63, "China": 13.5, "Miami": 12.67, "Imola": 14.33, "Monaco": 13.63, "Canada": 14.38, "Spain": 12.44, "Austria": 12.5, "Silverstone": 14.4, "Hungary": 15.67, "Spa-Francorchamps": 12.56, "Zandvoort": 19.0, "Monza": 13.38, "Baku": 15.5, "Singapore": 12.0, "Austin": 13.71, "Mexico": 16.0, "Brazil": 11.0, "Las Vegas": 8.0, "Qatar": 18.0, "Abu Dhabi": 15.13, "France": 14.67, "Hockenheim": 9.25, "Russia": 12.83, "Turkey": 13.0, "Portugal": 19.0, "Nürburgring": 15.0},
    "GAS": {"Bahrain": 11.25, "Jeddah": 10.5, "Australia": 14.8, "Suzuka": 13.17, "China": 12.67, "Miami": 8.0, "Imola": 10.25, "Monaco": 9.67, "Canada": 13.8, "Spain": 10.14, "Austria": 9.67, "Silverstone": 11.0, "Hungary": 11.71, "Spa-Francorchamps": 10.43, "Zandvoort": 9.0, "Monza": 13.0, "Baku": 12.8, "Singapore": 11.25, "Austin": 11.0, "Mexico": 13.33, "Brazil": 11.0, "Las Vegas": 4.0, "Qatar": 4.5, "Abu Dhabi": 13.29, "France": 10.75, "Hockenheim": 12.0, "Russia": 13.25, "Turkey": 11.5, "Portugal": 9.0, "Nürburgring": 12.0},
    "OCO": {"Bahrain": 11.88, "Jeddah": 9.25, "Australia": 12.2, "Suzuka": 11.67, "China": 14.0, "Miami": 13.67, "Imola": 12.25, "Monaco": 9.33, "Canada": 9.6, "Spain": 9.86, "Austria": 11.22, "Silverstone": 11.88, "Hungary": 12.29, "Spa-Francorchamps": 10.25, "Zandvoort": 12.0, "Monza": 12.71, "Baku": 11.6, "Singapore": 13.8, "Austin": 12.17, "Mexico": 13.5, "Brazil": 14.67, "Las Vegas": 16.0, "Qatar": 8.5, "Abu Dhabi": 11.0, "France": 10.67, "Hockenheim": 15.0, "Russia": 8.0, "Turkey": 9.5, "Portugal": 8.5, "Nürburgring": 7.0},
    "ALB": {"Bahrain": 11.67, "Jeddah": 15.0, "Australia": 13.25, "Suzuka": 12.25, "China": 17.0, "Miami": 14.33, "Imola": 12.67, "Monaco": 12.0, "Canada": 11.0, "Spain": 14.6, "Austria": 11.5, "Silverstone": 10.5, "Hungary": 14.2, "Spa-Francorchamps": 10.6, "Zandvoort": 9.5, "Monza": 7.67, "Baku": 13.33, "Singapore": 12.67, "Austin": 9.67, "Mexico": 12.0, "Brazil": 12.33, "Las Vegas": 5.0, "Qatar": 13.0, "Abu Dhabi": 10.75, "France": 12.0, "Hockenheim": 16.0, "Russia": 17.5, "Turkey": 4.0, "Portugal": 6.0, "Nürburgring": 5.0},
    "SAR": {"Bahrain": 17.6, "Jeddah": 19.5, "Australia": 18.0, "Suzuka": 19.5, "China": 20.0, "Miami": 18.5, "Imola": 19.0, "Monaco": 15.5, "Canada": 15.5, "Spain": 19.5, "Austria": 18.5, "Silverstone": 13.0, "Hungary": 17.0, "Spa-Francorchamps": 18.0, "Zandvoort": 10.0, "Monza": 15.0, "Baku": 14.0, "Singapore": 18.0, "Austin": 16.0, "Mexico": 19.0, "Brazil": 19.0, "Las Vegas": 6.0, "Qatar": 15.0, "Abu Dhabi": 20.0, "France": 16.91, "Hockenheim": 16.91, "Russia": 16.91, "Turkey": 16.91, "Portugal": 16.91, "Nürburgring": 16.91},
    "BOT": {"Bahrain": 5.92, "Jeddah": 10.0, "Australia": 12.33, "Suzuka": 8.2, "China": 6.25, "Miami": 10.33, "Imola": 8.0, "Monaco": 10.0, "Canada": 7.3, "Spain": 6.42, "Austria": 6.69, "Silverstone": 8.31, "Hungary": 6.08, "Spa-Francorchamps": 9.67, "Zandvoort": 12.33, "Monza": 8.45, "Baku": 7.43, "Singapore": 9.67, "Austin": 7.2, "Mexico": 5.63, "Brazil": 7.6, "Las Vegas": 7.0, "Qatar": 7.5, "Abu Dhabi": 9.27, "France": 4.5, "Hockenheim": 3.5, "Russia": 4.38, "Turkey": 5.0, "Portugal": 1.5, "Nürburgring": 9.0},
    "ZHO": {"Bahrain": 15.0, "Jeddah": 14.33, "Australia": 16.67, "Suzuka": 17.67, "China": 16.0, "Miami": 16.67, "Imola": 18.5, "Monaco": 19.0, "Canada": 16.67, "Spain": 14.33, "Austria": 16.67, "Silverstone": 13.33, "Hungary": 11.67, "Spa-Francorchamps": 18.0, "Zandvoort": 14.5, "Monza": 12.5, "Baku": 14.5, "Singapore": 16.5, "Austin": 15.0, "Mexico": 11.0, "Brazil": 16.5, "Las Vegas": 17.0, "Qatar": 19.0, "Abu Dhabi": 17.0, "France": 16.0, "Hockenheim": 15.69, "Russia": 15.69, "Turkey": 15.69, "Portugal": 15.69, "Nürburgring": 15.69}
}

track_list = {
    "Bahrain": 90.021,
    "Jeddah": 88.584,
    "Australia": 77.014,
    "Suzuka": 89.285,
    "China": 94.837,
    "Miami": 88.051,
    "Imola": 75.737,
    "Monaco": 71.266,
    "Canada": 72.705,
    "Spain": 72.256,
    "Austria": 65.288,
    "Silverstone": 88.924,
    "Hungary": 76.498,
    "Spa-Francorchamps": 106.075,
    "Zandvoort": 76.690, # from zandvoort onwards should subtract 0.5-1s for 2024 cars
    "Monza": 81.451,
    "Baku": 102.465,
    "Singapore": 92.076,
    "Austin": 95.585,
    "Mexico": 78.306,
    "Brazil": 70.513,
    "Las Vegas": 93.913,
    "Qatar": 85.297,
    "Abu Dhabi": 84.216,
    "France": 92.600, # have to get other data for these 6 tracks
    "Hockenheim": 72.905,
    "Russia": 93.247,
    "Turkey": 84.727,
    "Portugal": 79.244,
    "Nürburgring": 86.637
}

lap_data = { # will be accessed something like (lap_data['driver'][i] = whatever bullshit)
    'driver': [],
    'track': [],
    'year': [],
    'avg_grid_pos_track': [],
    'track_avg_lap_time': [],
    'temperature': [], # higher temp == slower laps (significant, from tire deg and lower engine RPM)
    'rain': [],
    'target_time': [], # just get the actual times basically
    'years_since_reg_change': []
}



# print(f"{session.results['Abbreviation']} {session.results['Q3']}")
# for result in session.results['Q3']:
#     print(result, session._drivers_results_from_ergast())

# print(session.results['Q3'], session.results['Abbreviation'])

# print(df)

# # for index, row in df.iterrows():
# #     print(row['Abbreviation'], row['Q3'])

erg = Ergast('pandas')

# don't understand this object, read https://docs.fastf1.dev/ergast.html#fastf1.ergast.interface.ErgastMultiResponse

# print(result.content[0]['Q3'].iloc[3])

# new_dict = result.content[0].to_dict()

# print(new_dict.keys())

# for key in new_dict: # invert all internal dictionaries
#     new_dict[key] = {v: k for k, v in new_dict[key].items()}
# print(new_dict)

# print(new_dict.keys())

# print(new_dict['Q3'])

# drivers = new_dict['driverCode'].keys()

# print(result.content[0])

year = 2014
for num in num_races:
    for j in range(num):
        result = erg.get_qualifying_results(
                                     season=year,
                                        round=j+1,
                                        result_type='pandas'
                                        )
        
        try:
            data = result.content[0]
        except:
            continue
        data.to_csv('test.csv')
        locality =  str(result.description['locality']).split('Name')[0].strip()
        country = str(result.description['country']).split()[1]
        print(locality, country)

        if country in track_list.keys():
            track = country
        elif locality.__contains__('Yas Marina'):
            track = 'Abu Dhabi'
        else:
            track = locality
            if track not in track_list.keys():
                continue

        # df = session._drivers_results_from_ergast(load_drivers=True, load_results=True)
        # df = df.drop(labels=['DriverNumber', 'TeamId', 'DriverId', 'LastName', 'FirstName', 'FullName'], axis=1)

        for i in range(20): # use this to create more dataset entries (how far back?)
            # Code is same for all cases

            try:
                driver = re.findall(r'[A-Z]{3}', str(data.iloc[i]))[0]
            except:
                continue

            if driver not in average_grid_positions.keys():
                continue

            if driver == 'VER' and year < 2017: # skip Jean Eric-Vergne (will cause errors when trying to find data for VER)
                continue

            if driver == 'VES': # Verstappen pre-2017
                driver = 'VER'

            # print(str(data.iloc[i]))
            if i < 10: # driver made it to Q3
                
                try: 
                    lap_data['target_time'].append(F1_Quali.convert_time(re.findall(r'0\d\:\d{2}\.\d{3}', str(data.iloc[i]))[2]))
                except:
                    continue # skip entry if no lap time set, not relevant
            elif i < 15: # driver made it to Q2
                try:
                    lap_data['target_time'].append(F1_Quali.convert_time(re.findall(r'0\d\:\d{2}\.\d{3}', str(data.iloc[i]))[1]))
                except:
                    continue
            else: # driver made it to Q1
                try:
                    lap_data['target_time'].append(F1_Quali.convert_time(re.findall(r'0\d\:\d{2}\.\d{3}', str(data.iloc[i]))[0]))
                except:
                    continue


            lap_data['driver'].append(driver)
            lap_data["track"].append(track)
            lap_data["year"].append(year)
            lap_data["avg_grid_pos_track"].append(average_grid_positions[driver][track])
            lap_data["rain"].append(False) # for now, don't know what approach to take
            lap_data["track_avg_lap_time"].append(track_list[track])
            lap_data['temperature'].append(25.0)
            lap_data['years_since_reg_change'].append(F1_Quali.get_years_since_reg_change(year))
    year += 1


for key in lap_data:
    print(key, len(lap_data[key]))

df = pd.DataFrame(lap_data)
print(df)
df.to_csv('data/old_data.csv')


# print(re.findall(r'\S\S+', str(result.description['country']))[0]) # can retreive country and locality and use whatever matches 