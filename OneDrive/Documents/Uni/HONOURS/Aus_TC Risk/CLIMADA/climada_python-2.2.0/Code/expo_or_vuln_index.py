# creates expo and vuln index layers
# run these lines of code in ArcGIS Pro python window

indexes = ["Expo", "Vuln"]
for index in indexes:
    index_name = index
    method = "Decile"
    if index_name == "Expo":
        indicator_name = "Average_Rank"
        sheet_name = "exposure_index"
    elif index_name == "Vuln":
        indicator_name = "Pareto_Rank"
        sheet_name = "vulnerability_index"
    else:
        print("Something went wrong with index ranking")

    file_name = sheet_name + ".csv"
    joined_column_name = sheet_name + "_csv_"
    show_column = indicator_name + method
    layer_name = index_name + "_index"

#create layer 
    arcpy.management.CopyFeatures(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_2016_AUST_ProjWGS_1984",layer_name)
#join specific columns to new layer
    arcpy.management.JoinField(layer_name,"LGA_NAME16",r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\data spreadsheets\\"+ file_name, "Region",[show_column])
#change symbology to match specified model layer
    inputLayer = layer_name
    symbologyLayer = r'C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\layers\symbology_model_'+index_name+'.lyrx'
    symbologyFields = [["VALUE_FIELD","AREASQKM16",show_column]]
    arcpy.management.ApplySymbologyFromLayer(inputLayer,symbologyLayer,symbologyFields)
