@echo off

for /F "tokens=1,2 delims=: " %%A in ('WhoAmI /USER /FO LIST') do @if /I "%%~A" == "SID" set SID=%%B
for /F "tokens=8 delims=-" %%A in ("%temp%") do echo AIRFLOW_UID=%%A > ../.env