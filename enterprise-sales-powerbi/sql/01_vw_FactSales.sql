USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_FactSales]    Script Date: 28-08-2026 12:53:24 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [BI].[vw_FactSales]
as
select
    -- Transaction identifiers
    il.InvoiceLineID,
    i.InvoiceID,
    i.OrderID,
      -- Date
    i.InvoiceDate,
      -- Dimension keys
    i.CustomerID,
    il.StockItemID AS ProductID,
    i.SalespersonPersonID AS SalespersonID,
     -- Transaction quantities / rates
    il.Quantity,
    il.UnitPrice,
    il.TaxRate,
     -- Additive financial values
    CAST(
        il.Quantity * il.UnitPrice
        AS decimal(18,2)
    ) AS NetSalesAmount,
     CAST(
        (il.Quantity * il.UnitPrice) - il.LineProfit
        AS decimal(18,2)
    ) AS CostAmount,
 CAST(
        il.LineProfit
        AS decimal(18,2)
    ) AS GrossProfitAmount,
    CAST(
        il.TaxAmount
        AS decimal(18,2)
    ) AS TaxAmount,
     CAST(
        il.ExtendedPrice
        AS decimal(18,2)
    ) AS InvoiceValueAmount,
     -- Useful analytical flag
    CASE
        WHEN il.LineProfit < 0 THEN 1
        ELSE 0
    END AS IsLossMaking
    FROM Sales.InvoiceLines AS il
    INNER JOIN Sales.Invoices AS i
    ON il.InvoiceID = i.InvoiceID;
GO

