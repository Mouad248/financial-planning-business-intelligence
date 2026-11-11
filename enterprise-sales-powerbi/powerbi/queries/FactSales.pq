let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_FactSales = Source{[Schema="BI",Item="vw_FactSales"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(BI_vw_FactSales,{{"TaxRate", type number}, {"UnitPrice", Currency.Type}, {"NetSalesAmount", Currency.Type}, {"CostAmount", Currency.Type}, {"GrossProfitAmount", Currency.Type}, {"TaxAmount", Currency.Type}, {"InvoiceValueAmount", Currency.Type}})
in
    #"Changed Type"