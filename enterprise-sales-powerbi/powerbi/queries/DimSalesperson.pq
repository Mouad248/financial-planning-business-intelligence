let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_DimSalesperson = Source{[Schema="BI",Item="vw_DimSalesperson"]}[Data]
in
    BI_vw_DimSalesperson