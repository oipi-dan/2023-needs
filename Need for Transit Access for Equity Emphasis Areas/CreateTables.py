#===============================================================================
# Create 5-year ACS Tables for IntearctVTrans
#===============================================================================
# This script pulls statistics from calendar import LocaleTextCalendar
# from the 5-Year American Community Survey that are 
# most relevant to determining the VTrans Mid-Term Needs for display on 
# InteractVTrans.
#
# Before running, it's important to ensure that the data in StatsDict.py is
# accurate, as the tables are built using that file as a reference.
#
# It will create a CSV file for each of the items in the ACS_Tables list located
# in StatsDict.py.
#===============================================================================
# Written for ArcGIS Pro Python Environment
# By Dan Fourquet
# September 2022
#===============================================================================

import pandas as pd
import arcpy
import os
import requests

from StatsDict import ACS_Tables

main_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
common_datasets_gdb = os.path.join(main_path, r'A1 - Common Datasets\Common_Datasets.gdb')


# Input census data
inputGDB = common_datasets_gdb
censusCounties = "County"
censusBlockGroups = "Block_Group"
censusTracts = "Tracts"

# Output directory for CSV files
output_dir = f"{main_path}\\Need for Transit Access for Equity Emphasis Areas"

if not os.path.exists(output_dir):
    raise Exception("Output directory does not exist.")


def build_url(table, data, geography):
    URL_base = "https://api.census.gov/data/2021/acs/acs5?"
    if table['tableType'] == 'Subject':
        URL_base = "https://api.census.gov/data/2021/acs/acs5/subject?"

    URL_for = "&for=block%20group:*&in=state:51%20county:*"

    if geography == "county":
        URL_for = "&for=county:*&in=state:51"
    if geography == "tract":
        URL_for = "&for=tract:*&in=state:51"
    if geography == "block group":
        URL_for = "&for=block%20group:*&in=state:51%20county:*"
    

    if table['fullTable']:
        # Download entire table
        URL_get = "get="
        URL_get += f"group({table['fullTable']}),"
    else:
        URL_get = "get=NAME,GEO_ID,"
        # Download individual statistics
        for stat in data.keys():
            URL_get += f"{stat},"

    URL = f"{URL_base}{URL_get[:-1]}{URL_for}"
    print(f"    URL:    {URL}")

    return URL


def get_data(URL):
    try:
        response = requests.get(URL)
        data = list(response.json())

        return data
    except Exception as e:
        print("Error creating URL\n--")
        print(e)
        print("\n==========\n")
        
        return None


def create_dataframe(table, data):
    try:
        columns = data[0]
        data = data[1:]
        df = pd.DataFrame(data,columns=columns)
        df = df.apply(pd.to_numeric, errors='ignore', downcast='integer')

        # Apply functions
        if table['functions']:
            for f in table['functions']:
                funcName = f['name']
                funcAlias = f['alias']
                funcOperation = f['operation']
                funcStatistics = f['statistics']

                print(f"    Calculating {funcName}")
                if funcOperation == "sum":
                    df[funcName] = df[funcStatistics].sum(axis=1)

                if funcOperation == "diff":
                    df[funcName] = abs(df[funcStatistics[0]]-df[funcStatistics[1]])

                if funcOperation == "percent":
                    df[funcName] = df[funcStatistics[0]]/df[funcStatistics[1]] * 100

        # Correct GEO_ID field in census blocks.  County and block groups require the same editing
        # but other geographies may be different in the future
        if table['geography'] in ["block group", "county", "tract"]:
            df['GEO_ID'] = df['GEO_ID'].str.slice(start=9)


        return df

    except Exception as e:
        print("Error creating DataFrame\n--")
        print(e)
        print("\n==========\n")
        return None


def download_tables(table):
    print(f"Downloading {table['name']}")

    name = table['name']
    data = table['data']
    geography = table['geography']
    
    # Create URL
    URL = build_url(table, data, geography)

    # Get data from URL
    data = get_data(URL)
    if data is None:
        raise Exception('No data')

    # Create DataFrame
    df = create_dataframe(table, data)
    if df is None:
        raise Exception('Data is None')

    # Save CSV
    try:
        df.to_csv(f"{output_dir}\\{name}.csv",index=False)

    except Exception as e:
        print("Error creating CSV\n--")
        print(e)
        print("\n==========\n")
        return
        
    print("\n==========\n")


def create_features(table):
    print(f"Creating {table['name']} in output.gdb")
    name = table['name']
    alias = table['alias']
    data = table['data']
    geography = table['geography']

    # Create copy of input features (census blocks, county, etc)
    print("    Creating new feature class")
    if geography == "county":
        inputFeatures = f"{inputGDB}\\{censusCounties}"
    elif geography == "tract":
        inputFeatures = f"{inputGDB}\\{censusTracts}"
    else:
        inputFeatures = f"{inputGDB}\\{censusBlockGroups}"
    
    arcpy.FeatureClassToFeatureClass_conversion(inputFeatures, arcpy.env.workspace, name)


    # Create required fields in new feature class
    print("    Creating Fields")
    fieldList = ["GEO_ID"] # Create a list of field names at the same time


    def add_field(fieldName, fieldAlias):
        arcpy.AddField_management(name, fieldName, "LONG", field_alias=fieldAlias)
        fieldList.append(fieldName)
        print(f"        {fieldName} - {fieldAlias}")


    # Add fields from main data section in StatsDict.py
    for field in data.keys():
        fieldName = field
        fieldAlias = data[field]
        add_field(fieldName, fieldAlias)

    # Add calculated fields from functions section in StatsDict.py
    if table['functions'] is not None:
        for field in table['functions']:
            fieldName = field['name']
            fieldAlias = field['alias']
            add_field(fieldName, fieldAlias)


    # Change GEOID field to GEO_ID to match ACS data
    arcpy.AlterField_management(name, "GEOID", "GEO_ID")


    # Open CSV data
    print("   Opening new feature data")
    arcpy.MakeTableView_management(f"{output_dir}\\{name}.csv", "csvData")

    fieldValues = {}
    with arcpy.da.SearchCursor("csvData", fieldList) as cur:
        for row in cur:
            GEO_ID = int(row[0])
            fieldValues[GEO_ID] = row[1:]


    # Add new data to new feature class
    print(name)
    fields = [field.name for field in arcpy.ListFields(name)]
    with arcpy.da.UpdateCursor(name, fieldList) as cur:
        for row in cur:
            GEO_ID = int(row[0])
            if GEO_ID in fieldValues.keys():
                values = fieldValues[GEO_ID]
                row[1:] = values
                cur.updateRow(row)






if __name__ == "__main__":
    print("\nDownloading Tables")
    print("\n==========\n")
    for table in ACS_Tables:
        download_tables(table)

    print("Creating GDB Features")
    print("\n==========\n")
    arcpy.env.overwriteOutput = True
    outputGDBPath = f"{output_dir}\\output.gdb"
    if not os.path.exists(outputGDBPath):
        print('    Creating output.gdb')
        arcpy.CreateFileGDB_management(output_dir,'output.gdb')

    arcpy.env.workspace = outputGDBPath

    for table in ACS_Tables:
        create_features(table)