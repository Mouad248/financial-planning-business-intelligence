# Native refresh and SQL source modes

Run `py -3.13 scripts/open_native_report.py` from the project root, then choose Refresh in Power BI Desktop. The launcher configures a private machine-specific copy of the native project and preserves the neutral public source.

The native project retains the original report pages, DAX expressions, date table, model relationships and field parameters. Its full anonymous transaction/dimension snapshots are included. Budgets load from the original Excel planning input, and salesperson targets load from their original CSV. All imported tables were refreshed in the native engine and independently checked.

The original SQL mode is separate: restore Microsoft's Wide World Importers database, apply SQL files 00-06 and run 07_validate_bi_layer.sql, then use the SQL-source queries in powerbi/queries with ProjectRoot and SqlServerInstance parameters. Native snapshot verification does not establish SQL Server execution.

Do not distribute .private originals, raw exports or local .pbi caches. The public source project and complete anonymous inputs are the publication artifact.
