# %% [markdown]
# # Need Category: Need for Transit Access to Activity Centers #
# 
# **Measure**: Transit Access to Activity Centers for Workers
# 
# **What it means**: Number of people that can access a given VTrans Activity Center via public transit versus a private
# automobile. VTrans Activity Centers are identified as “areas of regional importance that have a high density of economic
# and social activity” and are associated with the Regional Networks Travel Market. Activity Centers have been identified
# through stakeholder input.
# 
# **Applicable VTrans Travel Markets**: RN
# 
# **Year of analysis**: 2020

# %% [markdown]
# ### Code ###
# 
# The employment data was calculated by TMPD.  The script below makes use of that data to apply needs to the LRS.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# Paths to intermediate and output geodatabases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access to Activity Centers\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access to Activity Centers\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')

# Regional Networks polygon
RN = f'{common_datasets_gdb}\\RegionalNetworks'

# Overlap LRS
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# Functional Classification event table
TBL_FC = f'{common_datasets_gdb}\\tbl_fc23'

# Regional Networks event table
TBL_RN = f'{common_datasets_gdb}\\tbl_rn'

# Analysis results as an Activity Center point shapefile
AC_Results = f'{main_path}\\A1 - Common Datasets\\Need for Transit Access to Activity Centers\\data\\ActivityCenterShp\\Activity_Center 2023-09-14.shp'

# Transit commute time from census.  Must be downloaded using CreateTables.py before this script is run
Transit_Commute_Time = f'{main_path}\\A1 - Common Datasets\\Need for Transit Access to Activity Centers\\data\\output.gdb\\Transit_Commute_Time'

# %%
# Join county level census data on Means of Transprotation to Work to RNs

# Spatial Join counties to RNs
RN_Spatial_Join = os.path.join(intermediate_gdb, 'RN_Spatial_Join')
arcpy.analysis.SpatialJoin(RN, Transit_Commute_Time, RN_Spatial_Join, "JOIN_ONE_TO_MANY", "KEEP_ALL", 'RN_Name "Name" true true false 254 Text 0 0,First,#,RegionalNetworks,RN_Name,0,254;Includes "Includes Counties/Cities Of" true true false 254 Text 0 0,First,#,RegionalNetworks,Includes,0,254;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,RegionalNetworks,Shape_Length,-1,-1,Transit_Commute_Time,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,RegionalNetworks,Shape_Area,-1,-1,Transit_Commute_Time,Shape_Area,-1,-1;COUNTYNS "COUNTYNS" true true false 8 Text 0 0,First,#,Transit_Commute_Time,COUNTYNS,0,8;GEO_ID "GEOID" true true false 5 Text 0 0,First,#,Transit_Commute_Time,GEO_ID,0,5;NAMELSAD "NAMELSAD" true true false 100 Text 0 0,First,#,Transit_Commute_Time,NAMELSAD,0,100;CLASSFP "CLASSFP" true true false 2 Text 0 0,First,#,Transit_Commute_Time,CLASSFP,0,2;FUNCSTAT "FUNCSTAT" true true false 1 Text 0 0,First,#,Transit_Commute_Time,FUNCSTAT,0,1;ALAND "ALAND" true true false 8 Double 0 0,First,#,Transit_Commute_Time,ALAND,-1,-1;AWATER "AWATER" true true false 8 Double 0 0,First,#,Transit_Commute_Time,AWATER,-1,-1;INTPTLAT "INTPTLAT" true true false 11 Text 0 0,First,#,Transit_Commute_Time,INTPTLAT,0,11;INTPTLON "INTPTLON" true true false 12 Text 0 0,First,#,Transit_Commute_Time,INTPTLON,0,12;B08134_061E "Estimate!!Total:!!Public transportation (excluding taxicab)" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_061E,-1,-1;B08134_062E "LT 10 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_062E,-1,-1;B08134_063E "10-14 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_063E,-1,-1;B08134_064E "15-19 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_064E,-1,-1;B08134_065E "20-24 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_065E,-1,-1;B08134_066E "25-29 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_066E,-1,-1;B08134_067E "30-34 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_067E,-1,-1;B08134_068E "35-44 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_068E,-1,-1;B08134_069E "45-59 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_069E,-1,-1;B08134_070E "GT 60 min" true true false 4 Long 0 0,First,#,Transit_Commute_Time,B08134_070E,-1,-1', "INTERSECT", None, '')

