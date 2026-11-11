USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_DimStockGroup]    Script Date: 28-08-2026 12:54:32 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [BI].[vw_DimStockGroup]
AS

SELECT
    StockGroupID,
    StockGroupName
FROM Warehouse.StockGroups;
GO

