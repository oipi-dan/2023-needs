import arcpy
import pandas as pd
import os

from field_schema import FIELD_ALIAS, FIELD_TYPE
FIELDS = list(FIELD_ALIAS.keys())
NEEDS_FIELDS = FIELDS[19:]
main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

arcpy.env.overwriteOutput = True


class Field:
  def __init__(self, name, alias, type):
    self.name = name
    self.alias = alias
    self.type = type


lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# Create databases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Create Final Needs Layer\\intermediate.gdb"
if not os.path.exists(intermediate_gdb):
    arcpy.CreateFileGDB_management(os.path.dirname(intermediate_gdb), os.path.basename(intermediate_gdb))

output_gdb = f"{main_path}\\2023_VTrans_MidTerm_Needs.gdb"
if not os.path.exists(output_gdb):
    arcpy.CreateFileGDB_management(os.path.dirname(output_gdb), os.path.basename(output_gdb))


# Needs event tables
source_Congestion = f"{main_path}\\A1 - Common Datasets\\Congestion Mitigation\\data\\output.gdb\\tbl_congestion_mitigation"
source_Reliability = f"{main_path}\\A1 - Common Datasets\\Improved Reliability (Roadway)\\data\\output.gdb\\tbl_reliability"
source_CoSS_Rail_Reliability = f"{main_path}\\A1 - Common Datasets\\Improved Reliability (Intercity and Passenger Rail)\\data\\output.gdb\\tbl_rail_reliability"
source_Capacity_Preservation = f"{main_path}\\A1 - Common Datasets\\Capacity Preservation\\data\\output.gdb\\tbl_capacity_preservation"
source_TDM = f"{main_path}\\A1 - Common Datasets\\Transportation Demand Management (TDM)\\data\\output.gdb\\tbl_tdm_needs"
source_Safety_Intersection = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\output.gdb\\tbl_safety_intersections"
source_Safety_Segments = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\output.gdb\\tbl_safety_segment"
source_RN_AC_Bicycle_Access = f"{main_path}\\A1 - Common Datasets\\Need for Bicycle Access to Activity Centers\\data\\output.gdb\\tbl_bicycle_access"
source_RN_AC_Pedestrian_Access = f"{main_path}\\A1 - Common Datasets\\Need for Pedestrian Access to Activity Centers\\data\\output.gdb\\tbl_ped_access"
source_RN_AC_Transit_Access = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access to Activity Centers\\data\\output.gdb\\tbl_transit_access"
source_RN_Transit_Emphasis = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access for Equity Emphasis Areas\\data\\output.gdb\\tbl_transit_access_eaa"
source_RN_Safety_Pedestrian = f"{main_path}\\A1 - Common Datasets\\Pedestrian Safety\\data\\output.gdb\\tbl_ped_safety"
source_RN_VEDP_Business_Ready_Site = f"{main_path}\\A1 - Common Datasets\\Access to Industrial and Economic Development Areas (IEDAs)\\data\\output.gdb\\tbl_vedp"
source_UDA = f"{main_path}\\A1 - Common Datasets\\Urban Development Areas (UDAs) Needs\\data\\output.gdb\\tbl_uda_needs"

# CoSS and FC event tables
source_CoSS = f"{common_datasets_gdb}\\CoSS_2023"
source_CoSS = f"{common_datasets_gdb}\\tbl_coss_2023_01252024"
source_CoSS = f"{common_datasets_gdb}\\tbl_coss_2023"
source_FC = f"{common_datasets_gdb}\\tbl_fc23"

# Other datasets
VDOT_Districts = f'{common_datasets_gdb}\\VDOT_Districts'
VDOT_Jurisdictions = f'{common_datasets_gdb}\\County_and_City'
MPOs = f'{common_datasets_gdb}\MPO'
Census_Urban_Areas = f'{main_path}\\A1 - Common Datasets\\tl_rd22_51_place.shp'
RNs = f'{common_datasets_gdb}\\RegionalNetworks'
UDAs = f'{common_datasets_gdb}\\UrbanDevelopmentAreas'

