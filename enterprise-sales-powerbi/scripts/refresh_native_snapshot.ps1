param(
    [Parameter(Mandatory=$true)][int]$Port,
    [Parameter(Mandatory=$true)][string]$ProjectDirectory,
    [switch]$PublishPlaceholder
)
$ErrorActionPreference = 'Stop'
$bin = Join-Path (Get-AppxPackage 'Microsoft.MicrosoftPowerBIDesktop').InstallLocation 'bin'
foreach ($name in @('Microsoft.AnalysisServices.Server.Core.dll','Microsoft.AnalysisServices.Server.Tabular.dll','Microsoft.PowerBI.AdomdClient.dll')) {
    [void][System.Reflection.Assembly]::LoadFrom((Join-Path $bin $name))
}
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$Port")
if ($server.Databases.Count -ne 1) { throw 'Expected one report model' }
$database = $server.Databases[0]
if ($database.Model.Tables.Count -ne 14 -or $database.Model.Relationships.Count -ne 9) { throw 'Unexpected semantic model' }
$parameter = $database.Model.Expressions.Find('ProjectRoot')
if (!$parameter) {
    $parameter = New-Object Microsoft.AnalysisServices.Tabular.NamedExpression
    $parameter.Name = 'ProjectRoot'
    $parameter.Kind = [Microsoft.AnalysisServices.Tabular.ExpressionKind]::M
    $database.Model.Expressions.Add($parameter)
}
$root = if ($PublishPlaceholder) { 'C:\Projects\EnterpriseSales' } else { [System.IO.Path]::GetFullPath($ProjectDirectory) }
$parameter.Expression = '"' + $root.Replace('"','""') + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
if (!$PublishPlaceholder) {
    $sources = Get-Content -LiteralPath (Join-Path $ProjectDirectory '.private/native-work/snapshot-partitions.json') -Raw | ConvertFrom-Json
    foreach ($property in $sources.PSObject.Properties) {
        $table = $database.Model.Tables.Find($property.Name)
        if (!$table -or $table.Partitions.Count -ne 1) { throw ('Unexpected partition layout: '+$property.Name) }
        $source = New-Object Microsoft.AnalysisServices.Tabular.MPartitionSource
        $source.Expression = [string]$property.Value
        $table.Partitions[0].Source = $source
    }
    $order = $database.Model.Annotations.Find('PBI_QueryOrder')
    if ($order) {
        $names = @($order.Value | ConvertFrom-Json)
        if ($names -notcontains 'ProjectRoot') { $order.Value = ConvertTo-Json -InputObject (@('ProjectRoot') + $names) -Compress }
    }
    $database.Model.SaveChanges() | Out-Null
    Write-Output 'Native CSV partitions applied; refreshing the original model.'
    $database.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
}
$database.Model.SaveChanges() | Out-Null
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
$connection.ConnectionString = "Data Source=localhost:$Port;Initial Catalog=" + $database.Name
$connection.Open()
try {
    $command = $connection.CreateCommand()
    $command.CommandText = 'EVALUATE ROW("Revenue", [Revenue], "GrossProfit", [Gross Profit], "FactRows", COUNTROWS(FactSales), "Customers", COUNTROWS(DimCustomer), "Salespeople", COUNTROWS(DimSalesperson))'
    $reader = $command.ExecuteReader()
    $result = [ordered]@{}
    if ($reader.Read()) { for ($i=0;$i -lt $reader.FieldCount;$i++) { $result[$reader.GetName($i)] = $reader.GetValue($i) } }
    $reader.Close()
    $result | ConvertTo-Json
    $result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $ProjectDirectory '.private/native-work/after-refresh.json') -Encoding UTF8
    $json = [Microsoft.AnalysisServices.Tabular.JsonSerializer]::SerializeDatabase($database)
    $file = if ($PublishPlaceholder) { 'publication-model.json' } else { 'refreshed-model.json' }
    [System.IO.File]::WriteAllText((Join-Path $ProjectDirectory ('.private/native-work/' + $file)), $json)
} finally { $connection.Close(); $server.Disconnect() }
