# %% [markdown]
# # Need Category: Roadway Safety #
# 
# **Measure**: Potential for Safety Improvement (PSI)
# 
# **What it means**: Areas with a higher calculated risk of crashes based on roadway characteristics and observed crash data.
# 
# **Applicable VTrans Travel Market**: Statewide
# 
# **Data Sources**:
# 1. Virginia Department of Motor Vehicles - Five-year crash data by location and severity, including intersection
# and interchange-related crashes and segment-level crashes between intersections or interchanges on limited
# Access facilities
# 2. VDOT Traffic Engineering Division - PSI Analysis
# 
# **Year of Analysis**: 2018-2022

# %% [markdown]
# ### Calculations ###
# 1. Merge 2018-2022 crash database with PSI table data.  With this information, the number of crashes by severity can be calculated and related to the PSI values by location.
# 2. Create two sets of tables: One for crashes within 250 feet of an intersection and one for all crashes that occur along segments.
# 3. Identify the following attributes:
#     - Total crash aggregate five-year PSI
#     - Fatal and injury crash aggregate five-year PSI
#     - Number of years PSI analysis identifies a location as having crashes
#     - Number of years PSI analysis identifies a location as having fatal and injury crashes
# 4. Identify segments and intersections using the PSI ranking and crash thresholds as follows:
#     - The top 100 (miles for segments, locations for intersections) of VDOT Potential for Safety Improvement (PSI) Intersections and Segments by PSI rank
#     - Include additional intersections and segments meeting the following criteria:
#         - Locations on PSI list 2+ years out of last five years
#         - Locations on Fatal/Injury PSI List 2+ years out of last five years with at least 3+ fatal or injury crashes at the intersection or segment over the last five years
# 5. **Threshold for Need for Roadway Safety**: Roadway segments and intersections meeting the thresholds in Step 4 above are identified as those with a VTrans Mid-term Need for Roadway Safety.
# 6. Assign intersection safety needs to roadway segments using 150' buffers around the intersections.

# %% [markdown]
# ### Code ###
# Steps 1-5 above have been completed by VDOT and delivered as two CSV tables: INT_PSI_OIPI.csv and SEG_PSI_OIPI.csv.  These tables are converted to a needs event table below.

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %%
# Input PSI data from VDOT
segment_psi_source = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\SEG_PSI_OIPI.csv"
intersection_psi_source = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\INT_PSI_OIPI.csv"

# Path for CSVs that will only contain VTrans needs
segment_psi_csv = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\SEG_PSI_OIPI_vtransNeed.csv"
intersection_psi_csv = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\INT_PSI_OIPI_vtransNeed.csv"

# Only include records that are a VTrans need
df_segment_psi = pd.read_csv(segment_psi_source)
df_segment_psi_vtrans = df_segment_psi.loc[df_segment_psi['TIER'] == 'VTrans']
df_segment_psi_vtrans.to_csv(segment_psi_csv, index=False)
del df_segment_psi

df_intersection_psi = pd.read_csv(intersection_psi_source)
df_intersection_psi_vtrans = df_intersection_psi.loc[df_intersection_psi['TIER'] == 'VTrans']
df_intersection_psi_vtrans.to_csv(intersection_psi_csv, index=False)
del df_intersection_psi


# Database paths
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Roadway Safety\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')


# Overlap LRS
lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'
master_lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_MASTER_LRS_DY'

def make_path(gdb_path, filename):
    return os.path.join(gdb_path, filename)

# CoSS
CoSS = f'{common_datasets_gdb}\\tbl_coss_2023'

# %%
# Create event layer for intersection PSIs using a 150' buffer
intersection_psi_points = make_path(intermediate_gdb, 'intersection_psi_points')
intersection_psi_buffer = make_path(intermediate_gdb, 'intersection_psi_buffer')
arcpy.XYTableToPoint_management(intersection_psi_csv, intersection_psi_points, 'LON', 'LAT', coordinate_system=arcpy.SpatialReference(4326))
arcpy.PairwiseBuffer_analysis(intersection_psi_points, intersection_psi_buffer, '150 FEET', 'ALL')

# Clip LRS to buffer
lrs_clip = make_path(intermediate_gdb, 'lrs_clip')
arcpy.PairwiseClip_analysis(master_lrs, intersection_psi_buffer, lrs_clip)

