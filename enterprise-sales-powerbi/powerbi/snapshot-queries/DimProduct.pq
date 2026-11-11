let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\DimProduct.csv"), [Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"ProductID", Int64.Type}, {"ProductName", type text}, {"Brand", type text}, {"Size", type text}, {"Color", type text}, {"SupplierName", type text}, {"SupplierCategory", type text}, {"UnitPackageType", type text}, {"OuterPackageType", type text}, {"LeadTimeDays", Int64.Type}, {"QuantityPerOuter", Int64.Type}, {"IsChillerStock", type logical}, {"RecommendedRetailPrice", Currency.Type}, {"TypicalWeightPerUnit", Currency.Type}}, "en-US")
in
    Typed