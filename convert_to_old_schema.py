""" We developed these scripts with a new schema in mind that
improves on clarity and consistency compared to the last version
of the needs file.  In the end we needed to use the same schema
as the previous needs file.  Rather than changing all of the
individual scripts and risk breaking everything, this script will
convert the new schema to the old schema. """

import pandas as pd
import numpy as np
import arcpy
import os

arcpy.env.overwriteOutput = True
main_path = os.path.dirname(os.path.abspath(__file__))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')

new_source = f'{main_path}\\2023_VTrans_MidTerm_Needs.gdb\VTrans_MidTerm_Needs_2023'
output_gdb = f'{main_path}\\2023_VTrans_MidTerm_Needs.gdb'
output_tbl_name = 'tbl_VTrans_MidTerm_Needs_2023_Old_Schema'
output_event_layer_name = 'VTrans_MidTerm_Needs_2023_Old_Schema'
lrs = f'{common_datasets_gdb}\\SDE_VDOT_RTE_OVERLAP_LRS_DY'

OLD_FIELD_ALIAS = {
    'Segment_ID': 'Segment ID',
    'ST_NM': 'Street Name',
    'VDOT_RM': 'Route Name',
    'VDOT_COMMON_NM': 'Route Common Name',
    'From_measure': 'From Measure',
    'To_measure': 'To Measure',
    'Segment_Length': 'Segment Length',
    'MASTER_RTE_NM': 'Master Route Name',
    'RTE_OPPOSITE_DIRECTION_RTE_NM': 'Route Opposite Direction',
    'Direction': 'Direction',
    'VDOT_FC': 'Functional Classification',
    'VDOT_District': 'VDOT Construction District',
    'MPO': 'Metropolitan Planning Organization',
    'AADT_2018': 'AADT',
    'CoSS': 'Corridor of Statewide Significance',
    'CoSS_Primary': 'Corridor of Statewide Significance - Primary Facility',
    'CoSS_Name': 'CoSS Name',
    'CoSS_congestion': 'Need - Congestion Mitigation (CoSS)',
    'CoSS_reliability': 'Need - Improved Reliability (CoSS)',
    'CoSS_Rail_Reliability': 'Need - Rail On-time Performance (CoSS)',
    'CoSS_capacity_preservation': 'Need - Capacity Preservation (CoSS)',
    'CoSS_LA_TDM': 'Need - Transportation Demand Management (Limited Access CoSS)',
    'CoSS_non_LA_TDM': 'Need - Transportation Demand Management (non-limited Access CoSS)',
    'RN_Name': 'Regional Network Name',
    'RN_congestion': 'Need - Congestion Mitigation (RN)',
    'RN_reliability': 'Need - Improved Reliability (RN)',
    'RN_Capacity_Preservation': 'Need - Capacity Preservation (RN)',
    'RN_LA_TDM': 'Need - Transportation Demand Management (Limited Access RN)',
    'RN_non_LA_TDM': 'Need - Transportation Demand Management (Non-Limited Access RN)',
    'RN_transit_equity': 'Need - Transit Access for Equity Emphasis Areas (RN)',
    'RN_AC_Transit_Access': 'Need - Transit Access (RN)',
    'RN_AC_Bicycle_Access': 'Need - Bicycle Access (RN)',
    'RN_AC_pedestrian_access': 'Need - Pedestrian Access (RN)',
    'UDA': 'In Urban Development Area',
    'UDA_Name': 'UDA Name',
    'UDA_road_capacity': 'Need - Roadway capacity (UDA)',
    'UDA_road_ops': 'Need - Roadway operations (UDA)',
    'UDA_transit_freq': 'Need - Transit frequency (UDA)',
    'UDA_transit_ops': 'Need - Transit operations (UDA)',
    'UDA_transit_capacity': 'Need - Transit capacity (UDA)',
    'UDA_transit_facilities': 'Need - Transit facilities (UDA)',
    'UDA_street_grid': 'Need - Street Grid (UDA)',
    'UDA_bike_infrast': 'Need - Bicycle Infrastructure (UDA)',
    'UDA_ped_infrast': 'Need - Pedestrian Infrastructure (UDA)',
    'UDA_comp_street': 'Need - Complete Streets (UDA)',
    'UDA_safety_feat': 'Need - Safety features (UDA)',
    'UDA_onstreet_park': 'Need - On-street parking (UDA)',
    'UDA_offstreet_park': 'Need - Off-street parking (UDA)',
    'UDA_intersection_des': 'Need - Intersection design (UDA)',
    'UDA_signage': 'Need - Signage/wayfinding(UDA)',
    'UDA_traffic_calm': 'Need -Traffic calming (UDA)',
    'UDA_landscape': 'Need - Environment (UDA)',
    'UDA_sidewalk': 'Need - Sidewalks (UDA)',
    'RN_Growth_Area': 'RN eligible UDA Needs',
    'IEDA': 'Need for Improved Access to Industrial and Economic Development Area',
    'Safety_Segments': 'Need - Safety Improvement (Segment)',
    'CoSS_Safety_Segments': 'Need - Safety Improvement (CoSS Segment)',
    'Safety_Intersection': 'Need - Safety Improvement (Intersection)',
    'CoSS_Safety_Intersection': 'Need - Safety Improvement (CoSS Intersection)',
    'Safety_Pedestrian': 'Need - Pedestrian Safety Improvement',
    'All_Limited_Access': 'All Limited Access',
    'Select_Limited_Access': 'Select Limited Access'
}

