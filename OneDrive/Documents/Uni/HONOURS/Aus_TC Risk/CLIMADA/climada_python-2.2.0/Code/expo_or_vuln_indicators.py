# creates indicator layers for map
# run these lines of code in ArcGIS Pro python window

#choose index (Expo or Vuln)
index_name = "Vuln"
# choose csv file name (exposure_index or vulnerability_index)
sheet_name = "vulnerability_index"
file_name = sheet_name + ".csv"
joined_column_name = sheet_name + "_csv_"

# choose processing method (Decile or Nat_Breaks)
method = "_Decile"
#method = "_Nat_Breaks"


# make list of indicators (from csv columns) for for loop
indicatorList = ["IRSD", "Age", "Vehicle"]
#indicatorList = ["PopulationDensity", "HospitalDensity", "SubstationDensity","PowerlineDensity"]

for indicator in indicatorList:
    
    indicator_name = indicator
    #choose to show decile or nat breaks processing method
    show_column = indicator_name + method
    # change excel file name here
    layer_name = index_name + "_" + indicator_name

    arcpy.management.MakeFeatureLayer(r"C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\Sem2_indicators.gdb\LGA_2016_AUST_ProjWGS_1984",layer_name)
    arcpy.management.AddJoin(layer_name, "LGA_NAME16", r"C:\\Users\\camy_\\Documents\\ArcGIS\\Projects\\Sem2_indicators\\data spreadsheets\\"+ file_name, "Region", "KEEP_ALL")
    arcpy.management.CopyFeatures(layer_name,layer_name+"1")
    arcpy.management.DeleteField(layer_name+"1", [joined_column_name +'Region',joined_column_name +'_csv_State',joined_column_name +'_csv_LGA_area_sqkm'])
    arcpy.management.Delete(layer_name)
    inputLayer = layer_name+"1"
    symbologyLayer = r'C:\Users\camy_\Documents\ArcGIS\Projects\Sem2_indicators\layers\symbology_model_'+index_name+'.lyrx'
    symbologyFields = [["VALUE_FIELD","AREASQKM16",joined_column_name + show_column]]
    arcpy.management.ApplySymbologyFromLayer(inputLayer,symbologyLayer,symbologyFields)

