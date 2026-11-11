let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\DimSalesperson.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"SalespersonID", Int64.Type}, {"FullName", type text}, {"PreferredName", type text}, {"EmailAddress", type text}, {"PhoneNumber", type text}}, "en-US")
in
    Typed