OLD_FIELD_TYPE = {
    'Segment_ID': 'TEXT',
    'ST_NM': 'TEXT',
    'VDOT_RM': 'TEXT',
    'VDOT_COMMON_NM': 'TEXT',
    'From_measure': 'DOUBLE',
    'To_measure': 'DOUBLE',
    'Segment_Length': 'DOUBLE',
    'MASTER_RTE_NM': 'TEXT',
    'RTE_OPPOSITE_DIRECTION_RTE_NM': 'TEXT',
    'Direction': 'TEXT',
    'VDOT_FC': 'TEXT',
    'VDOT_District': 'TEXT',
    'MPO': 'TEXT',
    'AADT_2018': 'Integer',
    'CoSS': 'TEXT',
    'CoSS_Primary': 'TEXT',
    'CoSS_Name': 'TEXT',
    'CoSS_congestion': 'TEXT',
    'CoSS_reliability': 'TEXT',
    'CoSS_Rail_Reliability': 'TEXT',
    'CoSS_capacity_preservation': 'TEXT',
    'CoSS_LA_TDM': 'TEXT',
    'CoSS_non_LA_TDM': 'TEXT',
    'RN_Name': 'TEXT',
    'RN_congestion': 'TEXT',
    'RN_reliability': 'TEXT',
    'RN_Capacity_Preservation': 'TEXT',
    'RN_LA_TDM': 'TEXT',
    'RN_non_LA_TDM': 'TEXT',
    'RN_transit_equity': 'TEXT',
    'RN_AC_Transit_Access': 'TEXT',
    'RN_AC_Bicycle_Access': 'TEXT',
    'RN_AC_pedestrian_access': 'TEXT',
    'UDA': 'TEXT',
    'UDA_Name': 'TEXT',
    'UDA_road_capacity': 'TEXT',
    'UDA_road_ops': 'TEXT',
    'UDA_transit_freq': 'TEXT',
    'UDA_transit_ops': 'TEXT',
    'UDA_transit_capacity': 'TEXT',
    'UDA_transit_facilities': 'TEXT',
    'UDA_street_grid': 'TEXT',
    'UDA_bike_infrast': 'TEXT',
    'UDA_ped_infrast': 'TEXT',
    'UDA_comp_street': 'TEXT',
    'UDA_safety_feat': 'TEXT',
    'UDA_onstreet_park': 'TEXT',
    'UDA_offstreet_park': 'TEXT',
    'UDA_intersection_des': 'TEXT',
    'UDA_signage': 'TEXT',
    'UDA_traffic_calm': 'TEXT',
    'UDA_landscape': 'TEXT',
    'UDA_sidewalk': 'TEXT',
    'RN_Growth_Area': 'TEXT',
    'IEDA': 'TEXT',
    'Safety_Segments': 'TEXT',
    'CoSS_Safety_Segments': 'TEXT',
    'Safety_Intersection': 'TEXT',
    'CoSS_Safety_Intersection': 'TEXT',
    'Safety_Pedestrian': 'TEXT',
    'All_Limited_Access': 'TEXT',
    'Select_Limited_Access': 'TEXT'
}

