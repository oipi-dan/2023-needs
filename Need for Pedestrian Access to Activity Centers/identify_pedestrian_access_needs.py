# %% [markdown]
# # Need Category: Walk Access to Activity Centers #
# 
# **Measure**: Activity Centers Pedestrian Walk-sheds
# 
# **What it means**: Areas within walking distance of VTrans Activity Centers. VTrans Activity Centers are identified as “areas of regional importance that have a high density of economic and social activity” and are associated with the Regional Networks Travel Market. Activity Centers have been identified through stakeholder input.
# 
# **Travel Market**: RN
# 
# **Data Sources**:
# 1. Acitvity Centers (OIPI)
# 2. Existing, Planned and Under-Construction Fixed-Guideway and bus rapid transit (BRT) lines: Northern Virginia and
# Fredericksburg Regional Networks, Dulles Corridor Metrorail Project, Hampton Roads Regional Network, Greater
# Richmond Transit Company, Washington Metropolitan Area Transit Authority (GTFS Stops, DRPT)
# 3. Table B08534: Means of Transportation to Work by Travel Time to Work (US Census Bureau ACS)
# 4. Metropolitan Planning Organization (MPO) boundaries in Virginia
# 5. Transit stops in Virginia (GTFS Stops, DRPT)
# 
# **Year of Analysis**: 2022

# %% [markdown]
# #### Calculations ####
# 
# 1. Generate walk needs buffers of 1 mile around the Activity Centers, fixed-guideway transit stations, and BRT lines.
# 2. Identify applicable roadway segments as those within the 1-mile buffer that are characterized as a non-limited access
# facility and are functionally classified above Local Streets.
#     * Create event table for lrs within buffer area
#     * Create event table for non-limited access routes with functional classification greater than local
#     * Overlap the above event tables.  This result represents the pedestrian access needs.
# 3. Applicable roadway segments within one mile of Activity Centers, fixed-guideway transit stations, and BRT lines are identified as those with a VTrans Mid-term Need
# for Pedestrian Access to Activity Centers.

# %% [markdown]
# #### Code ####

# %%
import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True


main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

# %% [markdown]
# #### Input parameters ####
# Set the following input parameters:
# 1. walk_speed - obtained from Manual on Uniform Traffic Control Devices
# 2. walk_commute_time - Virginia's 90th percentile single-mode walk commute time from ACS Table B08534
# 3. walk_needs_radius - calculated by multiplying the walk speed by the walk commute time and rounding the result to the nearest integer

# %%
walk_speed = 2.4  # mph
walk_commute_time = 25  # minutes
walk_commute_time_hr = walk_commute_time / 60  # Convert to hours to match walk speed units
walk_needs_radius = round(walk_speed * walk_commute_time_hr)

# %% [markdown]
# #### Data Sources ####
# 1. Acitvity Centers (OIPI)
# 2. Existing, Planned and Under-Construction Fixed-Guideway and bus rapid transit (BRT) lines: Northern Virginia and
# Fredericksburg Regional Networks, Dulles Corridor Metrorail Project, Hampton Roads Regional Network, Greater
# Richmond Transit Company, Washington Metropolitan Area Transit Authority (GTFS Stops, DRPT)
# 3. Table B08534: Means of Transportation to Work by Travel Time to Work (US Census Bureau ACS)
# 4. Metropolitan Planning Organization (MPO) boundaries in Virginia
# 5. Transit stops in Virginia (GTFS Stops, DRPT)

# %%
intermediate_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Pedestrian Access to Activity Centers\\data\\intermediate.gdb"
output_gdb = f"{main_path}\\A1 - Common Datasets\\Need for Pedestrian Access to Activity Centers\\data\\output.gdb"

# Create gdbs if do not exist
for gdb_path in [intermediate_gdb, output_gdb]:
    if os.path.exists(os.path.dirname(gdb_path)):
        if not os.path.exists(gdb_path):
            arcpy.management.CreateFileGDB(os.path.dirname(gdb_path), os.path.basename(gdb_path))
    else:
        raise Exception(f'Path for GDB does not exist: \n{os.path.dirname(gdb_path)}')

# MPO Boundaries
mpo_boundaries_source = f'{common_datasets_gdb}\\MPO'
mpo_boundaries = os.path.join(intermediate_gdb, 'MPO')
arcpy.Project_management(mpo_boundaries_source, mpo_boundaries, arcpy.SpatialReference(3969))


