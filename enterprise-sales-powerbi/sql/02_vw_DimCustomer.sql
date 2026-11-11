USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_DimCustomer]    Script Date: 28-08-2026 12:53:40 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [BI].[vw_DimCustomer]
AS

SELECT
    c.CustomerID,
    CONCAT('Customer ', c.CustomerID) AS CustomerName,

    cc.CustomerCategoryName AS CustomerCategory,

    CASE WHEN c.BuyingGroupID IS NULL THEN NULL
         ELSE CONCAT('Buying Group ', c.BuyingGroupID) END AS BuyingGroup,

    city.CityName AS City,
    sp.StateProvinceName AS StateProvince,
    sp.SalesTerritory,
    co.CountryName AS Country,

    c.AccountOpenedDate,

    CAST(
        c.CreditLimit
        AS decimal(18,2)
    ) AS CreditLimit,

    c.StandardDiscountPercentage,
    c.PaymentDays,
    c.IsOnCreditHold

FROM Sales.Customers AS c

LEFT JOIN Sales.CustomerCategories AS cc
    ON c.CustomerCategoryID = cc.CustomerCategoryID

LEFT JOIN Sales.BuyingGroups AS bg
    ON c.BuyingGroupID = bg.BuyingGroupID

LEFT JOIN Application.Cities AS city
    ON c.DeliveryCityID = city.CityID

LEFT JOIN Application.StateProvinces AS sp
    ON city.StateProvinceID = sp.StateProvinceID

LEFT JOIN Application.Countries AS co
    ON sp.CountryID = co.CountryID;
GO