NEW_FIELD_ALIAS = {
    'Segment_ID': 'Segment ID',
    'ST_NM' : 'Street Name',
    'RTE_NM' : 'Route Name',
    'VDOT_COMMON_NM' : 'Route Common Name',
    'BEGIN_MSR' : 'From Measure',
    'END_MSR' : 'To Measure',
    'Segment_Length' : 'Segment Length',
    'MASTER_RTE_NM' : 'Master Route Name',
    'RTE_OPPOSITE_DIRECTION_RTE_NM' : 'Route Opposite Direction',
    'Direction' : 'Direction',
    'VDOT_FC' : 'Functional Classification',
    'VDOT_District' : 'VDOT Construction District',
    'MPO' : 'Metropolitan Planning Organization',
    'CoSS' : 'Corridor of Statewide Significance (CoSS)',
    'CoSS_Primary' : 'CoSS Primary Facility',
    'CoSS_Name' : 'CoSS Name',
    'RN_Name' : 'RN Name',
    'UDA': 'In Urban Development Area',
    'UDA_Name': 'UDA Name',
    'CoSS_Congestion' : 'Need - Congestion Mitigation (CoSS)',
    'CoSS_Reliability' : 'Need - Improved Reliability (CoSS)',
    'CoSS_Rail_Reliability' : 'Need - Rail On-time Performance (CoSS)',
    'CoSS_Capacity_Preservation' : 'Need - Capacity Preservation (CoSS)',
    'CoSS_LA_TDM' : 'Need - Transportation Demand Management (Limited Access CoSS)',
    'CoSS_non_LA_TDM': 'Need - Transportation Demand Management (non-limited Access CoSS)',
    'CoSS_Safety_Intersection' : 'Need - Safety Improvement (CoSS Intersection)',
    'CoSS_Safety_Segments' : 'Need - Safety Improvement (CoSS Segment)',
    'RN_Congestion' : 'Need - Congestion Mitigation (RN)',
    'RN_Reliability' : 'Need - Improved Reliability (RN)',
    'RN_Capacity_Preservation' : 'Need - Capacity Preservation (RN)',
    'RN_LA_TDM' : 'Need - Transportation Demand Management (Limited Access RN)',
    'RN_non_LA_TDM' : 'Need - Transportation Demand Management (Non-Limited Access RN)',
    'RN_AC_Bicycle_Access' : 'Need - Bicycle Access (RN)',
    'RN_AC_Pedestrian_Access' : 'Need - Pedestrian Access (RN)',
    'RN_AC_Transit_Access' : 'Need - Transit Access (RN)',
    'RN_Transit_Equity' : 'Need - Transit Access for Equity Emphasis Areas (RN)',
    'Safety_Segments' : 'Need - Safety Improvement (Segment)',
    'Safety_Intersection' : 'Need - Safety Improvement (Intersection)',
    'Safety_Pedestrian' : 'Need - Pedestrian Safety Improvement',
    'IEDA' : 'Need - Improved Access to Industrial and Economic Development Area',
    'UDA_Bike_Infrast': 'Need - Bicycle Infrastructure (UDA)',
    'UDA_Comp_Street': 'Need - Complete Streets (UDA)',
    'UDA_Intersection_Des': 'Need - Intersection design (UDA)',
    'UDA_Landscape': 'Need - Environment (UDA)',
    'UDA_Offstreet_Park': 'Need - Off-street parking (UDA)',
    'UDA_Onstreet_Park': 'Need - On-street parking (UDA)',
    'UDA_Ped_Infrast': 'Need - Pedestrian Infrastructure (UDA)',
    'UDA_Road_Capacity': 'Need - Roadway capacity (UDA)',
    'UDA_Road_Ops': 'Need - Roadway operations (UDA)',
    'UDA_Safety_Feat': 'Need - Safety features (UDA)',
    'UDA_Sidewalk': 'Need - Sidewalks (UDA)',
    'UDA_Signage': 'Need - Signage/wayfinding(UDA)',
    'UDA_Street_Grid': 'Need - Street Grid (UDA)',
    'UDA_Traffic_Calm': 'Need -Traffic calming (UDA)',
    'UDA_Transit_Capacity': 'Need - Transit capacity (UDA)',
    'UDA_Transit_Facilities': 'Need - Transit facilities (UDA)',
    'UDA_Transit_Freq': 'Need - Transit frequency (UDA)',
    'UDA_Transit_Ops': 'Need - Transit operations (UDA)',
    'RN_Growth_Area': 'RN eligible UDA Needs'
}

