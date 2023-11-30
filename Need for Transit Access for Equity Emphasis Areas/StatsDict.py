"""
{
        "name": Name of the table in the output csv and gdb,
        "alias": Alias of table in gdb,
        "geography": Geography level of the dataset (eg county, block group)
        "fullTable": If downloading a full table, the name of the table goes here
                     Note that the API allows a maximum of 50 stats, so if we need
                     more than that, we need to download the whole table
        "data": {
            Statistic Name: Statistic alias,
            Statistic Name: Statistic alias,
            Statistic Name: Statistic alias,
            Statistic Name: Statistic alias
        },
        "functions" [ # Additional columns added by performing functions on other columns
            {
                "name": column name,
                "alias": column alias
                "operation": sum, diff, or percent
                "statistics": [for sum and diff: list of statistics to apply operation to] or [for percent: part, whole],
            }
        ]
    }
"""


ACS_Tables = [
    {
        "name": "EEA_Statistics",
        "alias": "EEA Statistics",
        "geography": "block group",
        "fullTable": None,
        "tableType": "Detail",
        "data": {
            "B01003_001E": "Total Population",

            # INCOME TO POVERTY LEVEL
            "C17002_002E": "Income to Poverty Level: Under 0.50",
            "C17002_003E": "Income to Poverty Level: 0.50 to 0.99",
            "C17002_004E": "Income to Poverty Level: 1.00 to 1.24",
            "C17002_005E": "Income to Poverty Level: 1.25 to 1.49",

            # AGE
            "B01001_023E": "Total Male 75 to 79 years",
            "B01001_024E": "Total Male 80 to 84 years",
            "B01001_025E": "Total Male 85 and older",
            "B01001_047E": "Total Female 75 to 79 years",
            "B01001_048E": "Total Female 80 to 84 years",
            "B01001_049E": "Total Female 85 and older",

            # RACE
            "B03002_002E": "Total Not Hispanic or Latino",
            "B03002_003E": "Total Not Hispanic or Latino White alone",
            "B03002_012E": "Total Hispanic or Latino",
            "B03002_013E": "Total Hispanic or Latino White alone",

            # DOES NOT SPEAK ENGLISH WELL
            'B16004_007E': 'Estimate!!Total:!!5 to 17 years:!!Speak Spanish:!!Speak English "not well"',
            'B16004_008E': 'Estimate!!Total:!!5 to 17 years:!!Speak Spanish:!!Speak English "not at all"',
            'B16004_012E': 'Estimate!!Total:!!5 to 17 years:!!Speak other Indo-European languages:!!Speak English "not well"',
            'B16004_013E': 'Estimate!!Total:!!5 to 17 years:!!Speak other Indo-European languages:!!Speak English "not at all"',
            'B16004_017E': 'Estimate!!Total:!!5 to 17 years:!!Speak Asian and Pacific Island languages:!!Speak English "not well"',
            'B16004_018E': 'Estimate!!Total:!!5 to 17 years:!!Speak Asian and Pacific Island languages:!!Speak English "not at all"',
            'B16004_022E': 'Estimate!!Total:!!5 to 17 years:!!Speak other languages:!!Speak English "not well"',
            'B16004_023E': 'Estimate!!Total:!!5 to 17 years:!!Speak other languages:!!Speak English "not at all"',
            'B16004_029E': 'Estimate!!Total:!!18 to 64 years:!!Speak Spanish:!!Speak English "not well"',
            'B16004_030E': 'Estimate!!Total:!!18 to 64 years:!!Speak Spanish:!!Speak English "not at all"',
            'B16004_034E': 'Estimate!!Total:!!18 to 64 years:!!Speak other Indo-European languages:!!Speak English "not well"',
            'B16004_035E': 'Estimate!!Total:!!18 to 64 years:!!Speak other Indo-European languages:!!Speak English "not at all"',
            'B16004_039E': 'Estimate!!Total:!!18 to 64 years:!!Speak Asian and Pacific Island languages:!!Speak English "not well"',
            'B16004_040E': 'Estimate!!Total:!!18 to 64 years:!!Speak Asian and Pacific Island languages:!!Speak English "not at all"',
            'B16004_044E': 'Estimate!!Total:!!18 to 64 years:!!Speak other languages:!!Speak English "not well"',
            'B16004_045E': 'Estimate!!Total:!!18 to 64 years:!!Speak other languages:!!Speak English "not at all"',
            'B16004_051E': 'Estimate!!Total:!!65 years and over:!!Speak Spanish:!!Speak English "not well"',
            'B16004_052E': 'Estimate!!Total:!!65 years and over:!!Speak Spanish:!!Speak English "not at all"',
            'B16004_056E': 'Estimate!!Total:!!65 years and over:!!Speak other Indo-European languages:!!Speak English "not well"',
            'B16004_057E': 'Estimate!!Total:!!65 years and over:!!Speak other Indo-European languages:!!Speak English "not at all"',
            'B16004_061E': 'Estimate!!Total:!!65 years and over:!!Speak Asian and Pacific Island languages:!!Speak English "not well"',
            'B16004_062E': 'Estimate!!Total:!!65 years and over:!!Speak Asian and Pacific Island languages:!!Speak English "not at all"',
            'B16004_066E': 'Estimate!!Total:!!65 years and over:!!Speak other languages:!!Speak English "not well"',
            'B16004_067E': 'Estimate!!Total:!!65 years and over:!!Speak other languages:!!Speak English "not at all"'
        },
        "functions": [
            {
                "name": "poverty_ratio_sum",
                "alias": "residents whose income is below 150% of the poverty level",
                "operation": "sum",
                "statistics": ["C17002_002E", "C17002_003E", "C17002_004E", "C17002_005E"],
            },
            {
                "name": "over_75_sum",
                "alias": "residents over 75",
                "operation": "sum",
                "statistics": ["B01001_023E", "B01001_024E", "B01001_025E", "B01001_047E", "B01001_048E", "B01001_049E"],
            },
            {
                "name": "total_minority_non_hispanic",
                "alias": "total minority non hispanic",
                "operation": "diff",
                "statistics": ["B03002_002E", "B03002_003E"],
            },
            {
                "name": "total_minority_hispanic",
                "alias": "total minority hispanic",
                "operation": "diff",
                "statistics": ["B03002_012E", "B03002_013E"],
            },
            {
                "name": "total_minority",
                "alias": "total minority hispanic",
                "operation": "sum",
                "statistics": ["total_minority_non_hispanic", "total_minority_hispanic"],
            },
            {
                "name": "do_not_speak_english_very_well",
                "alias": "do not speak english very well",
                "operation": "sum",
                "statistics": ['B16004_007E','B16004_008E','B16004_012E','B16004_013E','B16004_017E','B16004_018E','B16004_022E','B16004_023E','B16004_029E','B16004_030E','B16004_034E','B16004_035E','B16004_039E','B16004_040E','B16004_044E','B16004_045E','B16004_051E','B16004_052E','B16004_056E','B16004_057E','B16004_061E','B16004_062E','B16004_066E','B16004_067E']
            },
        ]
    },
    {
        "name": "EEA_Statistics_Disability",
        "alias": "EEA Statistics Disability",
        "geography": "tract",
        "fullTable": None,
        "tableType": "Subject",
        "data": {
            "S0101_C01_001E": "Total Population",
            "S1810_C01_001E": "Total civilian noninstitutionalized population",
            "S1810_C02_001E": "With a disability",
            "S1810_C03_001E": "Percent with a disability"
        },
        "functions": []
    },
]