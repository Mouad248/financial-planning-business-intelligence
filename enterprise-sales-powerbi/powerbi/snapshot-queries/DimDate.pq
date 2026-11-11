let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\model\DimDate.csv"), [Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Date", type datetime}, {"Year", Int64.Type}, {"QuarterNumber", Int64.Type}, {"Quarter", type text}, {"MonthNumber", Int64.Type}, {"Month", type text}, {"MonthShort", type text}, {"YearMonth", type text}, {"YearMonthSort", Int64.Type}, {"WeekOfYear", Int64.Type}, {"Day", Int64.Type}, {"DayOfWeekNumber", Int64.Type}, {"DayName", type text}, {"IsWeekend", type logical}}, "en-US")
in
    Typed