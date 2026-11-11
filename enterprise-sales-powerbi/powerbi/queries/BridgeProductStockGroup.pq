let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_BridgeProductStockGroup = Source{[Schema="BI",Item="vw_BridgeProductStockGroup"]}[Data]
in
    BI_vw_BridgeProductStockGroup