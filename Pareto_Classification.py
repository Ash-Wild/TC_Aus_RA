import pandas as pd
import numpy as np


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


# change the directory and variable names here
dir=r"C:\Users\ashle\Downloads\vulnerability_messy (1).xlsx - Total.csv"
# same as column headers from CSV
indicators=['IRSD_Decile_Aus_0to1','decile_0vehiclepercent','decile_65percentpop']
df = pd.read_csv(dir)
LGA_Data=[]
for i in range(len(df['Region'])):
    info=[i]
    for indicator in indicators:
        info.append(df[indicator][i])
    LGA_Data.append(info)

#call the function to classify LGAs
categories = pareto_classification(LGA_Data)

#save it into dataframe
CategoriesNr = len(categories)
counter = 0
ranks=np.zeros(len(df['Region']))
NumLGAsInCategory=[]
for LGAs_grp in categories:
    rank_value = 1 - counter/CategoriesNr
    for LGA in LGAs_grp:
        ranks[LGA[0]]= rank_value
    NumLGAsInCategory.append(len(LGAs_grp))
    counter += 1
df['Pareto_Rank']=ranks
df.to_csv(dir)
print(NumLGAsInCategory)
#
# def simple_cull(inputPoints):
#     paretoPoints = set()
#     candidateRowNr = 0
#     counter = 0
#     pareto_locations=[]
#     dominatedPoints = set()
#     while True:
#         candidateRow = inputPoints[candidateRowNr]
#         inputPoints.remove(candidateRow)
#         rowNr = 0
#         nonDominated = True
#         while len(inputPoints) != 0 and rowNr < len(inputPoints):
#             row = inputPoints[rowNr]
#             if dominates(candidateRow, row):
#                 # If it is worse on all features remove the row from the array
#                 inputPoints.remove(row)
#                 dominatedPoints.add(tuple(row))
#             elif dominates(row, candidateRow):
#                 nonDominated = False
#                 dominatedPoints.add(tuple(candidateRow))
#                 rowNr += 1
#             else:
#                 rowNr += 1
#
#         if nonDominated:
#             # add the non-dominated point to the Pareto frontier
#             paretoPoints.add(tuple(candidateRow))
#             pareto_locations.append(counter)
#
#         if len(inputPoints) == 0:
#             break
#
#         counter += 1
#     return paretoPoints, dominatedPoints, pareto_locations