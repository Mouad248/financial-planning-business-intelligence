let
    Source = Csv.Document(File.Contents(ProjectRoot & "\data\targets\Salesperson_Targets.csv"),[Delimiter=",", Columns=3, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"SalespersonID", Int64.Type}, {"Year", Int64.Type}, {"TargetAmount", Currency.Type}}),
    #"Added Custom" = Table.AddColumn(#"Changed Type", "Custom", each #date([Year], 1, 1)),
    #"Changed Type1" = Table.TransformColumnTypes(#"Added Custom",{{"Custom", type date}}),
    #"Renamed Columns" = Table.RenameColumns(#"Changed Type1",{{"Year", "Year"}, {"Custom", "TargetYearDate"}})
in
    #"Renamed Columns"