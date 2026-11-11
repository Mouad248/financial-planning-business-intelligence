USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_DimProduct]    Script Date: 28-08-2026 12:54:00 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [BI].[vw_DimProduct]
AS

SELECT
    si.StockItemID AS ProductID,
    si.StockItemName AS ProductName,

    si.Brand,
    si.Size,

    c.ColorName AS Color,

    CONCAT('Supplier ', si.SupplierID) AS SupplierName,
    sc.SupplierCategoryName AS SupplierCategory,

    up.PackageTypeName AS UnitPackageType,
    op.PackageTypeName AS OuterPackageType,

    si.LeadTimeDays,
    si.QuantityPerOuter,
    si.IsChillerStock,

    CAST(
        si.RecommendedRetailPrice
        AS decimal(18,2)
    ) AS RecommendedRetailPrice,

    CAST(
        si.TypicalWeightPerUnit
        AS decimal(18,3)
    ) AS TypicalWeightPerUnit

FROM Warehouse.StockItems AS si

LEFT JOIN Warehouse.Colors AS c
    ON si.ColorID = c.ColorID

LEFT JOIN Purchasing.Suppliers AS s
    ON si.SupplierID = s.SupplierID

LEFT JOIN Purchasing.SupplierCategories AS sc
    ON s.SupplierCategoryID = sc.SupplierCategoryID

LEFT JOIN Warehouse.PackageTypes AS up
    ON si.UnitPackageID = up.PackageTypeID

LEFT JOIN Warehouse.PackageTypes AS op
    ON si.OuterPackageID = op.PackageTypeID;
GO