# Prepare CoSS - in order for the join to work, a version of the coss with matching field names needs to be created.  This will
# be used to join to the final output table
prepared_CoSS = os.path.join(intermediate_gdb, 'CoSS')
arcpy.CreateTable_management(intermediate_gdb, 'CoSS')
arcpy.AddField_management(prepared_CoSS, 'RTE_NM', 'TEXT')
arcpy.AddField_management(prepared_CoSS, 'BEGIN_MSR', 'DOUBLE')
arcpy.AddField_management(prepared_CoSS, 'END_MSR', 'DOUBLE')
arcpy.AddField_management(prepared_CoSS, 'CoSS', 'TEXT')
arcpy.AddField_management(prepared_CoSS, 'CoSS_Primary', 'TEXT')
arcpy.AddField_management(prepared_CoSS, 'CoSS_Name', 'TEXT')

# Get CoSS data from source
source_CoSS_fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'COSS_NAME', 'Primary']
CoSS_data = [row for row in arcpy.da.SearchCursor(source_CoSS, source_CoSS_fields)]

# Add CoSS data to prepared_CoSS table
prepared_CoSS_fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'CoSS', 'CoSS_Primary', 'CoSS_Name']
with arcpy.da.InsertCursor(prepared_CoSS, prepared_CoSS_fields) as cur:
    for rte_nm, begin_msr, end_msr, coss_name, primary in CoSS_data:
        record_data = (rte_nm, begin_msr, end_msr, 'YES', primary, coss_name)
        cur.insertRow(record_data)
        

# Prepare FC
prepared_FC = os.path.join(intermediate_gdb, 'FC')
arcpy.CreateTable_management(intermediate_gdb, 'FC')
arcpy.AddField_management(prepared_FC, 'RTE_NM', 'TEXT')
arcpy.AddField_management(prepared_FC, 'BEGIN_MSR', 'DOUBLE')
arcpy.AddField_management(prepared_FC, 'END_MSR', 'DOUBLE')
arcpy.AddField_management(prepared_FC, 'VDOT_FC', 'TEXT')

# Get FC data from source
source_FC_fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'STATE_FUNCT_CLASS_ID']
FC_data = [row for row in arcpy.da.SearchCursor(source_FC, source_FC_fields)]

# Add FC data to prepared_FC table
prepared_FC_fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'VDOT_FC']
with arcpy.da.InsertCursor(prepared_FC, prepared_FC_fields) as cur:
    for rte_nm, begin_msr, end_msr, vdot_fc in FC_data:
        record_data = (rte_nm, begin_msr, end_msr, str(vdot_fc))
        cur.insertRow(record_data)


# Join event tables
print('Creating initial table\n')
initial_table = os.path.join(intermediate_gdb, 'initial_table')
arcpy.CreateTable_management(os.path.dirname(initial_table), os.path.basename(initial_table))
arcpy.AddField_management(initial_table, 'RTE_NM', 'TEXT')
arcpy.AddField_management(initial_table, 'BEGIN_MSR', 'DOUBLE')
arcpy.AddField_management(initial_table, 'END_MSR', 'DOUBLE')

