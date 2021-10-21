# coding: utf-8
# 31st Aug 2021
# should add raw hazard data from local folder, do necessary adjustments
# should end up with final hazard layers

import arcpy
from arcpy import env
from arcpy.sa import *

# set your directory to the raw files
env.workspace = r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers"
LGA_file = r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\LGA_2016_AUST_ProjWGS_1984.shp"
#load in the files
flood_raw = arcpy.Raster('Hazard_AUS__100.grd\\Band_1')
wind_raw = arcpy.Raster('Cyclonic_wind_RT100years.grd\\Band_1')

surge_raw = arcpy.mapping.Layer('Storm_Surge_hazard_results.shp')
LGAs = arcpy.mapping.Layer(LGA_file)
# surge_raw = arcpy.PointGeometry(directory+'\\Storm_Surge_hazard_results.shp') # https://gis.stackexchange.com/questions/113799/how-to-read-a-shapefile-in-python

# create new raster that has weighted flood with wind 
flood_weighted = flood_raw * wind_raw

#convert rasters to integer for use in Zonal statistics
flood_int = arcpy.Int(flood_weighted)
wind_int = arcpy.Int(wind_raw)

Flood_LGAs_Table = arcpy.ZonalStatisticsAsTable("LGA_2016_AUST_ProjWGS_1984.shp", 'LGA_NAME16', flood_int, "Flood_LGAs_Table", "NODATA", "MEAN")
Wind_LGAs_Table = arcpy.ZonalStatisticsAsTable("LGA_2016_AUST_ProjWGS_1984.shp", 'LGA_NAME16', wind_int, "Wind_LGAs_Table", "NODATA", "MEAN")

# spatial join (mean surge - within 1km radius)
Surge_LGAs = arcpy.analysis.SpatialJoin("LGA_2016_AUST_ProjWGS_1984.shp", surge_raw, "Surge_LGAs", "JOIN_ONE_TO_ONE", "KEEP_ALL", 'LGA_CODE16 "LGA_CODE16" true true false 5 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_CODE16,0,5;LGA_NAME16 "LGA_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_NAME16,0,50;STE_CODE16 "STE_CODE16" true true false 1 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_CODE16,0,1;STE_NAME16 "STE_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_NAME16,0,50;AREASQKM16 "AREASQKM16" true true false 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,AREASQKM16,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Area,-1,-1;LON "LON" true true false 19 Double 0 0,First,#,surge_raw_imported,LON,-1,-1;LAT "LAT" true true false 19 Double 0 0,First,#,surge_raw_imported,LAT,-1,-1;T_100 "T_100" true true false 19 Double 0 0,Mean,#,surge_raw_imported,T_100,-1,-1', "INTERSECT", "1 Kilometers", '')


# convert raster to polygon
arcpy.conversion.RasterToPolygon("Int_flood", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\flood_poly", "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
arcpy.conversion.RasterToPolygon("Int_wind", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\wind_poly", "NO_SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)

# spatial join (sum flood, mean wind)
arcpy.analysis.SpatialJoin("LGA_2016_AUST_ProjWGS_1984", "flood_poly", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\flood_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", 'LGA_CODE16 "LGA_CODE16" true true false 5 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_CODE16,0,5;LGA_NAME16 "LGA_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_NAME16,0,50;STE_CODE16 "STE_CODE16" true true false 1 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_CODE16,0,1;STE_NAME16 "STE_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_NAME16,0,50;AREASQKM16 "AREASQKM16" true true false 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,AREASQKM16,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Area,-1,-1;Id "Id" true true false 4 Long 0 0,First,#,flood_poly,Id,-1,-1;gridcode "gridcode" true true false 4 Long 0 0,Sum,#,flood_poly,gridcode,-1,-1;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,flood_poly,Shape_Length,-1,-1;Shape_Area_1 "Shape_Area" false true true 8 Double 0 0,First,#,flood_poly,Shape_Area,-1,-1', "INTERSECT", None, '')
arcpy.analysis.SpatialJoin("LGA_2016_AUST_ProjWGS_1984", "wind_poly", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\wind_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", 'LGA_CODE16 "LGA_CODE16" true true false 5 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_CODE16,0,5;LGA_NAME16 "LGA_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_NAME16,0,50;STE_CODE16 "STE_CODE16" true true false 1 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_CODE16,0,1;STE_NAME16 "STE_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_NAME16,0,50;AREASQKM16 "AREASQKM16" true true false 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,AREASQKM16,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Area,-1,-1;Id "Id" true true false 4 Long 0 0,First,#,wind_poly,Id,-1,-1;gridcode "gridcode" true true false 4 Long 0 0,Mean,#,wind_poly,gridcode,-1,-1;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,wind_poly,Shape_Length,-1,-1;Shape_Area_1 "Shape_Area" false true true 8 Double 0 0,First,#,wind_poly,Shape_Area,-1,-1', "INTERSECT", None, '')

# spatial join (mean surge - within 1km radius)
arcpy.analysis.SpatialJoin("LGA_2016_AUST_ProjWGS_1984", "surge_raw_imported", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\surge_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", 'LGA_CODE16 "LGA_CODE16" true true false 5 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_CODE16,0,5;LGA_NAME16 "LGA_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_NAME16,0,50;STE_CODE16 "STE_CODE16" true true false 1 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_CODE16,0,1;STE_NAME16 "STE_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_NAME16,0,50;AREASQKM16 "AREASQKM16" true true false 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,AREASQKM16,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Area,-1,-1;LON "LON" true true false 19 Double 0 0,First,#,surge_raw_imported,LON,-1,-1;LAT "LAT" true true false 19 Double 0 0,First,#,surge_raw_imported,LAT,-1,-1;T_100 "T_100" true true false 19 Double 0 0,Mean,#,surge_raw_imported,T_100,-1,-1', "INTERSECT", "1 Kilometers", '')

# apply symbology according to 'symbology_model_hazard.lyrx' file in 'layers' folder - and select shown field
arcpy.management.ApplySymbologyFromLayer('flood_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","gridcode"]])
arcpy.management.ApplySymbologyFromLayer('wind_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","gridcode"]])

# reclassify null values in surge's T_100 column to 0 before applying symbology
arcpy.management.CalculateField("surge_join", "T_100", "Reclass(!T_100!)", "PYTHON3", """# Reclassify values to another value
# More calculator examples at esriurl.com/CalculatorExamples
def Reclass(arg):
    if arg is None:
        return 0
    return arg""", "TEXT")

arcpy.management.ApplySymbologyFromLayer('surge_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","T_100"]])
