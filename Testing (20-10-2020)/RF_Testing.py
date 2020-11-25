import pickle
import pandas as pd

def main():
    correct = pd.read_csv("testing_merchants.csv")
    correct = correct.dropna()
    print(correct.columns)
    df = correct.drop(columns=['CompanyName','CompanySSN', 'NMerchantID'])

    with open('random-forest-20-10-2020.pkl', 'rb') as f:
        clf = pickle.load(f)
    X = df.drop('MerchantActive', axis=1)
    print(X.tail())
    y = df['MerchantActive']

    y_pred = clf.predict(X)

    correct['predicted label'] = ["active" if x == 1 else "churned" for x in y_pred]
    correct.to_csv('./predicted.csv', index=False)
    print(len(correct[correct['predicted label'] == "churned"]))

main()