# %% [markdown]
# # Need Category: Improved Reliability (Roadway) #
# 
# **Measure**: Level of Travel Time Reliability (LOTTR)
# 
# **What it means**: Number of hours where the ratio of longer (80th percentile) travel times to “normal” (50th percentile) travel time exceeds 50%. A higher number indicates less reliable travel.
# 
# **Applicable VTrans Travel Markets**: CoSS, RN
# 
# **Year of analysis**: 2022
# 
# **Threshold for Need for Improved Reliability**: Roadway segments where the average weekday and weekend day LOTTR is greater than 1.5 for are identified as those with a VTrans Mid-term Need for Improved Reliability.

# %% [markdown]
# ### Code ###
# LOTTR was calculated by ICF.  The code below uses that data to create the needs event table.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %%
# Paths to intermediate and output geodatabases
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Improved Reliability (Roadway)\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Improved Reliability (Roadway)\\data\\output.gdb"

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
LRS = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'
TMC_LRS = f'{common_datasets_gdb}\\tbl_tmc_lrs_2023_master'

LOTTR = f"{main_path}\\A1 - Common Datasets\\Improved Reliability (Roadway)\\data\\2022_LOTTR_WA_updated.csv"

# %%
# Load LOTTR data
df_lottr = pd.read_csv(LOTTR)#, usecols=['tmc', 'F22SHrGT13', 'F22SHrGT15'])

# %%
# Identify reliability threshold - Roadway segments where the average weekday and weekend day LOTTR is greater than 1.5 for are identified as those with a VTrans Mid-term Need for Improved Reliability.
lottr_columns = ['F22SD6AM', 'F22SD7AM', 'F22SD8AM',
       'F22SD9AM', 'F22SD10AM', 'F22SD11AM', 'F22SD12PM', 'F22SD1PM',
       'F22SD2PM', 'F22SD3PM', 'F22SD4PM', 'F22SD5PM', 'F22SD6PM', 'F22SD7PM']

df_lottr['avg_lottr'] = df_lottr[lottr_columns].mean(axis=1)
df_lottr['reliability_threshold'] = 'NO'
df_lottr.loc[df_lottr['avg_lottr'] >= 1.5, 'reliability_threshold'] = 'YES'

# %%
# Overlay TMC, CoSS, and RN layers
tmc_coss = os.path.join(intermediate_gdb, 'tmc_coss')
arcpy.lr.OverlayRouteEvents(
        TMC_LRS,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        CoSS, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tmc_coss'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

tmc_coss_rn = os.path.join(intermediate_gdb, 'tmc_coss_rn')
arcpy.lr.OverlayRouteEvents(
        tmc_coss,
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        RN, 
        "RTE_NM; Line; BEGIN_MSR; END_MSR",
        'UNION', 
        os.path.join(intermediate_gdb, 'tmc_coss_rn'),
        'RTE_NM; LINE; BEGIN_MSR; END_MSR',
        "NO_ZERO",
        "FIELDS", 
        "INDEX")

# %%
# Join data to LRS by TMC
tmc_fields = ['TMC', 'RTE_NM', 'BEGIN_MSR', 'END_MSR', 'COSS', 'RN']
df_tmcs = pd.DataFrame([row for row in arcpy.da.SearchCursor(tmc_coss_rn, tmc_fields)], columns=tmc_fields).rename(columns={'TMC':'tmc'})
df_tmcs['len'] = round(df_tmcs['END_MSR'] - df_tmcs['BEGIN_MSR'], 3)
df_tmcs = df_tmcs.loc[~(df_tmcs['tmc'] == '') & (df_tmcs['len'] > 0)]

# %%
# Add tmc, coss, and rn data to lottr data
df_lottr_tmc = df_tmcs.merge(df_lottr, on='tmc')

# %% [markdown]
# #### Create output event table and layer ####

# %%
# Identify CoSS Reliability Needs
df_lottr_tmc['CoSS_Reliability'] = 'NO'
df_lottr_tmc.loc[(df_lottr_tmc['reliability_threshold'] == 'YES') & (df_lottr_tmc['COSS'] == 1), 'CoSS_Reliability'] = 'YES'

# Identify RN Reliability Needs
df_lottr_tmc['RN_Reliability'] = 'NO'
df_lottr_tmc.loc[(df_lottr_tmc['reliability_threshold'] == 'YES') & (df_lottr_tmc['RN'] == 1), 'RN_Reliability'] = 'YES'

# Fit to schema
fields_to_keep = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'CoSS_Reliability', 'RN_Reliability']
df_output = df_lottr_tmc.loc[(df_lottr_tmc['CoSS_Reliability'] == 'YES') | (df_lottr_tmc['RN_Reliability'] == 'YES')][fields_to_keep]

# %%
output_csv = os.path.join(os.path.dirname(intermediate_gdb), 'output.csv')
df_output.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_reliability')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(LRS, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_reliability Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_reliability Events", output_gdb, "Reliability")