# Dissolve spatial join, summing all statistics
RN_Commute_Times = os.path.join(intermediate_gdb, 'RN_Commute_Times')
arcpy.management.Dissolve(RN_Spatial_Join, RN_Commute_Times, "RN_Name", "B08134_061E SUM;B08134_062E SUM;B08134_063E SUM;B08134_064E SUM;B08134_065E SUM;B08134_066E SUM;B08134_067E SUM;B08134_068E SUM;B08134_069E SUM;B08134_070E SUM", "MULTI_PART", "DISSOLVE_LINES")

# %%
# Convert commute times by RN to dataframe
commute_time_fields = [field.name for field in arcpy.ListFields(RN_Commute_Times) if field.name not in ('OBJECTID', 'Shape', 'Shape_Length', 'Shape_Area')]
field_aliases = [
        'RN Name', 
        'Estimate!!Total:!!Public transportation (excluding taxicab)',
        'LT 10 min',
        '10-14 min',
        '15-19 min',
        '20-24 min',
        '25-29 min',
        '30-34 min',
        '35-44 min',
        '45-59 min',
        'GT 60 min'
    ]
df_rn_commute_times = pd.DataFrame([row for row in arcpy.da.SearchCursor(RN_Commute_Times, commute_time_fields)], columns=field_aliases)

# %%
# Identify the median transit commute time as the midpoint of the travel time bin containing the 50th percentile transit commuter
df_rn_commute_times['mid-commuter'] = df_rn_commute_times['Estimate!!Total:!!Public transportation (excluding taxicab)']/2

# %%


# Cumulative Buckets
df_rn_commute_times['C LT 10'] = df_rn_commute_times['LT 10 min']
df_rn_commute_times['C 10-14'] = df_rn_commute_times['C LT 10'] + df_rn_commute_times['10-14 min']
df_rn_commute_times['C 15-19'] = df_rn_commute_times['C 10-14'] + df_rn_commute_times['15-19 min']
df_rn_commute_times['C 20-24'] = df_rn_commute_times['C 15-19'] + df_rn_commute_times['20-24 min']
df_rn_commute_times['C 25-29'] = df_rn_commute_times['C 20-24'] + df_rn_commute_times['25-29 min']
df_rn_commute_times['C 30-34'] = df_rn_commute_times['C 25-29'] + df_rn_commute_times['30-34 min']
df_rn_commute_times['C 35-44'] = df_rn_commute_times['C 30-34'] + df_rn_commute_times['35-44 min']
df_rn_commute_times['C 45-59'] = df_rn_commute_times['C 35-44'] + df_rn_commute_times['45-59 min']
df_rn_commute_times['C GT 60'] = df_rn_commute_times['C 45-59'] + df_rn_commute_times['GT 60 min']


bucket_median_dict = {
    'LT 10 min': 5,
    '10-14 min': 12,
    '15-19 min': 17,
    '20-24 min': 22,
    '25-29 min': 27,
    '30-34 min': 32,
    '35-44 min': 40,
    '45-59 min': 52,
    'GT 60 min': 65
}

def get_median(row):   
    mid_commuter = row['mid-commuter']

    if mid_commuter < row['C LT 10']:
        return 'LT 10 min'
    if mid_commuter >= row['C LT 10'] and mid_commuter < row['C 10-14']:
        return '10-14 min'
    if mid_commuter >= row['C 10-14'] and mid_commuter < row['C 15-19']:
        return '15-19 min'
    if mid_commuter >= row['C 15-19'] and mid_commuter < row['C 20-24']:
        return '20-24 min'
    if mid_commuter >= row['C 20-24'] and mid_commuter < row['C 25-29']:
        return '25-29 min'
    if mid_commuter >= row['C 25-29'] and mid_commuter < row['C 30-34']:
        return '30-34 min'
    if mid_commuter >= row['C 30-34'] and mid_commuter < row['C 35-44']:
        return '35-44 min'
    if mid_commuter >= row['C 35-44'] and mid_commuter < row['C 45-59']:
        return '45-59 min'

    return 'GT 60 min'

df_rn_commute_times['median commute time bucket'] = df_rn_commute_times.apply(get_median, axis=1)

df_rn_commute_times['median commute time'] = df_rn_commute_times.apply(lambda x: bucket_median_dict[x['median commute time bucket']], axis=1)