# Arcpy only allows you to overlap two tables at a time
# Output paths for intermediate event tables:
overlay_CoSS = os.path.join(intermediate_gdb, 'overlay_CoSS')
overlay_FC = os.path.join(intermediate_gdb, 'overlay_FC')
overlay_Congestion = os.path.join(intermediate_gdb, 'overlay_Congestion')
overlay_Reliability = os.path.join(intermediate_gdb, 'overlay_Reliability')
overlay_CoSS_Rail_Reliability = os.path.join(intermediate_gdb, 'overlay_CoSS_Rail_Reliability')
overlay_Capacity_Preservation = os.path.join(intermediate_gdb, 'overlay_Capacity_Preservation')
overlay_TDM = os.path.join(intermediate_gdb, 'overlay_TDM')
overlay_Safety_Intersection = os.path.join(intermediate_gdb, 'overlay_Safety_Intersection')
overlay_Safety_Segments = os.path.join(intermediate_gdb, 'overlay_Safety_Segments')
overlay_RN_AC_Bicycle_Access = os.path.join(intermediate_gdb, 'overlay_RN_AC_Bicycle_Access')
overlay_RN_AC_Pedestrian_Access = os.path.join(intermediate_gdb, 'overlay_RN_AC_Pedestrian_Access')
overlay_RN_AC_Transit_Access = os.path.join(intermediate_gdb, 'overlay_RN_AC_Transit_Access')
overlay_RN_Transit_Emphasis = os.path.join(intermediate_gdb, 'overlay_RN_Transit_Emphasis')
overlay_RN_Safety_Pedestrian = os.path.join(intermediate_gdb, 'overlay_RN_Safety_Pedestrian')
overlay_RN_VEDP_Business_Ready_Site = os.path.join(intermediate_gdb, 'overlay_RN_VEDP_Business_Ready_Site')
overlay_UDA = os.path.join(intermediate_gdb, 'overlay_UDA')
all_needs_overlapped = os.path.join(intermediate_gdb, 'all_needs_overlapped')

# Ensure that the from/to measures for all input event tables are rounded.  Otherwise the overlay tool will create zero length events
print('Rounding Measures')
source_tables = [prepared_CoSS, prepared_FC, source_Congestion,source_Reliability,source_CoSS_Rail_Reliability,source_Capacity_Preservation,source_TDM,source_Safety_Intersection,source_Safety_Segments,source_RN_AC_Bicycle_Access,source_RN_AC_Pedestrian_Access,source_RN_AC_Transit_Access,source_RN_Transit_Emphasis,source_RN_Safety_Pedestrian,source_RN_VEDP_Business_Ready_Site,source_UDA]
for table in source_tables:
    if table is not None:
        with arcpy.da.UpdateCursor(table, ['BEGIN_MSR', 'END_MSR']) as cur:
            for row in cur:
                row[0] = round(row[0], 2)
                row[1] = round(row[1], 2)
                cur.updateRow(row)


