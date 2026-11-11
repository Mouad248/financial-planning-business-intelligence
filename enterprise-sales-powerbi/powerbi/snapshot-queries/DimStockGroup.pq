let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\DimStockGroup.csv"), [Delimiter=",", Columns=2, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"StockGroupID", Int64.Type}, {"StockGroupName", type text}}, "en-US")
in
    Typed