NEW_FIELD_TYPE = {
    'Segment_ID': 'TEXT',
    'ST_NM' : 'TEXT',
    'RTE_NM' : 'TEXT',
    'VDOT_COMMON_NM' : 'TEXT',
    'BEGIN_MSR' : 'DOUBLE',
    'END_MSR' : 'DOUBLE',
    'Segment_Length' : 'DOUBLE',
    'MASTER_RTE_NM' : 'TEXT',
    'RTE_OPPOSITE_DIRECTION_RTE_NM' : 'TEXT',
    'Direction' : 'TEXT',
    'VDOT_FC' : 'TEXT',
    'VDOT_District' : 'TEXT',
    'MPO' : 'TEXT',
    'Census_Urbanized' : 'TEXT',
    'SS_Area_Type' : 'TEXT',
    'CoSS' : 'TEXT',
    'CoSS_Primary' : 'TEXT',
    'CoSS_Name' : 'TEXT',
    'RN_Name' : 'TEXT',
    'UDA': 'TEXT',
    'UDA_Name': 'TEXT',
    'CoSS_Congestion' : 'TEXT',
    'CoSS_Reliability' : 'TEXT',
    'CoSS_Rail_Reliability' : 'TEXT',
    'CoSS_Capacity_Preservation' : 'TEXT',
    'CoSS_LA_TDM' : 'TEXT',
    'CoSS_non_LA_TDM': 'TEXT',
    'CoSS_Safety_Intersection' : 'TEXT',
    'CoSS_Safety_Segments' : 'TEXT',
    'RN_Congestion' : 'TEXT',
    'RN_Reliability' : 'TEXT',
    'RN_Capacity_Preservation' : 'TEXT',
    'RN_LA_TDM' : 'TEXT',
    'RN_non_LA_TDM' : 'TEXT',
    'RN_AC_Bicycle_Access' : 'TEXT',
    'RN_AC_Pedestrian_Access' : 'TEXT',
    'RN_AC_Transit_Access' : 'TEXT',
    'RN_Transit_Equity' : 'TEXT',
    'Safety_Segments' : 'TEXT',
    'Safety_Intersection' : 'TEXT',
    'Safety_Pedestrian' : 'TEXT',
    'IEDA' : 'TEXT',
    'UDA_Bike_Infrast': 'TEXT',
    'UDA_Comp_Street': 'TEXT',
    'UDA_Intersection_Des': 'TEXT',
    'UDA_Landscape': 'TEXT',
    'UDA_Offstreet_Park': 'TEXT',
    'UDA_Onstreet_Park': 'TEXT',
    'UDA_Ped_Infrast': 'TEXT',
    'UDA_Road_Capacity': 'TEXT',
    'UDA_Road_Ops': 'TEXT',
    'UDA_Safety_Feat': 'TEXT',
    'UDA_Sidewalk': 'TEXT',
    'UDA_Signage': 'TEXT',
    'UDA_Street_Grid': 'TEXT',
    'UDA_Traffic_Calm': 'TEXT',
    'UDA_Transit_Capacity': 'TEXT',
    'UDA_Transit_Facilities': 'TEXT',
    'UDA_Transit_Freq': 'TEXT',
    'UDA_Transit_Ops': 'TEXT',
    'RN_Growth_Area': 'TEXT'
}