# %%
# Convert the value to a distance by multiplying it by the average travel speed of a bus (12 mph).
df_rn_commute_times['distance'] = (df_rn_commute_times['median commute time'] / 60) * 12

# Create a dictionary containing the RN Name: buffer distance calculated above
buffer_distance_dict = df_rn_commute_times[['RN Name', 'distance']].set_index('RN Name').to_dict()['distance']

# %%
# Spatial join ACs with RNs
AC_Spatial_Join = os.path.join(intermediate_gdb, 'AC_Spatial_Join')
arcpy.analysis.SpatialJoin(AC_Results, RN, AC_Spatial_Join, "JOIN_ONE_TO_ONE", "KEEP_ALL", 'ID "ID" true true false 10 Long 0 10,First,#,Activity_Center 2023-09-14,ID,-1,-1;OBJECTID "OBJECTID" true true false 10 Long 0 10,First,#,Activity_Center 2023-09-14,OBJECTID,-1,-1;ACTVTYC "ACTVTYC" true true false 80 Text 0 0,First,#,Activity_Center 2023-09-14,ACTVTYC,0,80;REGION "REGION" true true false 80 Text 0 0,First,#,Activity_Center 2023-09-14,REGION,0,80;C000 "C000" true true false 19 Double 11 18,First,#,Activity_Center 2023-09-14,C000,-1,-1;PRMRY_C "PRMRY_C" true true false 80 Text 0 0,First,#,Activity_Center 2023-09-14,PRMRY_C,0,80;SH_FREG "SH_FREG" true true false 19 Double 11 18,First,#,Activity_Center 2023-09-14,SH_FREG,-1,-1;SH_LOCL "SH_LOCL" true true false 19 Double 11 18,First,#,Activity_Center 2023-09-14,SH_LOCL,-1,-1;SH_KNWL "SH_KNWL" true true false 19 Double 11 18,First,#,Activity_Center 2023-09-14,SH_KNWL,-1,-1;DISTRICT "DISTRICT" true true false 64 Text 0 0,First,#,Activity_Center 2023-09-14,DISTRICT,0,64;POP20_AUTO "POP20_AUTO" true true false 10 Double 2 9,First,#,Activity_Center 2023-09-14,POP20_AUTO,-1,-1;CNT_AUTO "CNT_AUTO" true true false 8 Long 0 8,First,#,Activity_Center 2023-09-14,CNT_AUTO,-1,-1;POP20_TRAN "POP20_TRAN" true true false 10 Double 2 9,First,#,Activity_Center 2023-09-14,POP20_TRAN,-1,-1;CNT_TRANSI "CNT_TRANSI" true true false 8 Long 0 8,First,#,Activity_Center 2023-09-14,CNT_TRANSI,-1,-1;ACCESS_DIF "ACCESS_DIF" true true false 10 Double 2 9,First,#,Activity_Center 2023-09-14,ACCESS_DIF,-1,-1;EMP20 "EMP20" true true false 10 Double 2 9,First,#,Activity_Center 2023-09-14,EMP20,-1,-1;DIFFPOP_EM "DIFFPOP_EM" true true false 10 Double 2 9,First,#,Activity_Center 2023-09-14,DIFFPOP_EM,-1,-1;RN_Name "Name" true true false 254 Text 0 0,First,#,RegionalNetworks,RN_Name,0,254;Includes "Includes Counties/Cities Of" true true false 254 Text 0 0,First,#,RegionalNetworks,Includes,0,254;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,RegionalNetworks,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,RegionalNetworks,Shape_Area,-1,-1', "INTERSECT", None, '')

# Create a dictionary containing the AC ID: RN Name
ac_rn_dict = {row[0]:row[1] for row in arcpy.da.SearchCursor(AC_Spatial_Join, ['ID', 'RN_Name'])}

# %%
# Add RN_Name and Buffer_Distance fields to ACs if it does not yet exist
AC_Fields = [field.name for field in arcpy.ListFields(AC_Results)]
if 'RN_Name' not in AC_Fields:
    arcpy.AddField_management(AC_Results, 'RN_Name', 'TEXT')
if 'Buffer_Dis' not in AC_Fields:
    arcpy.AddField_management(AC_Results, 'Buffer_Dis', 'TEXT')

