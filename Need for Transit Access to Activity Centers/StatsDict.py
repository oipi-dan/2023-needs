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
        "name": "Transit_Commute_Time",
        "alias": "Transit Commute Time",
        "geography": "county",
        "fullTable": None,
        "tableType": "Detail",
        "data": {
            "B08134_061E": "Estimate!!Total:!!Public transportation (excluding taxicab)",
            "B08134_062E": "LT 10 min",
            "B08134_063E": "10-14 min",
            "B08134_064E": "15-19 min",
            "B08134_065E": "20-24 min",
            "B08134_066E": "25-29 min",
            "B08134_067E": "30-34 min",
            "B08134_068E": "35-44 min",
            "B08134_069E": "45-59 min",
            "B08134_070E": "GT 60 min"
        },
        "functions": []
    }
]