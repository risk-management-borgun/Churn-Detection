SELECT

t1.TransactionDate,

t2.NMerchantID,

SUM(t1.SettlementAmountISK) AS SettlementAmountISK,

COUNT(*) AS Transactions 

FROM ACQ.F_Transaction t1

INNER JOIN ACQ.D_Merchant t2 ON t2.NMerchantID = t1.NMerchantID
 

WHERE t1.D_TransactionDateID > 20200615

AND t2.MerchantActive = 1 and t2.MerchantCountry = 'ISL'

 

GROUP BY

t1.TransactionDate,

t2.NMerchantID,

t2.MerchantName,

t2.MerchantCountry,

t2.MerchantActive


ORDER BY 1