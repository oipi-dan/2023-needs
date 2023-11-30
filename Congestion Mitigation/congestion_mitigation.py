# %% [markdown]
# # Need Category: Congestion Mitigation #
# 
# **Measure**: Percent Person Miles Traveled in Excessively Congested Conditions (PECC) and Travel Time Index (TTI)
# 
# **What it means (PECC)**: Percent of the total person-miles traveled (PMT) that takes place in conditions deemed as excessively congested (observed speed 75% or less of the posted speed limit). A higher number indicates more person-miles traveled are impacted by excessively congested conditions.
# 
# **What it means (TTI)**: The Travel Time Index is the ratio of the travel time during the peak period to the time required to make the same trip at reference (a.k.a typical) speeds. A higher number indicates more congestion.
# 
# **Applicable VTrans Travel Markets**: CoSS, RN
# 
# **Year of analysis**: 2022

# %% [markdown]
# ### Code ###
# 
# Steps 1-10 on page 17 of the technical guide were completed separately to create the PECC data found in PECC_2022.csv.  Steps 1-5 on page 18 of the technical guide were completed separately to create the TTI data found in 2022_TTI_WA.csv.  The code below brings these performance measures together and assigns needs to the LRS.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %%
# Paths to intermediate and output geodatabases
intermediate_gdb = f'{main_path}\\A1 - Common Datasets\\Congestion Mitigation\\data\\intermediate.gdb'
output_gdb = f'{main_path}\\A1 - Common Datasets\\Congestion Mitigation\\data\\output.gdb'

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')

# Paths to input layers
CoSS = f'{common_datasets_gdb}\\tbl_coss_2023'
RN = f'{common_datasets_gdb}\\tbl_regional_networks'
LA = f'{common_datasets_gdb}\\tbl_limited_access'

# Overlap LRS
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'
MasterLRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_MASTER_LRS_DY'
TMC_LRS = f'{common_datasets_gdb}\\tbl_tmc_lrs_2023_master'

# Performance Measures
PECC = f'{main_path}\\A1 - Common Datasets\\Congestion Mitigation\\data\\PECC_2022.csv'
TTI = f'{main_path}\\A1 - Common Datasets\\Congestion Mitigation\\data\\2022_TTI_WA.csv'

# %%

# Load PECC data
df_pecc = pd.read_csv(PECC, usecols=['TMC', 'Final Weight']).rename(columns={'TMC': 'tmc'})

# Convert PECC weight from string to number
df_pecc['PECC_Weight'] = df_pecc['Final Weight'].str[:-1]
df_pecc.drop('Final Weight', axis=1, inplace=True)


# Load TTI data
df_tti = pd.read_csv(TTI, usecols=['tmc', 'F22SHrGT13', 'F22SHrGT15'])


# Join PECC data to TMC layer by TMC
df_pecc_tti = df_pecc.merge(df_tti, 'outer', on='tmc')

# TTI should be ignored where PECC is available
df_pecc_tti.loc[df_pecc_tti['PECC_Weight'].notnull(), ['F22SHrGT13', 'F22SHrGT15']] = pd.NA


# Join TTI data to TMC layer by TMC
tmc_fields = ['tmc', 'rte_nm', 'begin_msr', 'end_msr']
df_tmc = pd.DataFrame([row for row in arcpy.da.SearchCursor(TMC_LRS, tmc_fields)], columns=tmc_fields)
df_tmc_pecc_tti = df_tmc.merge(df_pecc_tti, 'outer', on='tmc')
df_tmc_pecc_tti.rename(columns={'rte_nm': 'RTE_NM', 'begin_msr': 'BEGIN_MSR', 'end_msr': 'END_MSR'}, inplace=True)

# %%
# Overlay TMC data with Limited Access, CoSS, and RN tables
# Export as csv
csv_tmc_pecc_tti = os.path.join(os.path.dirname(intermediate_gdb), 'tmc_pecc_tti.csv')
df_tmc_pecc_tti.to_csv(csv_tmc_pecc_tti, index=False)

# Convert to gdb table
tbl_tmc_pecc_tti = os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti')
arcpy.TableToTable_conversion(csv_tmc_pecc_tti, intermediate_gdb, 'tbl_tmc_pecc_tti')

