@echo off

:: Set path to Pro's python environment
set propy="C:/Program Files/ArcGIS/Pro/bin/Python/envs/arcgispro-py3/python.exe"

:: Path to this bat file to create relative paths
set scriptpath=%~dp0

set begintime=%TIME%

echo NEEDS SCRIPTS
echo -------------


echo(
echo Congestion Mitigation (1 of 13)
@REM %propy% "%scriptpath%Congestion Mitigation\congestion_mitigation.py"

echo(
echo Improved Reliability (Roadway) (2 of 13)
@REM %propy% "%scriptpath%Improved Reliability (Roadway)\identify_reliability_needs.py"


echo(
echo Improved Reliability (Intercity and Passenger Rail) (3 of 13)


echo(
echo Transportation Demand Management (TDM) (4 of 13)
%propy% "%scriptpath%Transportation Demand Management (TDM)\Identify_TDM_Needs.py"


echo(
echo Capacity Preservation (5 of 13)
@REM %propy% "%scriptpath%Capacity Preservation\Identify_Capacity_Needs.py"


echo(
echo Bike Access to Activity Centers (6 of 13)
@REM %propy% "%scriptpath%Need for Bicycle Access to Activity Centers\identify_bicycle_access_needs.py"


echo(
echo Walk Access to Activity Centers (7 of 13)
@REM %propy% "%scriptpath%Need for Pedestrian Access to Activity Centers\identify_pedestrian_access_needs.py"


echo(
echo Transit Access to Activity Centers (8 of 13)
@REM %propy% "%scriptpath%Need for Transit Access to Activity Centers\Transit_Access.py"


echo(
echo Transit Access for Equity Emphasis Areas (9 of 13)
%propy% "%scriptpath%Need for Transit Access for Equity Emphasis Areas\identify_transit_access_for_eea.py"


echo(
echo Roadway Safety (10 of 13)
@REM %propy% "%scriptpath%Roadway Safety\identify_roadway_safety_need.py"


echo(
echo Pedestrian Safety (11 of 13)
@REM %propy% "%scriptpath%Pedestrian Safety\identify_pedestrian_safety.py"


echo(
echo Access to Industrial and Economic Development Areas (IEDAs) (12 of 13)


echo(
echo UDA Needs (13 of 13)


echo(
echo CREATE FINAL NEEDS LAYER
%propy% "%scriptpath%Create Final Needs Layer\create_final_needs_layer.py"


echo(
echo Done
echo Begin Time: %begintime%
echo End Time: %TIME%
pause