print('Overlaying prepared_CoSS')
if source_Congestion:
    arcpy.lr.OverlayRouteEvents(initial_table, 'RTE_NM LINE BEGIN_MSR END_MSR', prepared_CoSS, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_CoSS, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(initial_table, intermediate_gdb, 'overlay_CoSS')

print('Overlaying prepared_FC')
if source_Congestion:
    arcpy.lr.OverlayRouteEvents(overlay_CoSS, 'RTE_NM LINE BEGIN_MSR END_MSR', prepared_FC, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_FC, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_CoSS, intermediate_gdb, 'overlay_FC')

print('Overlaying source_Congestion')
if source_Congestion:
    arcpy.lr.OverlayRouteEvents(overlay_FC, 'RTE_NM LINE BEGIN_MSR END_MSR', source_Congestion, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_Congestion, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_FC, intermediate_gdb, 'overlay_congestion')

print('Overlaying source_Reliability')
if source_Reliability:
    arcpy.lr.OverlayRouteEvents(overlay_Congestion, 'RTE_NM LINE BEGIN_MSR END_MSR', source_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_Congestion, intermediate_gdb, 'overlay_Reliability')

print('Overlaying source_CoSS_Rail_Reliability')
if source_CoSS_Rail_Reliability:
    arcpy.lr.OverlayRouteEvents(overlay_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', source_CoSS_Rail_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_CoSS_Rail_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_Reliability, intermediate_gdb, 'overlay_CoSS_Rail_Reliability')

print('Overlaying source_Capacity_Preservation')
if source_Capacity_Preservation:
    arcpy.lr.OverlayRouteEvents(overlay_CoSS_Rail_Reliability, 'RTE_NM LINE BEGIN_MSR END_MSR', source_Capacity_Preservation, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_Capacity_Preservation, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_CoSS_Rail_Reliability, intermediate_gdb, 'overlay_Capacity_Preservation')

print('Overlaying source_TDM')
if source_TDM:
    arcpy.lr.OverlayRouteEvents(overlay_Capacity_Preservation, 'RTE_NM LINE BEGIN_MSR END_MSR', source_TDM, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_TDM, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_Capacity_Preservation, intermediate_gdb, 'overlay_TDM')

print('Overlaying source_Safety_Intersection')
if source_Safety_Intersection:
    arcpy.lr.OverlayRouteEvents(overlay_TDM, 'RTE_NM LINE BEGIN_MSR END_MSR', source_Safety_Intersection, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_Safety_Intersection, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_TDM, intermediate_gdb, 'overlay_Safety_Intersection')

print('Overlaying source_Safety_Segments')
if source_Safety_Segments:
    arcpy.lr.OverlayRouteEvents(overlay_Safety_Intersection, 'RTE_NM LINE BEGIN_MSR END_MSR', source_Safety_Segments, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_Safety_Segments, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_Safety_Intersection, intermediate_gdb, 'overlay_Safety_Segments')

print('Overlaying source_RN_AC_Bicycle_Access')
if source_RN_AC_Bicycle_Access:
    arcpy.lr.OverlayRouteEvents(overlay_Safety_Segments, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_AC_Bicycle_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_AC_Bicycle_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_Safety_Segments, intermediate_gdb, 'overlay_RN_AC_Bicycle_Access')

print('Overlaying source_RN_AC_Pedestrian_Access')
if source_RN_AC_Pedestrian_Access:
    arcpy.lr.OverlayRouteEvents(overlay_RN_AC_Bicycle_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_AC_Pedestrian_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_AC_Pedestrian_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_AC_Bicycle_Access, intermediate_gdb, 'overlay_RN_AC_Pedestrian_Access')

print('Overlaying source_RN_AC_Transit_Access')
if source_RN_AC_Transit_Access:
    arcpy.lr.OverlayRouteEvents(overlay_RN_AC_Pedestrian_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_AC_Transit_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_AC_Transit_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_AC_Pedestrian_Access, intermediate_gdb, 'overlay_RN_AC_Transit_Access')

print('Overlaying source_RN_Transit_Emphasis')
if source_RN_Transit_Emphasis:
    arcpy.lr.OverlayRouteEvents(overlay_RN_AC_Transit_Access, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_Transit_Emphasis, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_Transit_Emphasis, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_AC_Transit_Access, intermediate_gdb, 'overlay_RN_Transit_Emphasis')

print('Overlaying source_RN_Safety_Pedestrian')
if source_RN_Safety_Pedestrian:
    arcpy.lr.OverlayRouteEvents(overlay_RN_Transit_Emphasis, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_Safety_Pedestrian, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_Safety_Pedestrian, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_Transit_Emphasis, intermediate_gdb, 'overlay_RN_Safety_Pedestrian')

print('Overlaying source_RN_VEDP_Business_Ready_Site')
if source_RN_VEDP_Business_Ready_Site:
    arcpy.lr.OverlayRouteEvents(overlay_RN_Safety_Pedestrian, 'RTE_NM LINE BEGIN_MSR END_MSR', source_RN_VEDP_Business_Ready_Site, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', overlay_RN_VEDP_Business_Ready_Site, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_Safety_Pedestrian, intermediate_gdb, 'overlay_RN_VEDP_Business_Ready_Site')

print('Overlaying source_UDA')
if source_UDA:
    arcpy.lr.OverlayRouteEvents(overlay_RN_VEDP_Business_Ready_Site, 'RTE_NM LINE BEGIN_MSR END_MSR', source_UDA, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', all_needs_overlapped, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')
else:
    arcpy.TableToTable_conversion(overlay_RN_VEDP_Business_Ready_Site, intermediate_gdb, 'all_needs_overlapped')


# Create final output table
print('Creating intermediate output table')
tbl_output = os.path.join(output_gdb, 'tbl_2023_VTrans_MidTerm_Needs')
arcpy.CreateTable_management(output_gdb, os.path.basename(tbl_output))
for f in FIELDS:
    field = Field(name=f, alias=FIELD_ALIAS[f], type=FIELD_TYPE[f])
    arcpy.AddField_management(tbl_output, field.name, field.type, field_alias=field.alias)

# Add needs data
arcpy.Append_management(all_needs_overlapped, tbl_output, schema_type='NO_TEST')

# Calculate all non-YES needs to NO.  Delete records if all needs are NO
# needs_fields = ['CoSS_Congestion','CoSS_Reliability','CoSS_Rail_Reliability','CoSS_Capacity_Preservation','CoSS_TDM','CoSS_Safety_Intersection','CoSS_Safety_Segments','RN_Congestion','RN_Reliability','RN_Capacity_Preservation','RN_TDM','RN_AC_Bicycle_Access','RN_AC_Pedestrian_Access','RN_AC_Transit_Access','RN_Transit_Equity','RN_Safety_Segments','RN_Safety_Intersection','RN_Safety_Pedestrian','IEDA','UDA_Bike_Infrast','UDA_Comp_Street','UDA_Intersection_Des','UDA_Landscape','UDA_Offstreet_Park','UDA_Onstreet_Park','UDA_Ped_Infrast','UDA_Road_Capacity','UDA_Road_Ops','UDA_Safety_Feat','UDA_Sidewalk','UDA_Signage','UDA_Street_Grid','UDA_Traffic_Calm','UDA_Transit_Capacity','UDA_Transit_Facilities','UDA_Transit_Freq','UDA_Transit_Ops','RN_Growth_Area']
del_count = 0
with arcpy.da.UpdateCursor(tbl_output, NEEDS_FIELDS) as cur:
    for row in cur:
        # Set all non-YES fields to NO
        for n in range(len(row)):
            if row[n] is None or row[n] != 'YES':
                row[n] = 'NO'

        # Delete record if all needs are NO
        no_count = 0
        for n in range(len(row)):
            if row[n] == 'NO':
                no_count +=1
        
        if no_count == len(row):
            del_count += 1
            cur.deleteRow()
            continue

        cur.updateRow(row)



# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", tbl_output, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_output Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_output Events", intermediate_gdb, "VTrans_MidTerm_Needs_2023_Intermediate")


# Finish filling out fields in final output
fc_needs = os.path.join(intermediate_gdb, 'VTrans_MidTerm_Needs_2023_Intermediate')

### Fill LRS-related fields
# Make lrs dictionary
print('Update LRS Fields')
routes_needed = set([route[0] for route in arcpy.da.SearchCursor(fc_needs, 'RTE_NM')])
lrs_fields = ['RTE_NM', 'RTE_STREET_NM', 'RTE_COMMON_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM', 'RTE_DIRECTION_CD', 'RTE_PARENT_RTE_NM']
lrs_dict = {row[0]: (row[1], row[2], row[3], row[4], row[5]) for row in arcpy.da.SearchCursor(lrs, lrs_fields)}

update_lrs_fields = ['RTE_NM', 'ST_NM', 'VDOT_COMMON_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM', 'Direction', 'MASTER_RTE_NM']
with arcpy.da.UpdateCursor(fc_needs, update_lrs_fields) as cur:
    for row in cur:
        try:
            st_nm, vdot_common_nm, rte_opposite_direction_rte_nm, direction, master_rte_nm = lrs_dict.get(row[0])
        except:
            st_nm, vdot_common_nm, rte_opposite_direction_rte_nm, direction, master_rte_nm = ('ERROR', 'ERROR', 'ERROR', 'ERROR', 'ERROR')
        row[1] = st_nm
        row[2] = vdot_common_nm
        row[3] = rte_opposite_direction_rte_nm
        row[4] = direction
        row[5] = master_rte_nm
        cur.updateRow(row)

lyr_fc_needs = 'lyr_fc_needs'
arcpy.MakeFeatureLayer_management(fc_needs, lyr_fc_needs)

### VDOT Districts
print('Update VDOT Districts Fields')
lyr_districts = 'lyr_districts'
arcpy.MakeFeatureLayer_management(VDOT_Districts, lyr_districts)
districts = [row[0] for row in arcpy.da.SearchCursor(lyr_districts, 'DISTRICT_NAME')]
for district in districts:
    arcpy.SelectLayerByAttribute_management(lyr_districts, 'NEW_SELECTION', f"DISTRICT_NAME = '{district}'")
    arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_districts, selection_type='NEW_SELECTION')
    with arcpy.da.UpdateCursor(lyr_fc_needs, 'VDOT_District') as cur:
        for row in cur:
            row[0] = district
            cur.updateRow(row)
arcpy.SelectLayerByAttribute_management(lyr_fc_needs, 'CLEAR_SELECTION')


# ### VDOT Jurisdictions  (Field Removed)
# print('Update VDOT Jurisdictions Fields')
# lyr_jurisdictions = 'lyr_jurisdictions'
# arcpy.MakeFeatureLayer_management(VDOT_Jurisdictions, lyr_jurisdictions)
# jurisdictions = [row[0] for row in arcpy.da.SearchCursor(lyr_jurisdictions, 'NAMELSAD')]
# for jurisdiction in jurisdictions:
#     arcpy.SelectLayerByAttribute_management(lyr_jurisdictions, 'NEW_SELECTION', f"NAMELSAD = '{jurisdiction}'")
#     arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_jurisdictions, selection_type='NEW_SELECTION')
#     with arcpy.da.UpdateCursor(lyr_fc_needs, 'Jurisdiction') as cur:
#         for row in cur:
#             row[0] = jurisdiction
#             cur.updateRow(row)

### MPOs
print('Update MPO Fields')
lyr_MPOs = 'lyr_MPOs'
arcpy.MakeFeatureLayer_management(MPOs, lyr_MPOs)
MPO_Names = [row[0] for row in arcpy.da.SearchCursor(lyr_MPOs, 'MPO_NAME')]
for MPO_Name in MPO_Names:
    arcpy.SelectLayerByAttribute_management(lyr_MPOs, 'NEW_SELECTION', f"MPO_NAME = '{MPO_Name}'")
    arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_MPOs, selection_type='NEW_SELECTION')
    with arcpy.da.UpdateCursor(lyr_fc_needs, 'MPO') as cur:
        for row in cur:
            row[0] = MPO_Name
            cur.updateRow(row)
arcpy.SelectLayerByAttribute_management(lyr_fc_needs, 'CLEAR_SELECTION')


# ### Census Urban Areas  (Field Removed)
# print('Update Census Urban Areas Fields')
# lyr_UA = 'lyr_UA'
# arcpy.MakeFeatureLayer_management(Census_Urban_Areas, lyr_UA)
# UA_Names = [row[0] for row in arcpy.da.SearchCursor(lyr_UA, 'NAME')]
# for UA_Name in UA_Names:
#     # Fix single quote issue in sql query
#     sql_ua_name = UA_Name.replace("'", "''")
#     arcpy.SelectLayerByAttribute_management(lyr_UA, 'NEW_SELECTION', f"NAME = '{sql_ua_name}'")
#     arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_UA, selection_type='NEW_SELECTION')
#     with arcpy.da.UpdateCursor(lyr_fc_needs, 'Census_Urbanized') as cur:
#         for row in cur:
#             row[0] = UA_Name
#             cur.updateRow(row)


### Urban Development Areas
print('Update Urban Development Area Fields')
lyr_UDA = 'lyr_UDA'
arcpy.MakeFeatureLayer_management(UDAs, lyr_UDA)
UDA_Names = [row[0] for row in arcpy.da.SearchCursor(lyr_UDA, 'UDA_NM')]

# Set all UDA field for all records to NO
with arcpy.da.UpdateCursor(lyr_fc_needs, 'UDA') as cur:
    for row in cur:
        row[0] = 'NO'
        cur.updateRow(row)

# For each UDA, update UDA field to YES and enter the UDA Name
for UDA_Name in UDA_Names:
    # Fix single quote issue in sql query
    sql_uda_name = UDA_Name.replace("'", "''")
    arcpy.SelectLayerByAttribute_management(lyr_UDA, 'NEW_SELECTION', f"UDA_NM = '{sql_uda_name}'")
    arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_UDA, selection_type='NEW_SELECTION')
    with arcpy.da.UpdateCursor(lyr_fc_needs, ['UDA', 'UDA_Name']) as cur:
        for row in cur:
            row[0] = 'YES'
            row[1] = UDA_Name
            cur.updateRow(row)
