# creates risk layers on map
# still needs have some columns relabelled afterwards (expo and vuln instead of avgrank, paretorank)

method = "Decile"
hazards = ["surge","flood","wind","landslides"]
for hazard in hazards:
    layer_name = hazard + "risk"
    if hazard == "surge":
        column_name = "T_100"
    elif hazard == "wind":
        column_name = "MEAN"
    else:
        column_name = "SUM"

    arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_2016_AUST_ProjWGS_1984",layer_name)
# join specific columns from exposure and vulnerability csvs (change later to the shapefile??)
    arcpy.management.JoinField(layer_name,"LGA_NAME16",r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\data spreadsheets\\exposure_index.csv", "Region",["Average_Rank"+method])
    arcpy.management.JoinField(layer_name,"LGA_NAME16",r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\data spreadsheets\\vulnerability_index.csv", "Region",["Pareto_Rank"+method])
# join column from hazard feature class - then reclassify and do multiplication between the three
    arcpy.management.JoinField(layer_name,"LGA_NAME16",r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\Sem2_indicators.gdb\\"+hazard+"_join", "LGA_NAME16", [column_name])
# try with different classing methods here (nat breaks, quantile etc)
    arcpy.management.ReclassifyField(layer_name,column_name,"QUANTILE",10,None,"",None,None,"reclassed_"+hazard)
    arcpy.management.CalculateField(layer_name, hazard+"_0to1", "(!reclassed_"+hazard+"!-1)/10", "PYTHON3", '', "DOUBLE")
    arcpy.management.CalculateField(layer_name, hazard+"_risk", "(!"+hazard+"_0to1! * !Average_Rank"+method+"! * !Pareto_Rank"+method+"!)", "PYTHON3", '', "DOUBLE")

    show_column = hazard + "_risk"
    inputLayer = layer_name
    symbologyLayer = r'C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\layers\symbology_model_risk.lyrx'
    symbologyFields = [["VALUE_FIELD","AREASQKM16",show_column]]
    arcpy.management.ApplySymbologyFromLayer(inputLayer,symbologyLayer,symbologyFields)


# at end, create total TC_Risk layer

arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_2016_AUST_ProjWGS_1984",'TC_Risk')
arcpy.management.JoinField('TC_Risk', 'LGA_NAME16', 'windrisk', 'LGA_NAME16',['wind_0to1','wind_risk'])
arcpy.management.JoinField('TC_Risk', 'LGA_NAME16', 'floodrisk', 'LGA_NAME16',['flood_0to1','flood_risk'])
arcpy.management.JoinField('TC_Risk', 'LGA_NAME16', 'surgerisk', 'LGA_NAME16',['surge_0to1','surge_risk'])
arcpy.management.JoinField('TC_Risk', 'LGA_NAME16', 'landslidesrisk', 'LGA_NAME16',['landslides_0to1','landslides_risk'])
arcpy.management.AddField("TC_Risk", "tc_risk", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.CalculateField("TC_Risk", "tc_risk", "(!wind_risk!+!flood_risk!+!surge_risk!+!landslides_risk!)/4", "PYTHON3", '', "TEXT")

symbologyLayer = r'C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\layers\symbology_model_risk.lyrx'
symbologyFields = [["VALUE_FIELD","AREASQKM16","tc_risk"]]
arcpy.management.ApplySymbologyFromLayer("TC_Risk",symbologyLayer,symbologyFields)
