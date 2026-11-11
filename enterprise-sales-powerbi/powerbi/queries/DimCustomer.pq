let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_DimCustomer = Source{[Schema="BI",Item="vw_DimCustomer"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(BI_vw_DimCustomer,{{"CreditLimit", Currency.Type}}),
    Custom1 = Table.ReplaceValue(#"Changed Type", null, "No Buying Group", Replacer.ReplaceValue, {"BuyingGroup"})
in
    Custom1