arcpy.SelectLayerByAttribute_management(lyr_fc_needs, 'CLEAR_SELECTION')

### CoSS
# CoSS data is brought in from the CoSS layer.  Set CoSS field to NO if field is NULL.  Set CoSS_Primary to NO if field is NULL
with arcpy.da.UpdateCursor(fc_needs, ['CoSS', 'CoSS_Primary']) as cur:
    for row in cur:
        update = False

        if row[0] is None or row[0] == '':
            row[0] = 'NO'
            update = True

        if row[1] is None or row[0] == '':
            row[1] = 'NO'
            update = True
        
        if update == True:
            cur.updateRow(row)



### Regional Networks
print('Update Regional Networks')
lyr_RN = 'lyr_RN'
arcpy.MakeFeatureLayer_management(RNs, lyr_RN)
RN_Names = [row[0] for row in arcpy.da.SearchCursor(lyr_RN, 'RN_Name')]
for RN_Name in RN_Names:
    arcpy.SelectLayerByAttribute_management(lyr_RN, 'NEW_SELECTION', f"RN_Name = '{RN_Name}'")
    arcpy.SelectLayerByLocation_management(lyr_fc_needs, 'HAVE_THEIR_CENTER_IN', lyr_RN, selection_type='NEW_SELECTION')
    with arcpy.da.UpdateCursor(lyr_fc_needs, ['RN_Name']) as cur:
        for row in cur:
            row[0] = RN_Name
            cur.updateRow(row)
