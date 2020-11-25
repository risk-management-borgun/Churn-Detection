import pandas as pd
import numpy as np
from datetime import date
from tqdm import tqdm

# location of transaction and merchant summary files
TRX_FILE = "./trx_active_summary.csv"
MERCHANT_FILE = "./merchant_summaries_active_v2.csv"

# calculate the avg of a column for a mid
def calculateAvgOfTrxColumn(days, mid, df, column, sum=False):
    dfMid = df[df.NMerchantID == mid]
    total = 0

    for index, row in dfMid.iterrows():
        df_date = row['TransactionDate'].date()
        num = row[column]
        delta =  date.today() - df_date
        
        if delta.days <= days:
            total += num
        else:
            break #the df is sorted by date so we don't have to continue
    if sum:
        return total
    else:
        return total/days

# calculate the avg of a column for a mid
def calculateAvgOfTrxColumnFromLastDate(days, mid, df, column, sum=False):
    dfMid = df[df.NMerchantID == mid]
    
    if len(dfMid) == 0:
        return 0

    lastDate = dfMid['TransactionDate'].iloc[0].date()    
    total = 0

    for index, row in dfMid.iterrows():
        df_date = row['TransactionDate'].date()
        num = row[column]

        delta =  lastDate - df_date
        
        if delta.days <= days:
            total += num
        else:
            break #the df is sorted by date so we don't have to continue
    if sum:
        return total
    else:
        return total/days 

def main():
    merchant_file = input("File containing merchant summaries: ")
    trx_file = input("File containing daily transaction summaries: ")
    output_file = input("Output file: ")

    #read csv files into dataframes
    print("Loading data...")
    m_df = pd.read_csv(merchant_file, sep=";", decimal=",")
    t_df = pd.read_csv(trx_file, sep=";", decimal=",")

    #Reverse sort trx data so that the newest will be on top
    t_df['TransactionDate'] = pd.to_datetime(t_df.TransactionDate)
    t_df = t_df.sort_values('TransactionDate', ascending=False)

    #data that will become the complete dataframe
    transformed_data = {
        "avgNumTrx30": [],
        "avgNumTrx60": [],
        "avgNumTrx90": [],
        "avgNumTrxSinceLast30": [],
        "avgNumTrxSinceLast60": [],
        "avgNumTrxSinceLast90": [],
        "avgAmntTrx30": [],
        "avgAmntTrx60": [],
        "avgAmntTrx90": [],
        "avgAmntTrxSinceLast30": [],
        "avgAmntTrxSinceLast60": [],
        "avgAmntTrxSinceLast90": [],
        "TurnoverBalanceRatio": [],
        "TurnoverBalanceRatioSinceLast": []
    }

    #iterate over ids and calculate the needed values from the trx data
    #this is kinda disgusting code i know....
    for index, row in tqdm(m_df.iterrows(),desc="Transforming data..."):
        id = row["NMerchantID"]

        #avg daily trx frequency for different intervals
        avgNumTrx30 = calculateAvgOfTrxColumn(30, id, t_df, "Transactions")
        avgNumTrx60 = calculateAvgOfTrxColumn(60, id, t_df, "Transactions")
        avgNumTrx90 = calculateAvgOfTrxColumn(90, id, t_df, "Transactions")
        avgNumTrxSinceLast30 = calculateAvgOfTrxColumnFromLastDate(30, id, t_df, "Transactions")
        avgNumTrxSinceLast60 = calculateAvgOfTrxColumnFromLastDate(60, id, t_df, "Transactions")
        avgNumTrxSinceLast90 = calculateAvgOfTrxColumnFromLastDate(90, id, t_df, "Transactions")

        #avg daily trx frequency for different intervals
        avgAmntTrx30 = calculateAvgOfTrxColumn(30, id, t_df, "SettlementAmountISK")
        avgAmntTrx60 = calculateAvgOfTrxColumn(60, id, t_df, "SettlementAmountISK")
        avgAmntTrx90 = calculateAvgOfTrxColumn(90, id, t_df, "SettlementAmountISK")
        avgAmntTrxSinceLast30 = calculateAvgOfTrxColumnFromLastDate(30, id, t_df, "SettlementAmountISK")
        avgAmntTrxSinceLast60 = calculateAvgOfTrxColumnFromLastDate(60, id, t_df, "SettlementAmountISK")
        avgAmntTrxSinceLast90 = calculateAvgOfTrxColumnFromLastDate(90, id, t_df, "SettlementAmountISK")

        trxSum = calculateAvgOfTrxColumn(30, id, t_df, "SettlementAmountISK", sum=True)
        trxSumSinceSast = calculateAvgOfTrxColumnFromLastDate(30, id, t_df, "SettlementAmountISK", sum=True)


        if trxSum != 0:
            turnoverRatio = row['MerchantBalanceISK'] / trxSum
        else:
            turnoverRatio = row['MerchantBalanceISK'] # should this maybe be zero?
        
        transformed_data["TurnoverBalanceRatio"].append(turnoverRatio)
        
        if trxSumSinceSast != 0:
            turnoverRatioSinceLast = row['MerchantBalanceISK'] / trxSumSinceSast
        else:
            turnoverRatioSinceLast = row['MerchantBalanceISK'] # should this maybe be zero?
        
        transformed_data["TurnoverBalanceRatioSinceLast"].append(turnoverRatioSinceLast)

        transformed_data["avgNumTrx30"].append(avgNumTrx30)
        transformed_data["avgNumTrx60"].append(avgNumTrx60)
        transformed_data["avgNumTrx90"].append(avgNumTrx90)
        transformed_data["avgNumTrxSinceLast30"].append(avgNumTrxSinceLast30)
        transformed_data["avgNumTrxSinceLast60"].append(avgNumTrxSinceLast60)
        transformed_data["avgNumTrxSinceLast90"].append(avgNumTrxSinceLast90)
        transformed_data["avgAmntTrx30"].append(avgAmntTrx30)
        transformed_data["avgAmntTrx60"].append(avgAmntTrx60)
        transformed_data["avgAmntTrx90"].append(avgAmntTrx90)
        transformed_data["avgAmntTrxSinceLast30"].append(avgAmntTrxSinceLast30)
        transformed_data["avgAmntTrxSinceLast60"].append(avgAmntTrxSinceLast60)
        transformed_data["avgAmntTrxSinceLast90"].append(avgAmntTrxSinceLast90)

    
    #export the result to csv
    aggrigate = pd.DataFrame(transformed_data)
    print("Saving...")
    result = pd.concat([m_df, aggrigate], axis=1).reindex(m_df.index)
    result.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()