import pandas as pd
import seaborn as sb
import matplotlib as plt
from sklearn.cluster import DBSCAN

MONTH_EST = 30.51

#returns a 2d matrix of number of trx for each day for each year
def getTotalsPerDay(data):
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
    
    compiled = {
        "day": [],
        "trx": []
    }
    
    for index, row in data.iterrows():
        day_of_year = row['Date'].timetuple().tm_yday
        compiled["day"].append(day_of_year)
        compiled["trx"].append(1)
    
    return pd.DataFrame(compiled).sort_values(by=['day']).reset_index(drop=True)

# returns all seasons and at what months the seasons are
def getSeasons(X):
    clustering = DBSCAN(eps=15, min_samples=5).fit(X)
    seasons = []
    
    current_season = None
    current_day = None
    
    for index, label in enumerate(clustering.labels_):
        if current_season == None:
            current_season = label
            current_day = X['day'][0]
        elif current_season != label and index != len(clustering.labels_)-1 and label != -1:
            start_month = (current_day // MONTH_EST)+1
            end_month = (X['day'][index-1] // MONTH_EST)+1
            
            current_season = label
            current_day = X['day'][index]
            
            seasons.append((int(start_month), int(end_month)))
        elif index == len(clustering.labels_)-1:
            start_month = (current_day // MONTH_EST)+1
            end_month = (X['day'][index] // MONTH_EST)+1
            
            seasons.append((int(start_month), int(end_month)))
    return seasons

def main():
    df = pd.read_csv("./Data/transactions.csv", sep=';', decimal=',', names=['Date', 'MID', 'Name', 'Amount', 'Transactions'], header=None)
    season_data = {
        "MID": [],
        "Start": [],
        "End": []
    }
    
    for mid in df.MID.unique():
        try:
            data = df[df['MID'] == mid]

            if(len(data) < 365):
                continue

            trx_on_days = getTotalsPerDay(data)
            seasons = getSeasons(trx_on_days)

            season_data["End"].append(seasons[0][1])
            season_data["Start"].append(seasons[0][0])
            season_data["MID"].append(mid)
        except:
            continue
    season_data = pd.DataFrame(season_data)
    season_data.to_csv("Data/seasonalities.csv")
main()