arcpy.SelectLayerByAttribute_management(lyr_fc_needs, 'CLEAR_SELECTION')

### Segment Length
print('Update Length')
with arcpy.da.UpdateCursor(fc_needs, ['BEGIN_MSR', 'END_MSR', 'Segment_Length']) as cur:
    for row in cur:
        len = abs(row[1] - row[0])
        row[2] = len
        cur.updateRow(row)


### Functional Classification - Change numbers to text description
print('Update Functional Classification')
fc_dict = {
    '1': '1 - Interstate',
    '2': '2 - Other Freeways & Expressways',
    '3': '3 - Other Principal Arterial',
    '4': '4 - Minor Arterial',
    '5': '5 - Major Collector',
    '6': '6 - Minor Collector',
    '7': '7 - Local'
}
with arcpy.da.UpdateCursor(fc_needs, 'VDOT_FC') as cur:
    for row in cur:
        fc_text = fc_dict.get(row[0])
        row[0] = fc_text
        cur.updateRow(row)


### Segment IDs
print('Update Segment IDs')
def calculate_seg_id(rte_nm, geom):
    """ Calculates segment id based on line mid-point coordinates and direction """

    try:
        # Get direction as 1 for prime and 0 for non-prime
        if rte_nm.startswith('R-VA'):
            d = '1' if rte_nm[14:16] in ['NB', 'EB'] else '0'
        else:
            d = '1' if rte_nm[7:9] == 'PR' else '0'

        # Get last three of route number to avoid duplicates at intersections
        if rte_nm.startswith('R-VA'):
            n = rte_nm[11:14]
        else:
            n = rte_nm[10:13]
        # Get midpoint coordinates
        midPoint = geom.positionAlongLine(0.5, True)
        x = str(midPoint.firstPoint.X * -1).replace('.','')[:7]
        y = str(midPoint.firstPoint.Y).replace('.','')[:7]

        return d + n + x + y
    except:
        return None

