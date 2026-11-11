param(
    [Parameter(Mandatory=$true)][int]$Port,
    [Parameter(Mandatory=$true)][string]$ProjectDirectory,
    [switch]$Refresh
)
$ErrorActionPreference = 'Stop'
$bin = Join-Path (Get-AppxPackage 'Microsoft.MicrosoftPowerBIDesktop').InstallLocation 'bin'
foreach ($name in @('Microsoft.AnalysisServices.Server.Core.dll','Microsoft.AnalysisServices.Server.Tabular.dll','Microsoft.PowerBI.AdomdClient.dll')) {
    [void][System.Reflection.Assembly]::LoadFrom((Join-Path $bin $name))
}
$server = New-Object Microsoft.AnalysisServices.Tabular.Server
$server.Connect("localhost:$Port")
if ($server.Databases.Count -ne 1) { throw 'Expected one native report model' }
$database = $server.Databases[0]
if ($database.Model.Tables.Count -ne 14 -or $database.Model.Relationships.Count -ne 9) { throw 'Original model structure was not retained' }
if ($Refresh) {
    $database.Model.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
    $database.Model.SaveChanges() | Out-Null
    Write-Output 'Reconstructed native project refreshed successfully.'
}
$cases = Get-Content -LiteralPath (Join-Path $ProjectDirectory '.private/native-work/dax-checks.json') -Raw | ConvertFrom-Json
$reference = @{}
foreach ($case in $cases) { $reference[$case.name] = $case }
$connection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
$connection.ConnectionString = "Data Source=localhost:$Port;Initial Catalog=" + $database.Name
$connection.Open()
$results = @()
try {
    $command = $connection.CreateCommand()
    $command.CommandTimeout = 120
    $command.CommandText = Get-Content -LiteralPath (Join-Path $ProjectDirectory '.private/native-work/dax-checks.dax') -Raw
    $reader = $command.ExecuteReader()
    while ($reader.Read()) {
        $name = $reader.GetString(0)
        $case = $reference[$name]
        $actual = if ($reader.IsDBNull(1)) { $null } else { [decimal]$reader.GetValue(1) }
        if ($null -eq $case.expected) { $pass = $null -eq $actual }
        elseif ($null -eq $actual) { $pass = $false }
        else {
            $expected = [decimal]::Parse([string]$case.expected,[Globalization.NumberStyles]::Float,[cultureinfo]::InvariantCulture)
            $tolerance = [decimal]::Parse([string]$case.tolerance,[cultureinfo]::InvariantCulture)
            $pass = [Math]::Abs($actual - $expected) -le $tolerance
        }
        $results += [ordered]@{check=$name; actual=$actual; expected=$case.expected; passed=$pass}
    }
    $reader.Close()
    $failures = @($results | Where-Object {!$_.passed})
    $report = [ordered]@{engine='Native Power BI Desktop Analysis Services'; full_native_refresh=[bool]$Refresh; checks=$results.Count; passed=($results.Count-$failures.Count); failed=$failures.Count; tables=$database.Model.Tables.Count; relationships=$database.Model.Relationships.Count; results=$results}
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $ProjectDirectory 'reports/native_dax_verification.json') -Encoding UTF8
    Write-Output ('Native DAX checks: '+$report.passed+'/'+$report.checks+' passed')
    if ($failures.Count) { $failures | ConvertTo-Json; throw 'Native DAX regressions failed' }
} finally { $connection.Close(); $server.Disconnect() }
