let
    // Dynamically find the first and last sales dates
    MinSalesDate = List.Min(FactSales[InvoiceDate]),
    MaxSalesDate = List.Max(FactSales[InvoiceDate]),

    // Expand to complete calendar years
    StartDate = #date(Date.Year(MinSalesDate), 1, 1),
    EndDate = #date(Date.Year(MaxSalesDate), 12, 31),

    // Create one row per calendar day
    NumberOfDays = Duration.Days(EndDate - StartDate) + 1,

    DateList =
        List.Dates(
            StartDate,
            NumberOfDays,
            #duration(1, 0, 0, 0)
        ),

    ToTable =
        Table.FromList(
            DateList,
            Splitter.SplitByNothing(),
            {"Date"}
        ),

    ChangeType =
        Table.TransformColumnTypes(
            ToTable,
            {{"Date", type date}}
        ),

    AddYear =
        Table.AddColumn(
            ChangeType,
            "Year",
            each Date.Year([Date]),
            Int64.Type
        ),

    AddQuarterNumber =
        Table.AddColumn(
            AddYear,
            "QuarterNumber",
            each Date.QuarterOfYear([Date]),
            Int64.Type
        ),

    AddQuarter =
        Table.AddColumn(
            AddQuarterNumber,
            "Quarter",
            each "Q" & Text.From([QuarterNumber]),
            type text
        ),

    AddMonthNumber =
        Table.AddColumn(
            AddQuarter,
            "MonthNumber",
            each Date.Month([Date]),
            Int64.Type
        ),

    AddMonth =
        Table.AddColumn(
            AddMonthNumber,
            "Month",
            each Date.MonthName([Date]),
            type text
        ),

    AddMonthShort =
        Table.AddColumn(
            AddMonth,
            "MonthShort",
            each Text.Start(Date.MonthName([Date]), 3),
            type text
        ),

    AddYearMonth =
        Table.AddColumn(
            AddMonthShort,
            "YearMonth",
            each
                Text.From([Year])
                & "-"
                & Text.PadStart(
                    Text.From([MonthNumber]),
                    2,
                    "0"
                ),
            type text
        ),

    AddYearMonthSort =
        Table.AddColumn(
            AddYearMonth,
            "YearMonthSort",
            each [Year] * 100 + [MonthNumber],
            Int64.Type
        ),

    AddWeek =
        Table.AddColumn(
            AddYearMonthSort,
            "WeekOfYear",
            each Date.WeekOfYear([Date], Day.Monday),
            Int64.Type
        ),

    AddDay =
        Table.AddColumn(
            AddWeek,
            "Day",
            each Date.Day([Date]),
            Int64.Type
        ),

    AddDayOfWeekNumber =
        Table.AddColumn(
            AddDay,
            "DayOfWeekNumber",
            each Date.DayOfWeek([Date], Day.Monday) + 1,
            Int64.Type
        ),

    AddDayName =
        Table.AddColumn(
            AddDayOfWeekNumber,
            "DayName",
            each Date.DayOfWeekName([Date]),
            type text
        ),

    AddIsWeekend =
        Table.AddColumn(
            AddDayName,
            "IsWeekend",
            each [DayOfWeekNumber] >= 6,
            type logical
        )

in
    AddIsWeekend