class Field:
  def __init__(self, name, alias, type):
    self.name = name
    self.alias = alias
    self.type = type


# Create DataFrame for input data in new schema
new_cols = [field for field in NEW_FIELD_ALIAS]
df_new_data = pd.DataFrame([row for row in arcpy.da.SearchCursor(new_source, new_cols)], columns=new_cols)

# Dictionary showing how to rename each column
dict_col_rename = {'Segment_ID': 'Segment_ID','ST_NM': 'ST_NM','RTE_NM': 'VDOT_RM','VDOT_COMMON_NM': 'VDOT_COMMON_NM','BEGIN_MSR': 'From_measure','END_MSR': 'To_measure','Segment_Length': 'Segment_Length','MASTER_RTE_NM': 'MASTER_RTE_NM','RTE_OPPOSITE_DIRECTION_RTE_NM': 'RTE_OPPOSITE_DIRECTION_RTE_NM','Direction': 'Direction','VDOT_FC': 'VDOT_FC','VDOT_District': 'VDOT_District','MPO': 'MPO','AADT_2018': 'AADT_2018','CoSS': 'CoSS','CoSS_Primary': 'CoSS_Primary','CoSS_Name': 'CoSS_Name','CoSS_Congestion': 'CoSS_congestion','CoSS_Reliability': 'CoSS_reliability','CoSS_Rail_Reliability': 'CoSS_Rail_Reliability','CoSS_Capacity_Preservation': 'CoSS_capacity_preservation','CoSS_LA_TDM': 'CoSS_LA_TDM','CoSS_non_LA_TDM': 'CoSS_non_LA_TDM','RN_Name': 'RN_Name','RN_Congestion': 'RN_congestion','RN_Reliability': 'RN_reliability','RN_Capacity_Preservation': 'RN_Capacity_Preservation','RN_LA_TDM': 'RN_LA_TDM','RN_non_LA_TDM': 'RN_non_LA_TDM', 'RN_AC_Bicycle_Access': 'RN_AC_Bicycle_Access','RN_AC_Pedestrian_Access': 'RN_AC_pedestrian_access','RN_AC_Transit_Access': 'RN_AC_Transit_Access','RN_Transit_Equity': 'RN_transit_equity','UDA': 'UDA','UDA_Name': 'UDA_Name','UDA_Road_Capacity': 'UDA_road_capacity','UDA_Road_Ops': 'UDA_road_ops','UDA_Transit_Freq': 'UDA_transit_freq','UDA_Transit_Ops': 'UDA_transit_ops','UDA_Transit_Capacity': 'UDA_transit_capacity','UDA_Transit_Facilities': 'UDA_transit_facilities','UDA_Street_Grid': 'UDA_street_grid','UDA_Bike_Infrast': 'UDA_bike_infrast','UDA_Ped_Infrast': 'UDA_ped_infrast','UDA_Comp_Street': 'UDA_comp_street','UDA_Safety_Feat': 'UDA_safety_feat','UDA_Onstreet_Park': 'UDA_onstreet_park','UDA_Offstreet_Park': 'UDA_offstreet_park','UDA_Intersection_Des': 'UDA_intersection_des','UDA_Signage': 'UDA_signage','UDA_Traffic_Calm': 'UDA_traffic_calm','UDA_Landscape': 'UDA_landscape','UDA_Sidewalk': 'UDA_sidewalk','RN_Growth_Area': 'RN_Growth_Area','IEDA': 'IEDA','Safety_Segments': 'Safety_Segments','CoSS_Safety_Segments': 'CoSS_Safety_Segments','Safety_Intersection': 'Safety_Intersection','CoSS_Safety_Intersection': 'CoSS_Safety_Intersection','Safety_Pedestrian': 'Safety_Pedestrian','All_Limited_Access': 'All_Limited_Access','Select_Limited_Access': 'Select_Limited_Access'}
df_new_data.rename(columns=dict_col_rename, inplace=True)