with arcpy.da.UpdateCursor(fc_needs, ['Segment_ID', 'RTE_NM', 'SHAPE@']) as cur:
    for row in cur:
        rte_nm = row[1]
        geom = row[2]
        seg_id = calculate_seg_id(rte_nm, geom)
        row[0] = seg_id
        cur.updateRow(row)

# Remove duplicate segments
print('Removing Duplicates')
all_needs_fields = [field.name for field in arcpy.ListFields(fc_needs) if field.name not in ['OBJECTID', 'Shape', 'Shape_Length']]
df_all_needs = pd.DataFrame([row for row in arcpy.da.SearchCursor(fc_needs, all_needs_fields)], columns=all_needs_fields)
# print(f'  Before count: {len(df_all_needs)}')
df_all_needs_nodup = df_all_needs.drop_duplicates()
# print(f'  After count: {len(df_all_needs_nodup)}')

# RN Eligible UDA Needs are calculated here, after congestion and UDA segments have been finalized in the code above
print('Calculating RN Eligible UDA Needs')

# RNs with less than 20 miles of congestion needs
Congestion_RNs = ['Kingsport Region', 'Danville Region', 'Bristol Region', 'Central VA MPO Region (Lynchburg)', 'Harrisonburg Region', 'Charlottesville Region', 'New River Valley Region', 'Winchester Region', 'Staunton/Augusta/Waynesboro Region']

