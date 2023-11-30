# %% [markdown]
# # Need Category: Capacity Preservation #
# 
# **Measure**: VDOT Arterial Preservation Network or the state-maintained portion of the National Highway System in Virginia and including some additional highways that facilitate connectivity.
# 
# **What it means**: This VTrans Need Category focuses on the need for proactive measures to strike a balance between access and mobility.
# 
# **Applicable VTrans Travel Markets**: CoSS, RN
# 
# **Data Sources**:
# 1. VDOT, TMPD - Arterial Preservation Network
# 
# **Year of analysis**: 2023

# %% [markdown]
# ### Calculations ###
# 1. Identify roadway segments included in VDOT's Arterial Preservation Network
# 2. **Threshold for Need for Capacity Preservation**: Roadway segments within RNs or along CoSS and included in VDOT's Arterial Preservation Network are identified as those with a VTrans Mid-term Need for Capacity Preservation.

# %% [markdown]
# ### Code ###

# %%
import arcpy
import os
import pathlib
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %% [markdown]
# #### Collect required datasets ####
# 
# The following line feature classes must have LRS fields as "RTE_NM", "BEGIN_MSR", and "END_MSR":
# 
# 1. APN - A feature class of the Arterial Preservation Network (APN) (Note: Must have segments in both directions)
# 2. CoSS - A feature class of the Corridors of Statewide Significance (CoSS)
# 3. RN - A feature class of the Regional Networks (RN)
# 
# 4. LRS - A copy of the overlap LRS

# %%
# Paths to intermediate and output geodatabases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Capacity Preservation\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Capacity Preservation\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')

# Paths to input layers
APN = f'{main_path}\\A1 - Common Datasets\\Capacity Preservation\data\data.gdb\\apn'
CoSS = f'{common_datasets_gdb}\\tbl_coss_2023'
RN = f'{common_datasets_gdb}\\tbl_regional_networks'
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# %% [markdown]
# ### Prepare event table overlapping CoSS, RN, and APN ###
# 
# First the input layers are combined to create a single event table.


# %%
# Create event tables from input feature classes
tbl_apn = arcpy.TableToTable_conversion(APN, intermediate_gdb, 'tbl_apn')
tbl_coss = arcpy.TableToTable_conversion(CoSS, intermediate_gdb, 'tbl_coss')
tbl_rn = arcpy.TableToTable_conversion(RN, intermediate_gdb, 'tbl_rn')

# These tables should have a field ('APN', 'COSS', or 'RN') that is equal to 1 to indicate
# that a given segment belongs to that network
def add_field(layer, field_name):
    field_names = [field.name for field in arcpy.ListFields()]
    if field_name in field_names:
        print(f'{field_name} already exists')
        return
    else:
        arcpy.AddField_management(layer, field_name, 'SHORT')
        with arcpy.da.UpdateCursor(layer, field_name) as cur:
            for row in cur:
                row[0] = 1
                cur.updateRow(row)
        print(f'{field_name} added to table')

# Overlap APN with CoSS
arcpy.lr.OverlayRouteEvents(
        tbl_apn,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        tbl_coss, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tbl_apn_coss'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

# Overlap APN and CoSS with RN
arcpy.lr.OverlayRouteEvents(
        os.path.join(intermediate_gdb, 'tbl_apn_coss'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        tbl_rn, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tbl_apn_coss_rn'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")


# %% [markdown]
# ### Identify capacity preservation needs ###
# Roadway segments within RNs or along the CoSS, and included in VDOT’s Arterial Preservation Network, are identified as those with a VTrans Mid-term Need for Capacity Preservation.  The below code will clean up the event table created above and use it to identify segments that are identified as having a capacity preservation need.

# %%
# Create dataframe with only needed fields
fields_to_keep = [
    'RTE_NM',
    'BEGIN_MSR',
    'END_MSR',
    'APN',
    'RN',
    'COSS'
]

tbl_apn_coss_rn = os.path.join(intermediate_gdb, 'tbl_apn_coss_rn')
df = pd.DataFrame([row for row in arcpy.da.SearchCursor(tbl_apn_coss_rn, fields_to_keep)], columns=fields_to_keep)

# Add and calculate capcity preservation needs fields:
# CoSS and APN
df['CoSS_Capacity_Preservation'] = 'NO'
df.loc[(df['APN'] == 1) & (df['COSS'] == 1), 'CoSS_Capacity_Preservation'] = 'YES'

# RN and APN
df['RN_Capacity_Preservation'] = 'NO'
df.loc[(df['APN'] == 1) & (df['RN'] == 1), 'RN_Capacity_Preservation'] = 'YES'

# Place fields in order specified in schema sheet
df = df[['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'CoSS_Capacity_Preservation', 'RN_Capacity_Preservation']]

# Only keep records where at least one need is located
df = df.loc[(df['CoSS_Capacity_Preservation'] == 'YES') | (df['RN_Capacity_Preservation'] == 'YES')]


# %% [markdown]
# #### Create output event table and layer ####

# %%
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_capacity_preservation')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_capacity_preservation Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_capacity_preservation Events", output_gdb, "Capacity_Preservation")