# Activity Centers - project to VA lambert, retaining only knowledge-based and local-serving Activity Centers inside of MPO boundaries.
activity_centers_source = f'{common_datasets_gdb}\\VTrans_Activity_Centers'

activity_centers_mpos = os.path.join(intermediate_gdb, 'activity_centers_mpos')
arcpy.PairwiseClip_analysis(activity_centers_source, mpo_boundaries, activity_centers_mpos)

# Filter activity centers to local-serving and knowledge-based
activity_centers_filtered = os.path.join(intermediate_gdb, 'VTrans_Activity_Centers_Filtered')
sql = "prmry_c IN ('local serving', 'knowledge')"
arcpy.FeatureClassToFeatureClass_conversion(activity_centers_mpos, intermediate_gdb, 'VTrans_Activity_Centers_Filtered', sql)

activity_centers = os.path.join(intermediate_gdb, 'VTrans_Activity_Centers')
arcpy.Project_management(activity_centers_filtered, activity_centers, arcpy.SpatialReference(3969))


# RN Boundaries
rn_boundaries = f'{common_datasets_gdb}\\RegionalNetworks'

# GTFS Stops - fixed guideway only (DC metro, VRE, Amtrak, Pulse, Tide) retain only stops within MPO boundaries
gtfs_stops_source = f'{common_datasets_gdb}\\FixedGuideway_Transit'
arcpy.MakeFeatureLayer_management(gtfs_stops_source, 'lyr_gtfs_stops')
arcpy.MakeFeatureLayer_management(mpo_boundaries_source, 'lyr_mpo_boundaries')
arcpy.SelectLayerByLocation_management('lyr_gtfs_stops', 'INTERSECT', 'lyr_mpo_boundaries')
arcpy.FeatureClassToFeatureClass_conversion('lyr_gtfs_stops', intermediate_gdb, 'gtfs_stops_filtered')
gtfs_stops_filtered = os.path.join(intermediate_gdb, 'gtfs_stops_filtered')
arcpy.Delete_management('lyr_gtfs_stops')
arcpy.Delete_management('lyr_mpo_boundaries')

gtfs_stops = os.path.join(intermediate_gdb, 'Layer__GTFS_Stops')
arcpy.Project_management(gtfs_stops_filtered, gtfs_stops, arcpy.SpatialReference(3969))

# Functional Classification event table.  Create a new table that excludes local routes
tbl_fc = f'{common_datasets_gdb}\\tbl_fc23'
sql = 'STATE_FUNCT_CLASS_ID < 7'
arcpy.TableToTable_conversion(tbl_fc, intermediate_gdb, 'tbl_fc_noLocal', sql)
tbl_fc = os.path.join(intermediate_gdb, 'tbl_fc_noLocal')

# Overlap LRS
lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

# Limited Access
tbl_limited_access = f'{common_datasets_gdb}\\tbl_limited_access'
arcpy.TableToTable_conversion(tbl_limited_access, intermediate_gdb, 'tbl_la')
tbl_limited_access = os.path.join(intermediate_gdb, 'tbl_la')
if 'la' not in [field.name for field in arcpy.ListFields(tbl_limited_access)]:
    arcpy.AddField_management(tbl_limited_access, 'la', 'SHORT')
    with arcpy.da.UpdateCursor(tbl_limited_access, 'la') as cur:
        for row in cur:
            row[0] = 1
            cur.updateRow(row)


# %% [markdown]
# ### Calculations ###
# 1. Generate walk needs buffers of 1 mile around the Activity Centers, fixed-guideway transit stations, and BRT lines.
# 2. Identify applicable roadway segments as those within the 1-mile buffer that are characterized as a non-limited access
# facility and are functionally classified above Local Streets.
#     * Create event table for lrs within buffer area
#     * Create event table for non-limited access routes with functional classification greater than local
#     * Overlap the above event tables.  This result represents the pedestrian access needs.
# 3. Applicable roadway segments within one mile of Activity Centers, fixed-guideway transit stations, and BRT lines are identified as those with a VTrans Mid-term Need
# for Pedestrian Access to Activity Centers.

# %%
# Generate walk needs buffer
activity_centers_buffer = os.path.join(intermediate_gdb, 'activity_centers_buffer')
arcpy.analysis.PairwiseBuffer(activity_centers, activity_centers_buffer, f'{walk_needs_radius} MILES', "ALL", None, "GEODESIC", "0 DecimalDegrees")

