FIELD_ALIAS = {
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

FIELD_TYPE = {
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