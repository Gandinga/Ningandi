#takes arguments for actions 
param([string]$Action)

#gives me access to wndows system libraries
Add-Type -AssemblyName System.Runtime.WindowsRuntime

#converts WinRT async operations to .NET tasks for PowerShell
Function Await($WinRtTask, $ResultType) 
{
    $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

#core hotspot function
Function SetHotspot($Enable) 
{
    $connectionProfile = [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]::GetInternetConnectionProfile()      #grab current network connection and save it in connection profile
    $tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($connectionProfile)   #get hotspot controller object

    if ($Enable -eq 1) 
    {
        if ($tetheringManager.TetheringOperationalState -eq 1) 
        {
            "Hotspot is already On!"
        } 
        else 
        {
            "Turning hotspot on..."
            Await ($tetheringManager.StartTetheringAsync()) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])
        }
    } 
    
    else 
    {
        if ($tetheringManager.TetheringOperationalState -eq 2) 
        {
            "Hotspot is already Off!"
        } 
        
        else 
        {
            "Turning hotspot off..."
            Await ($tetheringManager.StopTetheringAsync()) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])
        }
    }
}
#forced the arguments to be uppercase internally
$Action = $Action.ToUpper()

#use arguments to turn on or off the hotspot
if ($Action -eq "ON") 
{
    SetHotspot(1)
} 

elseif ($Action -eq "OFF") 
{
    SetHotspot(0)
} 
#usage instructions if the parameter argument is wrong
else 
{
    Write-Host "Usage:"
    Write-Host "Turn on hotspot:  .\hotspot-start.ps1 on"
    Write-Host "Turn off hotspot: .\hotspot-start.ps1 off"
}

