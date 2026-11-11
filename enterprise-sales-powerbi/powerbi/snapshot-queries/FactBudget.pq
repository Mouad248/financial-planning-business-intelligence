let
    Source = Excel.Workbook(File.Contents(ProjectRoot & "\data\budget\Monthly_Budget.xlsx"), null, true),
    Sheet1_Sheet = Source{[Item="Sheet1",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(Sheet1_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Year", Int64.Type}, {"Jan", Currency.Type}, {"Feb", Currency.Type}, {"Mar", Currency.Type}, {"Apr", Currency.Type}, {"May", Currency.Type}, {"Jun", Currency.Type}, {"Jul", Currency.Type}, {"Aug", Currency.Type}, {"Sep", Currency.Type}, {"Oct", Currency.Type}, {"Nov", Currency.Type}, {"Dec", Currency.Type}, {"AnnualTotal", Currency.Type}}),
    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"AnnualTotal"}),
    #"Unpivoted Other Columns" = Table.UnpivotOtherColumns(#"Removed Columns", {"Year"}, "Attribute", "Value"),
    #"Renamed Columns" = Table.RenameColumns(#"Unpivoted Other Columns",{{"Attribute", "Month"}, {"Value", "BudgetAmount"}}),
    #"Added Custom" = Table.AddColumn(#"Renamed Columns", "BudgetMonth", each #date(
    [Year],
    List.PositionOf(
        {"Jan","Feb","Mar","Apr","May","Jun",
         "Jul","Aug","Sep","Oct","Nov","Dec"},
        [Month]
    ) + 1,
    1
)),
    #"Changed Type1" = Table.TransformColumnTypes(#"Added Custom",{{"BudgetMonth", type date}, {"BudgetAmount", Currency.Type}})
in
    #"Changed Type1"