# Explode LRS Clip to remove multipart segments
lrs_clip_explode = make_path(intermediate_gdb, 'lrs_clip_explode')
arcpy.management.MultipartToSinglepart(lrs_clip, lrs_clip_explode)

# Get begin and end points for LRS Clip
mp_fields = ['BEGIN_MSR', 'END_MSR']
for field in mp_fields:
    if field not in [field.name for field in arcpy.ListFields(lrs_clip_explode)]:
        arcpy.AddField_management(lrs_clip_explode, field, 'DOUBLE')

with arcpy.da.UpdateCursor(lrs_clip_explode, ['BEGIN_MSR', 'END_MSR', 'SHAPE@']) as cur:
    for row in cur:
        geom = row[-1]
        begin_msr = geom.firstPoint.M
        end_msr = geom.lastPoint.M
        row[0] = begin_msr
        row[1] = end_msr
        cur.updateRow(row)

# %%
# Routes not included in the intersection PSI should not be included in the event table.  The clip will include all routes within the buffer.lrs_clip
# This step will create an event table as well as remove routes that should not be included.

# Get list of routes in intersection PSI
psi_routes = []
with arcpy.da.SearchCursor(intersection_psi_points, 'RTE_NAME') as cur:
    for row in cur:
        routes = row[0].split(';')
        for route in routes:
            if route not in psi_routes:
                psi_routes.append(route)

# Make intersection psi needs event table in pandas
fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR']
df_intersection_psi = pd.DataFrame([row for row in arcpy.da.SearchCursor(lrs_clip_explode, fields)], columns=fields)

# Only include routes in psi_routes list
df_intersection_psi = df_intersection_psi.loc[df_intersection_psi['RTE_NM'].isin(psi_routes)]

# %% [markdown]
# #### Create final safety segments event table ####

# %%
# Create dataframe containing all safety segment needs
df_safety_segment = df_segment_psi_vtrans.copy()
df_safety_segment.rename(columns={'BEGIN_MP': 'BEGIN_MSR', 'END_MP': 'END_MSR'}, inplace=True)

# Reduce dataframe to only fields required
fields = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'DIRECTION']
df_safety_segment = df_safety_segment[fields]



# # Add opposite side on routes that are combined direction
# df_get_nonprime_segments = df_safety_segment.loc[df_safety_segment['DIRECTION'] == 'Combined-Direction']

# # Make opposite route dictionary
# df_opposite_route_dict = pd.DataFrame([row for row in arcpy.da.SearchCursor(lrs, ['RTE_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM'])], columns=['RTE_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM'])
# df_get_nonprime_segments = df_get_nonprime_segments.merge(df_opposite_route_dict, on='RTE_NM')

# # Modify to match schema of df_safety_segment dataframe and append
# df_get_nonprime_segments = df_get_nonprime_segments.loc[df_get_nonprime_segments['RTE_OPPOSITE_DIRECTION_RTE_NM'].notnull()]
# df_get_nonprime_segments = df_get_nonprime_segments[['RTE_OPPOSITE_DIRECTION_RTE_NM', 'BEGIN_MSR', 'END_MSR', 'DIRECTION']].rename(columns={'RTE_OPPOSITE_DIRECTION_RTE_NM': 'RTE_NM'})
# df_safety_segment = df_safety_segment.append(df_get_nonprime_segments)

# Remove direction field
df_safety_segment.drop('DIRECTION', axis=1, inplace=True)

# All of these records have safety segment need
df_safety_segment['Safety_Segments'] = 'YES'
df_safety_segment['CoSS_Safety_Segments'] = 'NO'  # Will identify in a later step

# Make final event table
safety_segment_csv = os.path.join(os.path.dirname(intermediate_gdb), 'df_safety_segment.csv')
df_safety_segment.to_csv(safety_segment_csv, index=False)
arcpy.TableToTable_conversion(safety_segment_csv, intermediate_gdb, 'tbl_safety_segment')