# Add missing columns to input data
df_new_data['AADT_2018'] = np.nan
df_new_data['All_Limited_Access'] = np.nan
df_new_data['Select_Limited_Access'] = np.nan

# Reorder input data to match order of old schema
new_col_order = ['Segment_ID', 'ST_NM', 'VDOT_RM', 'VDOT_COMMON_NM', 'From_measure', 'To_measure', 'Segment_Length', 'MASTER_RTE_NM', 'RTE_OPPOSITE_DIRECTION_RTE_NM', 'Direction', 'VDOT_FC', 'VDOT_District', 'MPO', 'AADT_2018', 'CoSS', 'CoSS_Primary', 'CoSS_Name', 'CoSS_congestion', 'CoSS_reliability', 'CoSS_Rail_Reliability', 'CoSS_capacity_preservation', 'CoSS_LA_TDM', 'CoSS_non_LA_TDM', 'RN_Name', 'RN_congestion', 'RN_reliability', 'RN_Capacity_Preservation', 'RN_LA_TDM', 'RN_non_LA_TDM', 'RN_transit_equity', 'RN_AC_Transit_Access', 'RN_AC_Bicycle_Access', 'RN_AC_pedestrian_access', 'UDA', 'UDA_Name', 'UDA_road_capacity', 'UDA_road_ops', 'UDA_transit_freq', 'UDA_transit_ops', 'UDA_transit_capacity', 'UDA_transit_facilities', 'UDA_street_grid', 'UDA_bike_infrast', 'UDA_ped_infrast', 'UDA_comp_street', 'UDA_safety_feat', 'UDA_onstreet_park', 'UDA_offstreet_park', 'UDA_intersection_des', 'UDA_signage', 'UDA_traffic_calm', 'UDA_landscape', 'UDA_sidewalk', 'RN_Growth_Area', 'IEDA', 'Safety_Segments', 'CoSS_Safety_Segments', 'Safety_Intersection', 'CoSS_Safety_Intersection', 'Safety_Pedestrian', 'All_Limited_Access', 'Select_Limited_Access']
df_new_data = df_new_data[new_col_order]

# Create output table
print('Make output table')
tbl_output = os.path.join(output_gdb, output_tbl_name)
arcpy.CreateTable_management(output_gdb, os.path.basename(tbl_output))
for f in OLD_FIELD_ALIAS:
    field = Field(name=f, alias=OLD_FIELD_ALIAS[f], type=OLD_FIELD_TYPE[f])
    arcpy.AddField_management(tbl_output, field.name, field.type, field_alias=field.alias)

# Insert data into output table
output_data = df_new_data.values.tolist()
with arcpy.da.InsertCursor(tbl_output, new_col_order) as cur:
    for row in output_data:
        cur.insertRow(row)

print('Make output event layer')
arcpy.lr.MakeRouteEventLayer(lrs, "RTE_NM", tbl_output, "VDOT_RM; Line; From_measure; To_measure", "tbl_output Events", None, "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
arcpy.conversion.FeatureClassToFeatureClass("tbl_output Events", output_gdb, output_event_layer_name)

print('Done')