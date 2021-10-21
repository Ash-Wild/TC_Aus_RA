# load master data
import pandas as pd
import jenkspy
import numpy as np


def goodness_of_variance_fit(array, classes):
    # get the break points
    classes = jenkspy.jenks_breaks(array, nb_class=classes)

    # do the actual classification
    classified = np.array([classify(i, classes) for i in array])

    # max value of zones
    maxz = max(classified)

    # nested list of zone indices
    zone_indices = [[idx for idx, val in enumerate(classified) if zone + 1 == val] for zone in range(maxz)]

    # sum of squared deviations from array mean
    sdam = np.sum((array - array.mean()) ** 2)

    # sorted polygon stats
    array_sort = [np.array([array[index] for index in zone]) for zone in zone_indices]

    # sum of squared deviations of class means
    sdcm = sum([np.sum((classified - classified.mean()) ** 2) for classified in array_sort])

    # goodness of variance fit
    gvf = (sdam - sdcm) / sdam

    return gvf, classified

def classify(value, breaks):
    for i in range(1, len(breaks)):
        if value < breaks[i]:
            return i
    return len(breaks) - 1


def make_DecileNatBreaks(CSV_directory, indicators_list):
    dir=CSV_directory
    indicators = indicators_list
    df = pd.read_csv(dir)
    for indicator in indicators:
        array=df[indicator]

        #calculate and save the decile values of the array
        df['Decile' + indicator] = (pd.qcut(array, 10, labels=False) + 1) / 10
        # for IRSD this creates strange value
        if indicator == 'IRSD_Decile_Ausrank':
            df['Decile' + indicator] = array/ 10

        # calculate the natural breaks values
        gvf = 0.0
        nclasses = 5
        threshold = .96
        while gvf < threshold:
            gvf,categories = goodness_of_variance_fit(array, nclasses)
            nclasses += 1
        df['Nat_Breaks'+indicator] = categories/(nclasses-1)
        # eg
        # array =[3.45, 4.05, ...]
        # Raw rank / Categories / classified = [4, 7, ...]

    #df.to_csv(dir,index=False)
    return df

def dominates(row, candidateRow):
    return sum([row[x] >= candidateRow[x] for x in range(1,len(row))]) == len(row)-1

# https://stackoverflow.com/questions/32791911/fast-calculation-of-pareto-front-in-python

def simple_cull(inputPoints):
    paretoPoints = set()
    candidateRowNr = 0
    dominatedPoints = set()
    while True:
        candidateRow = inputPoints[candidateRowNr]
        inputPoints.remove(candidateRow)
        rowNr = 0
        nonDominated = True
        while len(inputPoints) != 0 and rowNr < len(inputPoints):
            row = inputPoints[rowNr]
            if dominates(candidateRow, row):
                # If it is worse on all features remove the row from the array
                inputPoints.remove(row)
                dominatedPoints.add(tuple(row))
            elif dominates(row, candidateRow):
                nonDominated = False
                dominatedPoints.add(tuple(candidateRow))
                rowNr += 1
            else:
                rowNr += 1

        if nonDominated:
            # add the non-dominated point to the Pareto frontier
            paretoPoints.add(tuple(candidateRow))

        if len(inputPoints) == 0:
            break
    return paretoPoints, dominatedPoints
#
def Pareto_Ranking(dataframe, indicators,stat):
    df = dataframe
    LGA_Data = []
    for i in range(len(df['Region'])):
        info = [i]
        for indicator in indicators:
            info.append(df[stat+indicator][i])
        LGA_Data.append(info)

    # call the function to classify LGAs
    categories = pareto_classification(LGA_Data)

    # save it into dataframe
    CategoriesNr = len(categories)
    counter = 0
    ranks = np.zeros(len(df['Region']))
    NumLGAsInCategory = []
    for LGAs_grp in categories:
        rank_value = 1 - counter / CategoriesNr
        for LGA in LGAs_grp:
            ranks[LGA[0]] = rank_value
        NumLGAsInCategory.append(len(LGAs_grp))
        counter += 1
    df['Pareto_Rank'+stat] = ranks
    return df

def pareto_classification(LGA_Data):
    # Input: List with list of n number of variables
    categories=[]
    locations=[]
    while len(LGA_Data) != 0:
        paretoPoints, dominatedPoints = simple_cull(LGA_Data)
        categories.append(list(paretoPoints))
        LGA_Data = list(dominatedPoints)
    #print(categories)
    return categories



def Equal_Ranking(dataframe, indicators,stat):
    df=dataframe
    df['Average_Rank' + stat] = np.zeros(len(df['Region']))
    for i in range(len(df['Region'])):
        info=[]
        for indicator in indicators:
            info.append(df[stat+indicator][i])
        df['Average_Rank' + stat][i] = np.mean(info)
    return df

