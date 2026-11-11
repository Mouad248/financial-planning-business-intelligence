param(
    [Parameter(Mandatory=$true)][int]$Port,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $PSScriptRoot 'export_csv.cs') -ReferencedAssemblies System.Data
$bin = Join-Path (Get-AppxPackage 'Microsoft.MicrosoftPowerBIDesktop').InstallLocation 'bin'
foreach ($name in @('Microsoft.AnalysisServices.Server.Core.dll','Microsoft.AnalysisServices.Server.Tabular.dll','Microsoft.PowerBI.AdomdClient.dll')) {
    [void][System.Reflection.Assembly]::LoadFrom((Join-Path $bin $name))
}
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$Port")
$deadline = (Get-Date).AddSeconds(45)
while ($server.Databases.Count -eq 0 -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 750
    $server.Disconnect()
    $server.Connect("localhost:$Port")
}
if ($server.Databases.Count -ne 1) { throw 'Expected exactly one report model' }
$database = $server.Databases[0]
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
$connection.ConnectionString = "Data Source=localhost:$Port;Initial Catalog=" + $database.Name
$connection.Open()
$counts = [ordered]@{}
try {
    foreach ($table in $database.Model.Tables) {
        if ($table.Name -eq '_Measures' -or $table.Partitions[0].Source.GetType().Name -ne 'MPartitionSource') { continue }
        $columns = @($table.Columns | Where-Object { $_.Type.ToString() -ne 'RowNumber' })
        $tableName = $table.Name.Replace("'", "''")
        $selections = @($columns | ForEach-Object { '"' + $_.Name.Replace('"','""') + '", ' + "'$tableName'[" + $_.Name.Replace(']',']]') + ']' })
        $command = $connection.CreateCommand()
        $command.CommandText = "EVALUATE SELECTCOLUMNS('$tableName', " + ($selections -join ', ') + ')'
        $reader = $command.ExecuteReader()
        try {
            $count = [NativeModelCsv]::Export($reader, (Join-Path $OutputDirectory ($table.Name + '.csv')), [string[]]@($columns | ForEach-Object { $_.Name }))
        } finally { $reader.Close() }
        $counts[$table.Name] = $count
        Write-Output ($table.Name + ': ' + $count + ' rows exported privately')
    }
    $counts | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'counts.json') -Encoding UTF8
} finally { $connection.Close(); $server.Disconnect() }
