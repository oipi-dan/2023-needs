# %% [markdown]
# # Need Category: Transportation Demand Management (TDM) #
# 
# **Measure**: TDM Needs utilizing VTrans Travel Markets, Roadway Functional Classiication, and Roadway Access Management.
# 
# **What it means**: Locations where Transportation Demand Management (TDM) strategies can be beneficial to reduce vehicle miles traveled.
# 
# **Applicable VTrans Travel Markets**: CoSS, RN
# 
# **Data Sources**:
# 1. VDOT - Overlap LRS
# 2. VDOT - Functional Classification
# 
# **Year of analysis**: 2023

# %% [markdown]
# ### Calculations ###
# 1. Identify roadway segments by VTrans Travel Markets and facility type within Regional Networks or along CoSS
# 2. Categorize the following roads as qualifying for designation as a TDM need:
#     * Facilities on CoSS: These roads have a need whose solution may be new or expanded park and ride facilities, rail and public transportation services and passenger facilities, and expansion and coordination of commuter assistance programs services.
#     * Non-limited access facilities within Regional Networks: These roads have a need whose solution may be new or expanded shared mobility solutions.
# 3. **Threshold for VTrans Mid-term Need for Transportation Demand Management**:
#     * Roadway segments along CoSS facilities are identified as those with a VTrans Mid-term Need for Transportation Demand Management for new or expanded park and ride facilities, rail and public transportation services and passenger facilities, and expansion and coordination of commuter assistance programs services.
#     * Roadway segments along non-limited access facilities within Regional Networks (but not also along CoSS) are identified as those with a VTrans Mid-term Need for Transportation Demand Management for new or expanded shared mobility solutions.

# %% [markdown]
# ### Code ###

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %% [markdown]
# #### Prepare Data Sources ####
# 1. lrs - Overlap LRS
# 2. tbl_coss - CoSS Event Table
# 3. tbl_rn - RN Event Table
# 4. tbl_la - Limited Access Event Table
# 5. tbl_fc - Functional Classification Event Table

# %%
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Transportation Demand Management (TDM)\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Transportation Demand Management (TDM)\\data\\output.gdb"
for gdb in [intermediate_gdb, output_gdb]:
    if not os.path.exists(gdb):
        print(f'Creating gdb {os.path.basename(gdb)}')
        arcpy.CreateFileGDB_management(os.path.dirname(gdb), os.path.basename(gdb))

lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

tbl_coss = f'{common_datasets_gdb}\\tbl_coss_2023'

tbl_rn = f'{common_datasets_gdb}\\tbl_regional_networks'

tbl_la = f'{common_datasets_gdb}\\tbl_limited_access'

tbl_fc = f'{common_datasets_gdb}\\tbl_fc23'


# %% [markdown]
# 

# %% [markdown]
# 1. Combine event tables for CoSS, RN, and LA and limit them to FC greater than Local.
# 2. Calculate needs as follows:
#     * Transportation Demand Management - Park and Ride (CoSS) [CoSS_TDM_PR] - CoSS Limited Access, CoSS Non-Limited Access
#     * Transportation Demand Management - Commuter Assistance (CoSS) [CoSS_TDM_CA] - CoSS Limited Access, CoSS Non-Limited Access
#     * Transportation Demand Management - Transit Infrastructure (CoSS) [CoSS_TDM_Transit] - CoSS Limited Access, CoSS Non-Limited Access
#     * Need - Transportation Demand Management - Shared Mobility (RN) [RN_TDM_Shared_Mobility] - RN Non-Limited Access, non-CoSS

# %%
# Overlap all event tables
tbl_coss_rn = os.path.join(intermediate_gdb, 'tbl_coss_rn')
arcpy.lr.OverlayRouteEvents(tbl_coss, 'RTE_NM LINE BEGIN_MSR END_MSR', tbl_rn, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', tbl_coss_rn, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

tbl_coss_rn_la = os.path.join(intermediate_gdb, 'tbl_coss_rn_la')
arcpy.lr.OverlayRouteEvents(tbl_coss_rn, 'RTE_NM LINE BEGIN_MSR END_MSR', tbl_la, 'RTE_NM LINE RTE_FROM_MSR RTE_TO_MSR', 'UNION', tbl_coss_rn_la, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

tbl_coss_rn_la_fc = os.path.join(intermediate_gdb, 'tbl_coss_rn_la_fc')
arcpy.lr.OverlayRouteEvents(tbl_coss_rn_la, 'RTE_NM LINE BEGIN_MSR END_MSR', tbl_fc, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', tbl_coss_rn_la_fc, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')


# %%
# Convert to DataFrame
fields_to_keep = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'COSS', 'RN', 'RIM_ACCESS_CONTROL_DSC', 'STATE_FUNCT_CLASS_ID']
df = pd.DataFrame([row for row in arcpy.da.SearchCursor(tbl_coss_rn_la_fc, fields_to_keep)], columns=fields_to_keep)

# Create cleaner limited access column
df['LA'] = 0
df.loc[df['RIM_ACCESS_CONTROL_DSC'].str.startswith('1-Full'), 'LA'] = 1
df.drop('RIM_ACCESS_CONTROL_DSC', axis=1)

# Rename functional classification column
df.rename(columns={'STATE_FUNCT_CLASS_ID': 'FC'}, inplace=True)


# Add needs columns
# Need - Transportation Demand Management (Limited Access CoSS)
df['CoSS_LA_TDM'] = 'NO'
df.loc[(df['COSS'] == 1) & (df['LA'] == 1), 'CoSS_LA_TDM'] = 'YES'

# Need - Transportation Demand Management (non-limited Access CoSS)
df['CoSS_non_LA_TDM'] = 'NO'
df.loc[(df['COSS'] == 1) & (df['LA'] == 0), 'CoSS_non_LA_TDM'] = 'YES'

# Need - Transportation Demand Management (Limited Access RN)
df['RN_LA_TDM'] = 'NO'
df.loc[(df['RN'] == 1) & (df['FC'].isin([2,3,4,5,6]) & df['LA'] == 1), 'RN_LA_TDM'] = 'YES'

# Need - Transportation Demand Management (Non-Limited Access RN)
df['RN_non_LA_TDM'] = 'NO'
df.loc[(df['COSS'] == 0) & (df['RN'] == 1) & (df['FC'].isin([2,3,4,5,6]) & (df['LA'] == 0)), 'RN_non_LA_TDM'] = 'YES'

# Retain only records where one of the four need fields == 'YES'
df = df.loc[(df['CoSS_LA_TDM'] == 'YES') | (df['CoSS_non_LA_TDM'] == 'YES') | (df['RN_LA_TDM'] == 'YES') | (df['RN_non_LA_TDM'] == 'YES')]

# Clean DataFrame
fields_to_keep = [
    'RTE_NM',
    'BEGIN_MSR',
    'END_MSR',
    'CoSS_LA_TDM',
    'CoSS_non_LA_TDM',
    'RN_LA_TDM',
    'RN_non_LA_TDM'
    ]

df = df[fields_to_keep]

# %% [markdown]
# #### Create output event table and layer ####

# %%
output_csv = os.path.join(os.path.dirname(output_gdb), 'output.csv')
df.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_tdm_needs')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_tdm_needs Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_tdm_needs Events", output_gdb, "Transportation_Demand_Management")


