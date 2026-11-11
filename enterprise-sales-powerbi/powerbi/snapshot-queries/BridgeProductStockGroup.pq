let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\BridgeProductStockGroup.csv"), [Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"ProductID", Int64.Type}, {"StockGroupID", Int64.Type}}, "en-US")
in
    Typed