# Overlay tbl_tmc_pecc_tti with Limited Access
tbl_tmc_pecc_tti_la = os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la')
arcpy.lr.OverlayRouteEvents(
        tbl_tmc_pecc_tti,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        LA, 
        "RTE_NM; Line; RTE_FROM_MSR; RTE_TO_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

# Overlay with CoSS
tbl_tmc_pecc_tti_la_coss = os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la_coss')
arcpy.lr.OverlayRouteEvents(
        tbl_tmc_pecc_tti_la,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        CoSS, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la_coss'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

# Overlay with RN
tbl_tmc_pecc_tti_la_coss_rn = os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la_coss_rn')
arcpy.lr.OverlayRouteEvents(
        tbl_tmc_pecc_tti_la_coss,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        RN, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tbl_tmc_pecc_tti_la_coss_rn'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

congestion_fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'tmc', 'PECC_Weight', 'F22SHrGT13', 'F22SHrGT15', 'COSS', 'RN', 'RIM_ACCESS_CONTROL_DSC']
df_congestion = pd.DataFrame([row for row in arcpy.da.SearchCursor(tbl_tmc_pecc_tti_la_coss_rn, congestion_fields)], columns=congestion_fields)

# %% [markdown]
# #### Locate Congestion Needs ####
# 
# **Where PECC is used**: PECC is used to identify Needs for Congestion Mitigation for: (1) Interstate roadways within CoSS; and (2) other select Limited Access Facilities (LAF).  Roadway segments where the average weekday and weekend day share of person miles traveled in excessively congested conditions exceeds policy threshold of 2% are identified as those with Need for Congestion Mitigation
# 
# **Where TTI is used**: TTI is used to identify Needs for Congestion Mitigation for: (1) non-limited access roadways within CoSS; and (2) all other roadways within RNs.  Roadway segments where the average weekday and weekend day TTI is greater than 1.5 for at least one hour, or 1.3 for at least three hours, are identified as those with a VTrans Midterm Need for Congestion Mitigation.

# %%
# Locate segments that meet congestion needs threshold with PECC
df_congestion.loc[(df_congestion['PECC_Weight'] > 2) & ~(df_congestion['RIM_ACCESS_CONTROL_DSC'] == ''), 'congestion_need'] = 'YES'


# Locate segments that meet TTI threshold.  Must be on non-limited access segments according to policy
df_congestion.loc[((df_congestion['F22SHrGT13'] >= 3) | (df_congestion['F22SHrGT15'] >= 1)) & (df_congestion['RIM_ACCESS_CONTROL_DSC'] == ''), 'tti_threshold'] = 'YES'

# (1) non-limited access roadways within CoSS
df_congestion.loc[(df_congestion['RIM_ACCESS_CONTROL_DSC'] == '') & (df_congestion['COSS'] == 1) & (df_congestion['tti_threshold'] == 'YES'), 'congestion_need'] = 'YES'

# (2) all other roadways within RNs
df_congestion.loc[(df_congestion['RIM_ACCESS_CONTROL_DSC'] == '') & (df_congestion['RN'] == 1) & (df_congestion['tti_threshold'] == 'YES'), 'congestion_need'] = 'YES'


# Fit to schema
df_congestion['CoSS_Congestion'] = 'NO'
df_congestion.loc[(df_congestion['COSS'] == 1) & (df_congestion['congestion_need'] == 'YES'), 'CoSS_Congestion'] = 'YES'

df_congestion['RN_Congestion'] = 'NO'
df_congestion.loc[(df_congestion['RN'] == 1) & (df_congestion['congestion_need'] == 'YES'), 'RN_Congestion'] = 'YES'

fields_to_keep = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'CoSS_Congestion', 'RN_Congestion']
df_output = df_congestion.loc[(df_congestion['CoSS_Congestion'] == 'YES') | (df_congestion['RN_Congestion'] == 'YES')][fields_to_keep]

# %% [markdown]
# #### Create output event table and layer ####

# %%
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df_output.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_congestion_mitigation')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_congestion_mitigation Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_congestion_mitigation Events", output_gdb, "Congestion_Mitigation")


