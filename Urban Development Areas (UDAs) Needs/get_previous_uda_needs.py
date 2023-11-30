# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')


# Paths to intermediate and output geodatabases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Urban Development Areas (UDAs) Needs\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Urban Development Areas (UDAs) Needs\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')


previous_needs = f'{main_path}\\A1 - Common Datasets\\Previous Needs Layer\\2021_VTrans_Mid_term_Needs.gdb\\Base_2021v8'

# Overlap LRS
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# %%
# Create DataFrame from previous needs layer.  Filter for only records that have a UDA need
fields_to_keep = [
    'VDOT_RM',
    'From_measure',
    'To_measure'
]

uda_fields = [
    'UDA_road_capacity',
    'UDA_road_ops',
    'UDA_transit_freq',
    'UDA_transit_ops',
    'UDA_transit_capacity',
    'UDA_transit_facilities',
    'UDA_street_grid',
    'UDA_bike_infrast',
    'UDA_ped_infrast',
    'UDA_comp_street',
    'UDA_safety_feat',
    'UDA_onstreet_park',
    'UDA_offstreet_park',
    'UDA_intersection_des',
    'UDA_signage',
    'UDA_traffic_calm',
    'UDA_landscape',
    'UDA_sidewalk',
    'RN_Growth_Area'
]

fields_to_keep += uda_fields

df_previous_uda_needs = pd.DataFrame([row for row in arcpy.da.SearchCursor(previous_needs, fields_to_keep)], columns=fields_to_keep)

# %%
# Find only records that previously contained a UDA need.  Replace NO with 0 and YES with 1 then sum all need columns.
# Anywhere that the value > 0 had at least one need
df_previous_uda_needs.replace('NO', 0, inplace=True)
df_previous_uda_needs.replace('YES', 1, inplace=True)
df_previous_uda_needs['need_sum'] = df_previous_uda_needs.iloc[:, -19:-1].sum(axis=1)
df_previous_uda_needs_filtered = df_previous_uda_needs.loc[df_previous_uda_needs['need_sum'] >= 1].copy()

# Turn needs back to text
df_previous_uda_needs_filtered.iloc[:, -20:-1] = df_previous_uda_needs_filtered.iloc[:, -20:-1].replace(0, 'NO')
df_previous_uda_needs_filtered.iloc[:, -20:-1] = df_previous_uda_needs_filtered.iloc[:, -20:-1].replace(1, 'YES')

# Rename fields to match schema
df_previous_uda_needs_filtered.rename(columns={'VDOT_RM': 'RTE_NM', 'From_measure':'BEGIN_MSR', 'To_measure': 'END_MSR'}, inplace=True)

field_order = ['RTE_NM', 'BEGIN_MSR', 'END_MSR'] + uda_fields
df_previous_uda_needs_filtered[field_order]  # Only contains segments with UDA needs

# %%
# Create final output
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df_previous_uda_needs_filtered[field_order].to_csv(output_csv, index=False)

# Make raw output gdb table.  This will be dissolved to reduce the amount of very short segments that have carried over from the previous layer
predissolve_table = os.path.join(intermediate_gdb, 'tbl_uda_needs_predissolve')
arcpy.TableToTable_conversion(output_csv, intermediate_gdb, 'tbl_uda_needs_predissolve')

tbl_output = os.path.join(output_gdb, 'tbl_uda_needs')
arcpy.lr.DissolveRouteEvents(predissolve_table, "RTE_NM; Line; BEGIN_MSR; END_MSR", "UDA_road_capacity;UDA_road_ops;UDA_transit_freq;UDA_transit_ops;UDA_transit_capacity;UDA_transit_facilities;UDA_street_grid;UDA_bike_infrast;UDA_ped_infrast;UDA_comp_street;UDA_safety_feat;UDA_onstreet_park;UDA_offstreet_park;UDA_intersection_des;UDA_signage;UDA_traffic_calm;UDA_landscape;UDA_sidewalk;RN_Growth_Area", tbl_output, "RTE_NM; Line; BEGIN_MSR; END_MSR", "DISSOLVE", "INDEX")

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", tbl_output, "RTE_NM; LINE; BEGIN_MSR; END_MSR", "tbl_uda_needs Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_uda_needs Events", output_gdb, "UDA_Needs")

# %%



