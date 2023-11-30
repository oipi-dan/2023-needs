# %% [markdown]
# # Transit Access for Equaity Emphasis Areas #
# 
# This script requires the three input parts to be calculated in advance:
# 1. Equity Emphasis Areas (EEA)
# 2. Transit Viability
# 3. Areas Underserved by Transit
# 
# **Threshold for Need for Transit Access for Equity Emphasis Areas** : Roadway segments in areas that are
# identified as EEAs, are considered Transit-viable, and are considered underserved by transit are identified as those with
# a VTrans Mid-term Need for Transit Access for Equity Emphasis Areas.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')


# Paths to intermediate and output geodatabases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access for Equity Emphasis Areas\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Transit Access for Equity Emphasis Areas\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')


# Overlap LRS
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# Functional Classification event table
TBL_FC = f'{common_datasets_gdb}\\tbl_fc23'

# Regional Network event table
RN = f'{common_datasets_gdb}\\tbl_regional_networks'

# Input parts:
# EEA.  These are in a block group polygon where eea = 'YES'
EEAs = f'{main_path}\\A1 - Common Datasets\\Need for Transit Access for Equity Emphasis Areas\\data\\intermediate.gdb\\Block_Group'

# Transit Viability and Underserved by Transit.  These are in a block group polygon
# where TransitViability_Flag = 1 and TransitUnderserved_Flag = 1
Transit_Viability_Underserved = f'{main_path}\\A1 - Common Datasets\\Need for Transit Access for Equity Emphasis Areas\\data\\transit_viability_underserved.gdb\\transit_viability_underserved'

# %%
# Identify block groups that meet the threshold for transit access need

# EEA Blocks
eea_fields = ['GEOID', 'eea']
df_EEAs = pd.DataFrame([row for row in arcpy.da.SearchCursor(EEAs, eea_fields)], columns=eea_fields).set_index('GEOID')

# Transit Viability Blocks
viability_fields = ['GEOID', 'TransitViability_Flag']
df_transit_viability = pd.DataFrame([row for row in arcpy.da.SearchCursor(Transit_Viability_Underserved, viability_fields)], columns=viability_fields).set_index('GEOID')
df_transit_viability.loc[df_transit_viability['TransitViability_Flag'] == 1, 'TransitViability_Flag'] = 'YES'
df_transit_viability.loc[df_transit_viability['TransitViability_Flag'] == 0, 'TransitViability_Flag'] = 'NO'

# Underserved Transit Blocks
underserved_fields = ['GEOID', 'TransitUnderserved_Flag']
df_transit_underserved = pd.DataFrame([row for row in arcpy.da.SearchCursor(Transit_Viability_Underserved, underserved_fields)], columns=underserved_fields).set_index('GEOID')
df_transit_underserved.loc[df_transit_underserved['TransitUnderserved_Flag'] == 1, 'TransitUnderserved_Flag'] = 'YES'
df_transit_underserved.loc[df_transit_underserved['TransitUnderserved_Flag'] == 0, 'TransitUnderserved_Flag'] = 'NO'

# Three parts merged into one DataFrame
df_eea_viability_underserved = df_EEAs.join([df_transit_viability, df_transit_underserved])

# Needs will be determined by the blocks that meet the threshold of all three parts
df_blocks_all_three = df_eea_viability_underserved.loc[(df_eea_viability_underserved['eea'] == 'YES') & (df_eea_viability_underserved['TransitViability_Flag'] == 'YES') & (df_eea_viability_underserved['TransitUnderserved_Flag'] == 'YES')]

# %%
# create census blocks layer containing only blocks that meet all three thresholds identified in df_blocks_all_three
blocks_all_three_sql = f"GEOID in {str(tuple(df_blocks_all_three.index))}"
threshold_blocks = os.path.join(intermediate_gdb, 'threshold_blocks')
arcpy.FeatureClassToFeatureClass_conversion(EEAs, intermediate_gdb, 'threshold_blocks', blocks_all_three_sql)

# Buffer by 100' to prevent segmentation on roads that lie on the boundary of the block groups
threshold_blocks_buffer = os.path.join(intermediate_gdb, 'threshold_blocks_buffer')
arcpy.PairwiseBuffer_analysis(threshold_blocks, threshold_blocks_buffer, '100 FEET')
arcpy.PairwiseDissolve_analysis(threshold_blocks_buffer, threshold_blocks)

# %%
# Using functional classification > local as base, identify segments that are within threshold_blocks as a need

# Make FC route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", TBL_FC, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_fc Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_fc Events", intermediate_gdb, "tbl_fc_events")
tbl_fc_events = os.path.join(intermediate_gdb, 'tbl_fc_events')

# Clip FC with threshold_blocks
fc_threshold_blocks = os.path.join(intermediate_gdb, 'fc_threshold_blocks')
arcpy.PairwiseClip_analysis(tbl_fc_events, threshold_blocks, fc_threshold_blocks)



# %%
# Recalculate begin and end measures
fc_threshold_blocks_singlepart = os.path.join(intermediate_gdb, 'fc_threshold_blocks_singlepart')
arcpy.MultipartToSinglepart_management(fc_threshold_blocks, fc_threshold_blocks_singlepart)
with arcpy.da.UpdateCursor(fc_threshold_blocks_singlepart, ['SHAPE@', 'BEGIN_MSR', 'END_MSR']) as cur:
    for row in cur:
        geom = row[0]
        begin_msr = geom.firstPoint.M
        end_msr = geom.lastPoint.M
        row[1] = begin_msr
        row[2] = end_msr
        cur.updateRow(row)

# %%
# Overlay with RN to only include segments within RN

# Convert fc_threshold_blocks_singlepart to event table
tbl_fc_threshold_blocks_singlepart = os.path.join(intermediate_gdb, 'tbl_fc_threshold_blocks_singlepart')
arcpy.TableToTable_conversion(fc_threshold_blocks_singlepart, intermediate_gdb, 'tbl_fc_threshold_blocks_singlepart')

# Overlay with RN
transit_access_RN_Overlay = os.path.join(intermediate_gdb, 'transit_access_RN_Overlay')
arcpy.lr.OverlayRouteEvents(tbl_fc_threshold_blocks_singlepart, 'RTE_NM LINE BEGIN_MSR END_MSR', RN, 'RTE_NM LINE BEGIN_MSR END_MSR', 'INTERSECT', transit_access_RN_Overlay, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')


# %%
# Clean up needs event table in Pandas
transit_access_fields = [field.name for field in arcpy.ListFields(transit_access_RN_Overlay) if field.name not in ('OBJECTID', 'Shape', 'ORIG_FID', 'Shape_Length', 'RN')]
df_transit_access = pd.DataFrame([row for row in arcpy.da.SearchCursor(transit_access_RN_Overlay, transit_access_fields)], columns=transit_access_fields)
df_transit_access['RN_Transit_Equity'] = 'YES'

# Filter out ramps and non-local functional classification
df_transit_access = df_transit_access.loc[df_transit_access['STATE_FUNCT_CLASS_ID'] < 7]
df_transit_access.drop(columns='STATE_FUNCT_CLASS_ID', axis=1, inplace=True)
df_transit_access

# %%
# Create final output
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df_transit_access.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_transit_access_eaa')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_transit_access Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_transit_access Events", output_gdb, "Transit_Access_EAA")

# %%



