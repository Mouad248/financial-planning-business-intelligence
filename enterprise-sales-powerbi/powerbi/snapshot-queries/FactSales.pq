let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\FactSales.csv"), [Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"InvoiceLineID", Int64.Type}, {"InvoiceID", Int64.Type}, {"OrderID", Int64.Type}, {"InvoiceDate", type datetime}, {"CustomerID", Int64.Type}, {"ProductID", Int64.Type}, {"SalespersonID", Int64.Type}, {"Quantity", Int64.Type}, {"UnitPrice", Currency.Type}, {"TaxRate", type number}, {"NetSalesAmount", Currency.Type}, {"CostAmount", Currency.Type}, {"GrossProfitAmount", Currency.Type}, {"TaxAmount", Currency.Type}, {"InvoiceValueAmount", Currency.Type}, {"IsLossMaking", Int64.Type}}, "en-US")
in
    Typed