# Caclulate the RN_Name and Buffer_Distance fields based on dictionaries created above
with arcpy.da.UpdateCursor(AC_Results, ['ID', 'RN_Name', 'Buffer_Dis']) as cur:
    for row in cur:
        rn_name = ac_rn_dict.get(row[0]) if ac_rn_dict.get(row[0]) else 'None'
        buffer_distance = buffer_distance_dict.get(rn_name)

        row[1] = rn_name

        if rn_name == 'None':
            row[2] = '5.4 MILES'
        else:
            row[2] = f'{buffer_distance} MILES'

        cur.updateRow(row)

# %%
# Buffer ACs on Buffer_Dis
AC_Buffer = os.path.join(intermediate_gdb, 'AC_Buffer')
arcpy.Buffer_analysis(AC_Results, AC_Buffer, 'Buffer_Dis')

# %%
# Identify ACs that meet threshold - Activity Centers, where fewer population can access the
# Activity Center within 45 minutes by transit than by automobile are identified as those with a VTrans Mid-term Need for
# Transit Access to Activity Centers.

# POP20_AUTO - Population access to AC within 45 min by auto 
# POP20_TRAN - Population access to AC within 45 min by transit

if 'need' not in [field.name for field in arcpy.ListFields(AC_Buffer)]:
    arcpy.AddField_management(AC_Buffer, 'need', 'TEXT')

with arcpy.da.UpdateCursor(AC_Buffer, ['POP20_AUTO', 'POP20_TRAN', 'need']) as cur:
    for row in cur:
        if row[1] < row[0]:
            row[2] = 'YES'
        else:
            row[2] = 'NO'

        cur.updateRow(row)

# Export only buffered ACs where need = 'YES'
AC_Buffer_w_Need = os.path.join(intermediate_gdb, 'AC_Buffer_w_Need')
arcpy.FeatureClassToFeatureClass_conversion(AC_Buffer, intermediate_gdb, 'AC_Buffer_w_Need', "need = 'YES'")

AC_Buffer_w_Need_Dissolved = os.path.join(intermediate_gdb, 'AC_Buffer_w_Need_Dissolved')
arcpy.Dissolve_management(AC_Buffer_w_Need, AC_Buffer_w_Need_Dissolved)

# %%
# Use the Functional Classification layer as a base for segmentation.  Then clip by AC_Buffer to determine the needs

# Make FC route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", TBL_FC, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_fc Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_fc Events", intermediate_gdb, "tbl_fc_events")
tbl_fc_events = os.path.join(intermediate_gdb, 'tbl_fc_events')

# Clip tbl_fc_events by buffer
fc_ac_buffer = os.path.join(intermediate_gdb, 'fc_ac_buffer')
arcpy.PairwiseClip_analysis(tbl_fc_events, AC_Buffer_w_Need_Dissolved, fc_ac_buffer)

# Recalculate begin and end measures
fc_ac_buffer_singlepart = os.path.join(intermediate_gdb, 'fc_ac_buffer_singlepart')
arcpy.MultipartToSinglepart_management(fc_ac_buffer, fc_ac_buffer_singlepart)
with arcpy.da.UpdateCursor(fc_ac_buffer_singlepart, ['SHAPE@', 'BEGIN_MSR', 'END_MSR']) as cur:
    for row in cur:
        geom = row[0]
        begin_msr = geom.firstPoint.M
        end_msr = geom.lastPoint.M
        row[1] = begin_msr
        row[2] = end_msr
        cur.updateRow(row)

# %%
# Clean up needs event table in Pandas
transit_access_fields = [field.name for field in arcpy.ListFields(fc_ac_buffer_singlepart) if field.name not in ('OBJECTID', 'Shape', 'ORIG_FID', 'Shape_Length')]
df_transit_access = pd.DataFrame([row for row in arcpy.da.SearchCursor(fc_ac_buffer_singlepart, transit_access_fields)], columns=transit_access_fields)
df_transit_access['RN_AC_Transit_Access'] = 'YES'

# Filter out ramps and non-local functional classification
df_transit_access = df_transit_access.loc[df_transit_access['STATE_FUNCT_CLASS_ID'] < 7]
df_transit_access.drop(columns='STATE_FUNCT_CLASS_ID', axis=1, inplace=True)
df_transit_access

# %%
# Create final output
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df_transit_access.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_transit_access')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_transit_access Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_transit_access Events", output_gdb, "Transit_Access")

# %%



