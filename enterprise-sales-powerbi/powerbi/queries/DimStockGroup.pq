let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_DimStockGroup = Source{[Schema="BI",Item="vw_DimStockGroup"]}[Data]
in
    BI_vw_DimStockGroup