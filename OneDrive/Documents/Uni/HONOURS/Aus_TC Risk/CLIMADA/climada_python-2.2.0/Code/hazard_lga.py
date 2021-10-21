# creates hazard layers for map
# run code in ArcGIS Pro python window

# 31st Aug 2021
# should add raw hazard data from local folder, do necessary adjustments
# should end up with final hazard layers
# updated wind hazard to use better dataset (GA)

# 22 Sept 2021 - added landslides and used zonal stats for no avging errors
# landslides done partially manually so code here may not work from scratch

arcpy.management.MakeRasterLayer("C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\Hazard\\Hazard_AUS__100.grd\\Band_1","flood_raw_imported")
#arcpy.management.MakeRasterLayer("C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\Hazard\\Cyclonic_wind_RT100years.grd\\Band_1","wind_raw_imported")
arcpy.management.MakeRasterLayer("C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\Hazard\\GA_wind\\hazard_kmhr.gdb\\R100\\Band_1","wind_raw_imported")
arcpy.management.MakeFeatureLayer("C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\Hazard\\Storm_Surge_hazard_results.shp","surge_raw_imported")

# spatial join (mean surge - within 1km radius) (surge basically done for now)
arcpy.analysis.SpatialJoin("LGA_2016_AUST_ProjWGS_1984", "surge_raw_imported", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\surge_join", "JOIN_ONE_TO_ONE", "KEEP_ALL", 'LGA_CODE16 "LGA_CODE16" true true false 5 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_CODE16,0,5;LGA_NAME16 "LGA_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,LGA_NAME16,0,50;STE_CODE16 "STE_CODE16" true true false 1 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_CODE16,0,1;STE_NAME16 "STE_NAME16" true true false 50 Text 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,STE_NAME16,0,50;AREASQKM16 "AREASQKM16" true true false 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,AREASQKM16,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,LGA_2016_AUST_ProjWGS_1984,Shape_Area,-1,-1;LON "LON" true true false 19 Double 0 0,First,#,surge_raw_imported,LON,-1,-1;LAT "LAT" true true false 19 Double 0 0,First,#,surge_raw_imported,LAT,-1,-1;T_100 "T_100" true true false 19 Double 0 0,Mean,#,surge_raw_imported,T_100,-1,-1', "INTERSECT", "1 Kilometers", '')


# create new raster that has weighted flood with wind 
#output_raster = arcpy.ia.RasterCalculator(' "flood_raw_imported" * "wind_raw_imported"')
#output_raster.save(r"c:\Users\camy_\documents\ArcGIS\Projects\sem2_indicators\sem2_indicators.gdb\flood_weighted")
output_raster = arcpy.ia.RasterCalculator(["flood_raw_imported","wind_raw_imported"],["x","y"],"x*y"); output_raster.save(r"c:\Users\camy_\documents\ArcGIS\Projects\sem2_indicators\sem2_indicators.gdb\flood_weighted")

# landslides (i think you need to add landslides and GA wind raster layers to current map first)
# landslides clip first (raster is global)
arcpy.management.Clip("Int_landslides", "109.439366657039 -46.1968244136877 158.503009323558 -7.87347855648194", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\Int_landslides_Clip1", "aus_coral_boundary_for_clip", "255", "NONE", "NO_MAINTAIN_EXTENT")
#output_raster = arcpy.ia.RasterCalculator(' "Int_landslides_Clip1"* "R100_Band_1"'); output_raster.save(r"c:\Users\camy_\documents\ArcGIS\Projects\sem2_indicators\sem2_indicators.gdb\landslides_x_wind")
# instead, reclassify landslide = 1 values to 0 so that wind doesn't play such a big part...
arcpy.ddd.Reclassify("Int_landslides_Clip1", "Value", "1 0;2 2;3 3;4 4", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\Int_landslides_Clip1_with0", "DATA")
output_raster = arcpy.ia.RasterCalculator(' "Int_landslides_Clip1_with0"* "R100_Band_1"'); output_raster.save(r"c:\Users\camy_\documents\ArcGIS\Projects\sem2_indicators\sem2_indicators.gdb\landslides_x_wind_0")

# use int to prep rasters for polygon conversion (not for polygon conversion anymore, but creates new layer for us)
arcpy.ddd.Int("flood_weighted", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\Int_flood")
arcpy.ddd.Int("wind_raw_imported", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\Int_wind")
arcpy.ddd.Int("landslides_x_wind_0", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\landslides_x_wind_int")

# zonal stat table
arcpy.ia.ZonalStatisticsAsTable("LGA_2016_AUST_ProjWGS_1984", "LGA_NAME16", "landslides_x_wind_int", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\landslides_x_wind_zonalmean_table", "DATA", "ALL", "CURRENT_SLICE", 90, "AUTO_DETECT")
arcpy.ia.ZonalStatisticsAsTable("LGA_2016_AUST_ProjWGS_1984", "LGA_NAME16", "Int_flood", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\flood_zonal", "DATA", "ALL", "CURRENT_SLICE", 90, "AUTO_DETECT")
arcpy.ia.ZonalStatisticsAsTable("LGA_2016_AUST_ProjWGS_1984", "LGA_NAME16", "Int_wind", r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\wind_zonal", "DATA", "ALL", "CURRENT_SLICE", 90, "AUTO_DETECT")

# make layer and name it to the hazard
arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_base_new",'landslides_join')
arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_base_new",'flood_join')
arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_base_new",'wind_join')

# join field from zonal stats table
arcpy.management.JoinField("landslides_join", "LGA_NAME16", "landslides_x_wind_zonalmean_table", "LGA_NAME16", "MEAN;SUM")
arcpy.management.JoinField("flood_join", "LGA_NAME16", "flood_zonal", "LGA_NAME16", "SUM")
arcpy.management.JoinField("wind_join", "LGA_NAME16", "wind_zonal", "LGA_NAME16", "MEAN")

# convert from null to 0
hazLayers=["surge_join","wind_join","flood_join","landslides_join"]
hazColumn=["T_100","MEAN","SUM","SUM"]
for i,j in zip(hazLayers,hazColumn):
    arcpy.management.CalculateField(i,j, "Reclass(!"+j+"!)", "PYTHON3", """# Reclassify values to another value
    # More calculator examples at esriurl.com/CalculatorExamples
def Reclass(arg):
    if arg is None:
        return 0
    return arg""", "TEXT")

# apply symbology according to 'symbology_model_hazard.lyrx' file in 'layers' folder - and select shown field
arcpy.management.ApplySymbologyFromLayer('flood_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","SUM"]])
arcpy.management.ApplySymbologyFromLayer('wind_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","MEAN"]])
arcpy.management.ApplySymbologyFromLayer('surge_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","T_100"]])
arcpy.management.ApplySymbologyFromLayer('landslides_join',"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\layers\\symbology_model_hazard.lyrx",[["VALUE_FIELD","gridcode","SUM"]])


