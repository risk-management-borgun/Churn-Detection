from tqdm import tqdm
import pandas as pd

def calculateColumn(data, date_from, date_to, column, method="mean"):
    """Calculates either the mean, sum or standard deviation for a given column for a given interval"""
    mask = (df['Date'] >= date_from) & (df['Date'] <= date_to)
    data = data.loc[mask]

    if method == "mean":
        return data[column].mean()
    elif method == "sum":
        return data[column].sum()
    elif method == "std":
        return data[column].std()
    else:
        return 0


def main():
    file_name = input("Enter CSV file: ")
    df = pd.read_csv("./Data/transactions.csv", sep=';', decimal=',', names=['Date', 'MID', 'Name', 'Amount', 'Transactions'], header=None)
    
    for mid in tqdm(df.MID.unique(), desc="Transforming data..."):
        mid_data = df[df['MID'] == mid]

if __name__ == "__main__":
    main()