df_all_needs_nodup.loc[((df_all_needs_nodup['UDA_Bike_Infrast'] == 'YES') | (df_all_needs_nodup['UDA_Comp_Street'] == 'YES') | (df_all_needs_nodup['UDA_Intersection_Des'] == 'YES') | (df_all_needs_nodup['UDA_Landscape'] == 'YES') | (df_all_needs_nodup['UDA_Offstreet_Park'] == 'YES') | (df_all_needs_nodup['UDA_Onstreet_Park'] == 'YES') | (df_all_needs_nodup['UDA_Ped_Infrast'] == 'YES') | (df_all_needs_nodup['UDA_Road_Capacity'] == 'YES') | (df_all_needs_nodup['UDA_Road_Ops'] == 'YES') | (df_all_needs_nodup['UDA_Safety_Feat'] == 'YES') | (df_all_needs_nodup['UDA_Sidewalk'] == 'YES') | (df_all_needs_nodup['UDA_Signage'] == 'YES') | (df_all_needs_nodup['UDA_Street_Grid'] == 'YES') | (df_all_needs_nodup['UDA_Traffic_Calm'] == 'YES') | (df_all_needs_nodup['UDA_Transit_Capacity'] == 'YES') | (df_all_needs_nodup['UDA_Transit_Facilities'] == 'YES') | (df_all_needs_nodup['UDA_Transit_Freq'] == 'YES') | (df_all_needs_nodup['UDA_Transit_Ops'] == 'YES')) & (df_all_needs_nodup['RN_Name'].isin(Congestion_RNs)), 'RN_Growth_Area'] = 'YES'

all_needs_csv = os.path.join(os.path.dirname(intermediate_gdb), 'all_needs.csv')
df_all_needs_nodup.to_csv(all_needs_csv, index=False)

# Make route event layer
tbl_output = os.path.join(output_gdb, 'tbl_2023_VTrans_MidTerm_Needs')

print('Creating final output table')
arcpy.CreateTable_management(output_gdb, os.path.basename(tbl_output))
for f in FIELDS:
    field = Field(name=f, alias=FIELD_ALIAS[f], type=FIELD_TYPE[f])
    arcpy.AddField_management(tbl_output, field.name, field.type, field_alias=field.alias)

# Add needs data
arcpy.Append_management(all_needs_csv, tbl_output, schema_type='NO_TEST')

arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", tbl_output, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_output Events2", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_output Events2", output_gdb, "VTrans_MidTerm_Needs_2023")