# Overlap with CoSS
output_table = os.path.join(output_gdb, 'tbl_safety_segment')
arcpy.lr.OverlayRouteEvents(os.path.join(intermediate_gdb, 'tbl_safety_segment'), 'RTE_NM LINE BEGIN_MSR END_MSR', CoSS, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', output_table, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

# Delete all records where RN Safety Segments do not exist
with arcpy.da.UpdateCursor(output_table, 'Safety_Segments') as cur:
    for row in cur:
        if row[0] == '':
            cur.deleteRow()

# Mark overlaps with CoSS with CoSS Need
with arcpy.da.UpdateCursor(output_table, ['COSS', 'CoSS_Safety_Segments']) as cur:
    for row in cur:
        if row[0] == 1:
            row[1] = 'YES'
        else:
            row[1] = 'NO'
        cur.updateRow(row)

# Delete null values

# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", output_table, "RTE_NM; Line; BEGIN_MSR; END_MSR", "safety_segment Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("safety_segment Events", output_gdb, "safety_segment")

# %% [markdown]
# #### Create final safety intersections event table ####

# %%
# Create dataframe containing all safety intersection needs
df_safety_intersections = df_intersection_psi.copy()

# # Add opposite side routes
# # Reuse opposite route dictionary created above (df_opposite_route_dict)
# df_get_nonprime_intersections = df_safety_intersections.copy()  #  Opposite route needs to be found on all segments
# df_get_nonprime_intersections = df_get_nonprime_intersections.merge(df_opposite_route_dict, on='RTE_NM')


# # Modify to match schema of df_safety_intersections dataframe and append
# df_get_nonprime_intersections = df_get_nonprime_intersections.loc[df_get_nonprime_intersections['RTE_OPPOSITE_DIRECTION_RTE_NM'].notnull()]
# df_get_nonprime_intersections = df_get_nonprime_intersections[['RTE_OPPOSITE_DIRECTION_RTE_NM', 'BEGIN_MSR', 'END_MSR']].rename(columns={'RTE_OPPOSITE_DIRECTION_RTE_NM': 'RTE_NM'})
# df_safety_intersections = df_safety_intersections.append(df_get_nonprime_intersections)

# All of these records have safety segment need
df_safety_intersections['Safety_Intersection'] = 'YES'
df_safety_intersections['CoSS_Safety_Intersection'] = 'NO'  # Will identify in later step

# Make final event table
safety_intersections_csv = os.path.join(os.path.dirname(intermediate_gdb), 'df_safety_intersections.csv')
df_safety_intersections.to_csv(safety_intersections_csv, index=False)
tbl_safety_intersections_predissolve = os.path.join(intermediate_gdb, 'tbl_safety_intersections_predissolve')
arcpy.TableToTable_conversion(safety_intersections_csv, intermediate_gdb, 'tbl_safety_intersections_predissolve')

# Dissolve table to remove potential overlaps
tbl_safety_intersections_dissolve = os.path.join(intermediate_gdb, 'tbl_safety_intersections_dissolve')
arcpy.lr.DissolveRouteEvents(tbl_safety_intersections_predissolve, "RTE_NM; Line; BEGIN_MSR; END_MSR", "Safety_Intersection;CoSS_Safety_Intersection", tbl_safety_intersections_dissolve, "RTE_NM; Line; BEGIN_MSR; END_MSR", "DISSOLVE", "INDEX")

# Overlap with CoSS
output_table = os.path.join(output_gdb, 'tbl_safety_intersections')
arcpy.lr.OverlayRouteEvents(tbl_safety_intersections_dissolve, 'RTE_NM LINE BEGIN_MSR END_MSR', CoSS, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', output_table, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

# Delete all records where RN Safety Segments do not exist
with arcpy.da.UpdateCursor(output_table, 'Safety_Intersection') as cur:
    for row in cur:
        if row[0] == '':
            cur.deleteRow()

# Mark overlaps with CoSS with CoSS Need
with arcpy.da.UpdateCursor(output_table, ['COSS', 'CoSS_Safety_Intersection']) as cur:
    for row in cur:
        if row[0] == 1:
            row[1] = 'YES'
        else:
            row[1] = 'NO'
        cur.updateRow(row)

# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", output_table, "RTE_NM; Line; BEGIN_MSR; END_MSR", "safety_intersection Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("safety_intersection Events", output_gdb, "safety_intersections")

# %%



