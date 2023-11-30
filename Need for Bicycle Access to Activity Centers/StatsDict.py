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
                "operation": sum or percent
                "statistics": [for sum: list of statistics to apply operation to] or [for percent: part, whole],
            }
        ]
    }
"""


ACS_Tables = [
    {
        "name": "Means_Of_Transportation",
        "alias": "Population by Age",
        "geography": "county",
        "fullTable": None,
        "data": {
            "B08534_001E": "Total Commuters",
            "B08534_101E": "Walked",
            "B08534_102E": "Walked (Less than 10 minutes)",
            "B08534_103E": "Walked (10 to 14 minutes)",
            "B08534_104E": "Walked (15 to 19 minutes)",
            "B08534_105E": "Walked (20 to 24 minutes)",
            "B08534_106E": "Walked (25 to 29 minutes)",
            "B08534_107E": "Walked (30 to 34 minutes)",
            "B08534_108E": "Walked (35 to 44 minutes)",
            "B08534_109E": "Walked (45 to 59 minutes)",
            "B08534_110E": "Walked (60 or more minutes)"
        },
        "functions": []
    },
]