let
    Source = Sql.Database(SqlServerInstance, "WideWorldImporters"),
    BI_vw_DimProduct = Source{[Schema="BI",Item="vw_DimProduct"]}[Data],
    #"Changed Type" = Table.TransformColumnTypes(BI_vw_DimProduct,{{"RecommendedRetailPrice", Currency.Type}, {"TypicalWeightPerUnit", Currency.Type}}),
    Custom1 = Table.ReplaceValue(#"Changed Type", null, "Not Specified", Replacer.ReplaceValue, {"Brand"}),
    Custom2 = Table.ReplaceValue(#"Custom1", null, "Not Specified", Replacer.ReplaceValue, {"Size"}),
    Custom3 = Table.ReplaceValue(#"Custom2", null, "Not Specified", Replacer.ReplaceValue, {"Color"})
in
    Custom3