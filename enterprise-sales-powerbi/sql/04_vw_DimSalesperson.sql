USE [WideWorldImporters]
GO

/****** Object:  View [BI].[vw_DimSalesperson]    Script Date: 28-08-2026 12:54:16 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE   VIEW [BI].[vw_DimSalesperson]
AS

SELECT
    PersonID AS SalespersonID,
    CONCAT('Salesperson ', PersonID) AS FullName,
    CONCAT('Salesperson ', PersonID) AS PreferredName,
    CAST(NULL AS nvarchar(256)) AS EmailAddress,
    CAST(NULL AS nvarchar(50)) AS PhoneNumber
FROM Application.People
WHERE IsSalesperson = 1;
GO

