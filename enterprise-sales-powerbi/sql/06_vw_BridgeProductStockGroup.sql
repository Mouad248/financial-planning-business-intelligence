USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_BridgeProductStockGroup]    Script Date: 28-08-2026 12:53:08 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE   VIEW [BI].[vw_BridgeProductStockGroup]
AS

SELECT
    StockItemID AS ProductID,
    StockGroupID
FROM Warehouse.StockItemStockGroups;
GO

