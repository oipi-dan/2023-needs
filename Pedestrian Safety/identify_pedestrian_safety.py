# %% [markdown]
# # Need Category: Pedestrian Safety #
# 
# **Measure**: Utilization of roadway segments included in VDOT’s Pedestrian Safety Action Plan (PSAP) Priority 5% Corridors
# 
# **What it means**: Roadway areas that may require attention based on pedestrian safety factors
# 
# **Travel Market**: Statewide
# 
# **Data Sources**:
# 1. VDOT Traffic Engineering, Geospatial database developed for PSAP
# 
# **Year of Analysis**: 2018, based on calendar year 2012–2016 crash data
# 
# **Period of analysis**: all days, 24-hour days

# %% [markdown]
# ## Code ##
# 
# Using PSAP data supplied by VDOT, this code flips events on LRS so that records in both directions exist, then exports the results as an event table that will be used in the final needs layer.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Pedestrian Safety\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Pedestrian Safety\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')

# PSAP data
psap = f'{main_path}\\A1 - Common Datasets\\Pedestrian Safety\\data\\PSAP4.gdb\\psap4'

# Overlap LRS
lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# %%
# Flip segments that are prime direction on non-one way segments
# Add 'flip' field to flag segments to be flipped.  These will be exported to a new feature class,
# have the new RTE_NM and m-values recalculated, then added to the final event table.

# Add flip field
if 'flip' not in [field.name for field in arcpy.ListFields(psap)]:
    arcpy.AddField_management(psap, 'flip', 'SHORT')

# Identify fields that need to be flipped
with arcpy.da.UpdateCursor(psap, ['VDOT_DIVIDED', 'UMIS_FACILITY_TYPE', 'flip']) as cur:
    for row in cur:
        if row[0] == 'Undivided' and row[1] != '1-One-Way Undivided':
            row[2] = 1
        else:
            row[2] = 0
        cur.updateRow(row)

# %%
# Make opposite route dictionary
opp_rte_nm_dict = {row[0]: row[1] for row in arcpy.da.SearchCursor(lrs, ['RTE_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM'])}

# %%
# Create new feature class containing only flip segments
psap_to_flip = os.path.join(intermediate_gdb, 'psap_to_flip')
arcpy.FeatureClassToFeatureClass_conversion(psap, intermediate_gdb, 'psap_to_flip', 'flip = 1')

# %%
# Flip RTE_NM and recalculate m-value for records in psap_to_flip
with arcpy.da.UpdateCursor(psap_to_flip, ['RTE_NM', 'FMEAS', 'TMEAS', 'SHAPE@']) as cur:
    for row in cur:
        # Flip rte_nm to opposite direction route
        rte_nm = row[0]
        opp_rte_nm = opp_rte_nm_dict.get(rte_nm)
        row[0] = opp_rte_nm

        # Calculate new m-values
        geom = row[-1]
        new_fmeas = geom.firstPoint.M
        new_tmeas = geom.lastPoint.M
        row[1] = new_fmeas
        row[2] = new_tmeas

        cur.updateRow(row)


# %%
# Convert original and flipped event tables in pandas dataframes and convert to schema
fields_to_keep = ['RTE_NM', 'FMEAS', 'TMEAS']
df_original_psap = pd.DataFrame([row for row in arcpy.da.SearchCursor(psap, fields_to_keep)], columns=fields_to_keep)
df_flipped_psap = pd.DataFrame([row for row in arcpy.da.SearchCursor(psap_to_flip, fields_to_keep)], columns=fields_to_keep)

# DataFrame with both tables
df_psap = df_original_psap.append(df_flipped_psap)

# Fit to schema
df_psap.rename(columns={'FMEAS': 'BEGIN_MSR', 'TMEAS': 'END_MSR'}, inplace=True)
df_psap['Safety_Pedestrian'] = 'YES'

# %%
# Export to csv
output_csv = os.path.join(os.path.dirname(output_gdb), 'output.csv')
df_psap.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_ped_safety')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_ped_safety Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_ped_safety Events", output_gdb, "Pedestrian_Safety_Improvements")

# %%



