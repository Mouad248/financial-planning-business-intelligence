let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\DimCustomer.csv"), [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"CustomerID", Int64.Type}, {"CustomerName", type text}, {"CustomerCategory", type text}, {"BuyingGroup", type text}, {"City", type text}, {"StateProvince", type text}, {"SalesTerritory", type text}, {"Country", type text}, {"AccountOpenedDate", type datetime}, {"CreditLimit", Currency.Type}, {"StandardDiscountPercentage", type number}, {"PaymentDays", Int64.Type}, {"IsOnCreditHold", type logical}}, "en-US")
in
    Typed