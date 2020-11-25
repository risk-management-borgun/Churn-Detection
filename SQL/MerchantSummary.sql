SELECT

*,

CASE
    WHEN DaysSinceLastSettlement <= 7 THEN 1
    ELSE 0
END AS transactedPastWeek

from

 
(SELECT

 

tafla1.period,

 

tafla1.SettlementAmountISK,

 

tafla1.NMerchantID,

 

tafla1.MerchantName,


tafla1.MCCCode,


tafla1.DaysSinceLastSettlement,

 

tafla1.CompanySSN,

 

tafla1.Transactions,



tafla1.avgTransactionsPerDay,

 
tafla1.diffTrxContractEnd,


tafla1.Fees,

 

--calculate the ratio betwwen the fee and the settlment amount

tafla1.Fees / NULLIF(tafla1.SettlementAmountISK, 0) as FeeRatio,

 

--get avg fees and feeRatios for the past 2 preceding months

(SUM(tafla1.Transactions) OVER (PARTITION by tafla1.NMerchantID ORDER BY tafla1.period, tafla1.NMerchantID ROWS BETWEEN 2 preceding and 1 preceding))/2 as TransactionsLastTwoMonths,

 

AVG(tafla1.avgTransactionsPerDay) OVER (PARTITION by tafla1.NMerchantID ORDER BY tafla1.period, tafla1.NMerchantID ROWS BETWEEN 2 preceding and 1 preceding) as avgTransactionsPerDayLastTwoMonths,



(SUM(tafla1.SettlementAmountISK) OVER (PARTITION by tafla1.NMerchantID ORDER BY tafla1.period, tafla1.NMerchantID ROWS BETWEEN 2 preceding and 1 preceding))/2 as SettlementsLastTwoMonths,
 

(SUM(tafla1.Fees / NULLIF(tafla1.SettlementAmountISK, 0)) OVER (PARTITION by tafla1.NMerchantID ORDER BY tafla1.period, tafla1.NMerchantID ROWS BETWEEN 2 preceding and 1 preceding))/2 as FeeRatioLastTwoMonths,


ISNULL(b12.MerchantBalance, b.MerchantBalance) as MerchantBalance, --if vbalances is null for merchant then try b2
 

tafla1.MerchantActive

 

 

FROM (
select

floor(datediff(D, '1970-01-01', t.TransactionDate) / 30) as period,

m.NMerchantID, 

m.MerchantName,

m.CompanySSN, 

m.MerchantActive,

m.MCCCode,

DATEDIFF(day, s.LastSettlement, GETDATE()) AS DaysSinceLastSettlement,

SUM(t.SettlementAmountISK) AS SettlementAmountISK,

(case when count(*) > 1
        then datediff(day, min(t.TransactionDate), max(t.TransactionDate)) / cast(count(*) - 1 as float)
        else 0
end) as avgTransactionsPerDay,

(case when m.MerchantActive = 0
        then datediff(day, max(t.TransactionDate), m.dss_end_date)
        else datediff(day, max(t.TransactionDate), GETDATE())
end) as diffTrxContractEnd, --days since the contract ended

COUNT(*) AS Transactions, 

f.Fees

From

BorgunDW.ACQ.D_Merchant_H m

left join BorgunDW.ACQ.F_Transaction t on t.NMerchantID = m.NMerchantID

left join (SELECT MERCHANTID,
MAX(SETTLE_DATE) as LastSettlement
FROM ACQ.F_DM_settle_opt
GROUP BY MERCHANTID) s on m.NMerchantID = s.MERCHANTID

right join BorgunDW.Dim.D_Date d on d.D_DateId = t.D_TransactionDateID

left join (select NMerchantID, StartOfMonthID, sum(MerchantFeesISK) Fees from BorgunDW.ACQ.F_Fees_Aggregated_Monthly GROUP BY NMerchantID, StartOfMonthID

) f on f.NMerchantID = m.NMerchantID and f.StartOfMonthID = d.StartOfMonthID

--hér get ég minnkað hvaða transactional gögn ég held áfram með
--ef ég er að gera fyrir inactive merchants þá þyrfti ég að taka öll trx gögnin fyrir þá
where m.MerchantCountry = 'ISL' and m.MerchantActive = 1 and t.TransactionDate > DATEADD(day, -90, GETDATE())

group by

floor(datediff(D, '1970-01-01', t.TransactionDate) / 30)

,m.NMerchantID,

m.MerchantName,m.CompanySSN,m.MerchantActive,f.Fees,m.MCCCode,

DATEDIFF(day, s.LastSettlement, GETDATE()), m.dss_end_date
) as tafla1

 
left join ACQ.vBalances b12 on b12.NMerchantID = tafla1.NMerchantID
 
-- I'm getting the most  recent balance here
left JOIN (select balanceTable.MerchantBalance, balanceTable.NMerchantID from ACQ.Balances balanceTable
where ValueDate = any(SELECT max(ValueDate) from ACQ.Balances where NMerchantID = balanceTable.NMerchantID))
b on tafla1.NMerchantID = b.NMerchantID) as tafla2

 

-- here I only want to get the newest year and month for the merchants. meaning we only want to summerize the month that the merchant had his last transaction

WHERE (tafla2.period) = any( SELECT max(floor(datediff(D, '1970-01-01', t1.TransactionDate) / 30))

  FROM BorgunDW.ACQ.F_Transaction t1

  WHERE tafla2.NMerchantID = t1.NMerchantID

  GROUP BY t1.NMerchantID

)