import pickle
import pandas as pd

def main():
    correct = pd.read_csv("../Data/Icelandic_Set.csv", sep=';', decimal=',')
    correct = correct.dropna()
    df = correct.drop(columns=['SummaryYear','SummaryMonth','NMerchantID','MerchantName', 'CompanySSN'])

    with open('random-forest-03-11-2020.pkl', 'rb') as f:
        clf = pickle.load(f)
    X = df.drop('MerchantActive', axis=1)
    y = df['MerchantActive']

    y_pred = clf.predict(X)

    correct['predicted label'] = ["active" if x == 1 else "churned" for x in y_pred]
    correct.to_csv('../Data/predicted.csv', index=False)
    print(len(correct[correct['predicted label'] == "churned"]))
main()