gtfs_stops_dissolved = os.path.join(intermediate_gdb, 'gtfs_stops_dissolved')
arcpy.analysis.PairwiseDissolve(gtfs_stops, gtfs_stops_dissolved, None, None, "MULTI_PART")
gtfs_stops_buffer = os.path.join(intermediate_gdb, 'gtfs_stops_buffer')
arcpy.analysis.PairwiseBuffer(gtfs_stops_dissolved, gtfs_stops_buffer, f'{walk_needs_radius} MILES', "ALL", None, "GEODESIC", "0 DecimalDegrees")

walk_needs_buffer_source = os.path.join(intermediate_gdb, 'walk_needs_buffer_source')
# arcpy.analysis.PairwiseIntersect([activity_centers_buffer, gtfs_stops_buffer], walk_needs_buffer_source)
arcpy.analysis.Union([activity_centers_buffer, gtfs_stops_buffer], walk_needs_buffer_source)
walk_needs_buffer = os.path.join(intermediate_gdb, 'walk_needs_buffer')
arcpy.analysis.PairwiseDissolve(walk_needs_buffer_source, walk_needs_buffer, None, None, "MULTI_PART")

lrs_clip = os.path.join(intermediate_gdb, 'lrs_clip')
lrs_clip_rn = os.path.join(intermediate_gdb, 'lrs_clip_rn')
lrs_clip_explode = os.path.join(intermediate_gdb, 'lrs_clip_explode')
arcpy.analysis.PairwiseClip(lrs, walk_needs_buffer, lrs_clip)
arcpy.analysis.PairwiseClip(lrs_clip, rn_boundaries, lrs_clip_rn)
arcpy.management.MultipartToSinglepart(lrs_clip_rn, lrs_clip_explode)
# Add mp fields to lrs_clip_explode if they do not yet exist
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

tbl_lrs_clip_explode = os.path.join(intermediate_gdb, 'tbl_lrs_clip_explode')
arcpy.TableToTable_conversion(lrs_clip_explode, intermediate_gdb, 'tbl_lrs_clip_explode')

# %%
# Overlay event tables
tbl_la_fc = os.path.join(intermediate_gdb, 'tbl_la_fc')
arcpy.lr.OverlayRouteEvents(tbl_limited_access, 'RTE_NM LINE RTE_TO_MSR RTE_FROM_MSR', tbl_fc, 'RTE_NM LINE BEGIN_MSR END_MSR', 'UNION', tbl_la_fc, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

tbl_la_fc_buffer = os.path.join(intermediate_gdb, 'tbl_la_fc_buffer')
arcpy.lr.OverlayRouteEvents(tbl_la_fc, 'RTE_NM LINE BEGIN_MSR END_MSR', tbl_lrs_clip_explode, 'RTE_NM LINE BEGIN_MSR END_MSR', 'INTERSECT', tbl_la_fc_buffer, 'RTE_NM LINE BEGIN_MSR END_MSR', zero_length_events='NO_ZERO')

# Create needs field.  Need = 1 where not limited access (la = 0)
sql = 'la = 0'
arcpy.AddField_management(tbl_la_fc_buffer, 'RN_AC_Pedestrian_Access', 'TEXT')
with arcpy.da.UpdateCursor(tbl_la_fc_buffer, ['la', 'RN_AC_Pedestrian_Access']) as cur:
    for row in cur:
        if row[0] == 0:
            row[1] = 'YES'
        else:
            row[1] = 'NO'
        cur.updateRow(row)

# %% [markdown]
# #### Create output event table and layer ####

# %%
# Create a dataframe from the previous output that will  match the required schema for needs
fields_to_keep = ['RTE_NM', 'BEGIN_MSR', 'END_MSR', 'RN_AC_Pedestrian_Access']
df = pd.DataFrame([row for row in arcpy.da.SearchCursor(tbl_la_fc_buffer, fields_to_keep)], columns=fields_to_keep)

# Place fields in order specified in schema sheet
df = df[fields_to_keep]

# Export to csv
output_csv = os.path.join(os.path.dirname(output_gdb), 'output.csv')
df.to_csv(output_csv, index=False)

# Make gdb event table
arcpy.TableToTable_conversion(output_csv, output_gdb, 'tbl_ped_access')

# Make route event layer
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", output_csv, "RTE_NM; Line; BEGIN_MSR; END_MSR", "tbl_ped_access Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_ped_access Events", output_gdb, "Walk_Access_to_Activity_Centers")


# %%



