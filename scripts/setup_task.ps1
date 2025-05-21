$taskName = "FederalRegisterUpdate"
$taskPath = "K:\Environments\RAG_Agent\scripts\run_daily_update.bat"
$action = New-ScheduledTaskAction -Execute $taskPath
$trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the task (run as administrator)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force