def Multiplicative_Ranking(dataframe, indicators,stat):
    df = dataframe
    df['Mult_Rank' + stat] = np.zeros(len(df['Region']))

    for i in range(len(df['Region'])):
        counter=1
        for indicator in indicators:
            counter = counter * df[stat + indicator][i]
            # eg. 1x4 -> 4x5 -> 20x3. = 4x5x3 or 1 x a, a x b, ab x c = abc
        df['Mult_Rank' + stat][i] = counter
    return df

def classify_risk(CSV_directory, indicators_list):
    df = make_DecileNatBreaks(CSV_directory, indicators_list)

    df = Pareto_Ranking(df, indicators_list, 'Decile')
    df = Pareto_Ranking(df, indicators_list, 'Nat_Breaks')

    df = Equal_Ranking(df, indicators_list, 'Decile')
    df = Equal_Ranking(df, indicators_list, 'Nat_Breaks')

    df = Multiplicative_Ranking(df, indicators_list, 'Decile')
    df = Multiplicative_Ranking(df, indicators_list, 'Nat_Breaks')
    df.to_csv(dir, index=False)

# add in the directory to CSV of entire data
dir=r"C:\Users\ashle\Downloads\exposure_messy.xlsx - Total (1).csv"
# same as column headers from CSV
indicators=['p_density (p/km2)','density_hospital','density_substations','density_powerlinelength']

#classify_risk(dir, indicators)

###
# Hazard layer creation
import rasterio
from rasterio.plot import show
from rasterstats import zonal_stats
import geopandas as gpd

directory = r"C:\Users\ashle\OneDrive\Documents\Uni\HONOURS\Aus_TC Risk\python"
Hazards_folder = "\hazard_layers"
#load in the files
flood_raw = rasterio.read(Hazards_folder+'\Hazard_AUS__100.grd\Band_1')
wind_raw = rasterio.read(Hazards_folder+'\Cyclonic_wind_RT100years.grd\Band_1')
surge_raw = gpd.read_file(Hazards_folder+ '\Storm_Surge_hazard_results.shp')
LGAs = gpd.read_file(Hazards_folder+ '\LGA_2016_AUST_ProjWGS_1984.shp')

# create new raster that has weighted flood with wind
assert flood_raw.crs.data == wind_raw.crs.data
flood_weighted = flood_raw * wind_raw # not sure if works

#convert rasters to integer for use in Zonal statistics
flood_int = flood_weighted.astype(int)
wind_int = wind_raw.astype(int)

# reproject to the same CRS
LGAs_reprojected = LGAs.to_crs(flood_int.crd.data)
surge_reprojected = surge_raw.to_crs(flood_int.crd.data)

# plotting wind and LGAs
ax = show((wind_int, 1))
LGAs_reprojected.plot(ax=ax, facecolor='None', edgecolor='red', linewidth=2)

# calculate zonal stats, so each hazard now fits to LGAs
# https://automating-gis-processes.github.io/CSC18/lessons/L6/zonal-statistics.html
# https://pythonhosted.org/rasterstats/manual.html#zonal-statistics
Wind_array = wind_int.read(1)
affine = wind_int.affine
zs_Wind = zonal_stats(LGAs_reprojected, Wind_array, affine=affine, stats=['mean'])
Flood_array = wind_int.read(1)
affine = flood_int.affine
zs_Flood = zonal_stats(LGAs_reprojected, Flood_array, affine=affine, stats=['mean'])
# think there's some issues, not the same as ArcGIS function. Maybe need to do nearest neighbour for each point
zs_SS = gpd.sjoin(LGAs_reprojected, surge_reprojected, how="inner", op="intersect")
# could save these using .to_file(director)

# combine the hazard layers together to a common dataframe with vuln and exposure
# load in exposure and vuln
vuln_csv = pd.read_csv(directory + 'vuln csv')
exposure_csv = pd.read_csv(directory + 'exposure csv')
df = vuln_csv['Region'] # initialises the dataframe with first column being LGAs from Vulnerability
index_calc = ['Pareto','Average','Mult']
indicator_stats = ['Decile','Nat_Breaks']
for calc in index_calc:
    for stat in indicator_stats:
        df['Vuln' + calc + stat] = vuln_csv[calc + '_Rank' + stat]
        df['Expo' + calc + stat] = exposure_csv[calc + '_Rank' + stat]

# join the dataframe contain Expo+Vuln with the Hazard data
# may need to rename columns of hazard layer so that it matches the Regions
#df = df.merge(zs_Wind.data, on='Regions')
# if  the merge
df = df.merge(zs_Wind.data, on='Region')
df['Wind_means'] = df['Wind_means']

# make decile and nat breaks for hazards
