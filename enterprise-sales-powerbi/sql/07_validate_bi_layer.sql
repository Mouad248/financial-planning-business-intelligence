USE [WideWorldImporters];
GO
-- Run after 00-06. These are executable checks, not recorded passing results.
IF EXISTS (SELECT InvoiceLineID FROM BI.vw_FactSales GROUP BY InvoiceLineID HAVING COUNT(*) > 1)
    THROW 50001, 'Fact grain is not unique', 1;
IF EXISTS (SELECT CustomerID FROM BI.vw_DimCustomer GROUP BY CustomerID HAVING COUNT(*) > 1)
    THROW 50002, 'Customer dimension key is not unique', 1;
IF EXISTS (SELECT SalespersonID FROM BI.vw_DimSalesperson GROUP BY SalespersonID HAVING COUNT(*) > 1)
    THROW 50003, 'Salesperson dimension key is not unique', 1;
IF EXISTS (SELECT 1 FROM BI.vw_FactSales f LEFT JOIN BI.vw_DimCustomer c ON f.CustomerID=c.CustomerID WHERE c.CustomerID IS NULL)
    THROW 50004, 'Missing customer dimension keys', 1;
IF EXISTS (SELECT 1 FROM BI.vw_DimSalesperson WHERE EmailAddress IS NOT NULL OR PhoneNumber IS NOT NULL OR FullName NOT LIKE 'Salesperson %')
    THROW 50005, 'Salesperson identity masking failed', 1;
SELECT COUNT_BIG(*) AS FactRows, SUM(NetSalesAmount) AS Revenue,
       SUM(GrossProfitAmount) AS GrossProfit, SUM(TaxAmount) AS Tax,
       SUM(InvoiceValueAmount) AS InvoiceValue,
       CAST(SUM(GrossProfitAmount) / NULLIF(SUM(NetSalesAmount),0) AS decimal(18,6)) AS GrossMargin
FROM BI.vw_FactSales;
GO
