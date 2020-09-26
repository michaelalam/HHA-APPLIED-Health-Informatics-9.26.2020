# Data Preprocessing Tools

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
from scipy.stats import norm



# Importing the dataset
# NOTE - you will need to update this part below to reflect the location of where you saved this file

    
dataset = pd.read_csv("https://raw.githubusercontent.com/hantsw/statistics/master/data_meds_ph.csv")




# Create a sub-sample of the dataset since it is large / random selection of 20 rows
temp = dataset.sample(20)
temp = dataset.sample(20)
# Michael after trying temp = dataset.sample (20) gave no results, I used dataset.sample (20) instead as a fix.
dataset.sample(20)

# Preview the set, see how it looks 
temp 

# Looks like there is a erraneous column 1 - lets remove 
dataset = dataset.drop(columns=['Unnamed: 0'])
dataset = dataset.drop(columns=['Unamed: 0'])
# Now confirm that it is gone: 
list(dataset)

# Update are working temp dataset
temp = dataset.sample(20)
dataset.sample(20) # this had been adjusted instead of the previous version to get it to run properly.

# Lets now look and see what additional cleaning should happen, first up is some date columns
# Lets transform the date columns to actual dates
# First lets see what the column names are 
list(temp)

# Appears they are 'created' and 'date_expired'
# So lets transform those to actual date/times
dataset['created'] = pd.to_datetime(dataset['created'])

# Now to confirm, lets update our temp dataset, and then order that column from 
# earliest to latest dates 
temp = dataset.sample(20)
temp = temp.sort_values(by=['created'])
#adjusted by Michael Lam
dataset.sample(20)
dataset.sort_values(by=['created'])

# Great! Looks like it worked - now lets do that for the other date column 
dataset['date_expired'] = pd.to_datetime(dataset['date_expired'])

# Lets just confirm and double check here as well: 
temp = dataset.sample(20)
temp = temp.sort_values(by=['date_expired'])
#Adjusted by Michael Lam
dataset.sample(20)
dataset.sort_values(by=['date_expired'])

# Lets now go back and see what other data cleaning might be warranted: 
temp 

# It appears 'name' represents drug name, lets rename the column so it is more clear
dataset = dataset.rename(columns = {'name': 'drug_name'}, inplace = False)

# lets confirm the change has happened: 
temp = dataset.sample(20)
temp
#adjustments 
dataset.sample(20)
dataset

# great! looks better 


# Lets now also do the same for 'roa' which stands for route_of_administration 
dataset = dataset.rename(columns = {'roa': 'route_of_admin'}, inplace = False)






# for 'frequency' column, it looks like there is the medical abbreviation, 
# and then there is the actual human-readable form - lets make this one column 
# two columns - one with the abbreviation, and a seperate one with the full description 
# in the first line below, we make sure that the column is a string 
# in the second line below, we then see that the abbreviation and seperated by some white space, 
# so in our code, we first give the names of the two new columns that we want to create, which is 
# "frequency_abbreviation" and "frequency_readible", then we SPLIT the columns by the white space, 
# which is designated by " " 
dataset["frequency"] = dataset["frequency"].astype(str)
dataset[["frequency_abbreviation", "frequency_readible"]]= dataset["frequency"].str.split(" ", n = 1, expand = True) 





# lets now confirm that this has worked 
temp = dataset.sample(20)
temp
##Michael Lam Adjusted 
dataset.sample(20)
dataset

# great! now in addition, looks like we should remove our old 'frequency' column since that is no 
# longer needed, and lets remove the ( ) from our last new variable that we created, 'frequency_readible'

dataset = dataset.drop(columns=['frequency'])
dataset['frequency_readible']= dataset['frequency_readible'].str.replace('(', '')
dataset['frequency_readible']= dataset['frequency_readible'].str.replace(')', '')

# now lets confirm...
temp = dataset.sample(20)
temp
##Michael Lam Adjusted
dataset.sample(20)
# great! looks better 


# lets clean up the drug details column - this right now is in the structure of a DICTIONARY, but it is a string 
# first, lets convert the string to a dictionary, and then get some of the nested information out 

drug_details = dataset.drug_details.apply(eval)

# lets confirmed it worked , but getting the first medispan ID value
# if you do not know what MEDISPAN is, look it up! 
drug_details[0]['medispan_id']

# alright looks good! 

# now lets just get the columns we want - medispan ID, NDC number, and product name
# and create this as a new dataframe!
drug_details_pd = pd.DataFrame(drug_details.tolist(), columns=['medispan_id', 'ndcndf_id', 'product_name'])

# because we have the same amount of rows in our new drug_details_pd as our original dataset, 
# lets just now merge the two dataframes together into a new DF called clean_df
clean_df = dataset.merge(drug_details_pd, how='left', left_index=True, right_index=True)






# Now, lets get an understanding of our missing data
df_missing = pd.DataFrame(clean_df.isnull().sum()) #this is taken from our EDA_Common_Code_CheatSheet.py file 
df_missing = df_missing.reset_index() #this resets the index, so our index now becomes a column variable that we can filter by 

# Lets now see how many unique patients we have in this DF 
clean_df.UUID.nunique()

# Lets find how the average number of TOTAL medications for each patient 
counts = clean_df.groupby(['UUID']).size().reset_index(name='total_med_counts') #this is grouping each row by UID - 
counts.total_med_counts.mean()

# Lets find out the frequency counts for 'added_by' --> each number represents a unique physician 
added_by_counts = pd.DataFrame(clean_df.addedby.value_counts())
added_by_counts = added_by_counts.reset_index()


# Lets find out what the most commonly prescribed medication is by 'product_name'
common_meds = pd.DataFrame(clean_df['product_name'].value_counts())
common_meds = common_meds.reset_index()

# Lets now find out which medications have the highest re-fill rate 
refilled = pd.DataFrame(clean_df.groupby(['refills_rxed','product_name']).size())
refilled = refilled.reset_index()

# Lets now find out which medications are the most prescribed by doses_rxed column
doses = pd.DataFrame(clean_df.groupby(['doses_rxed','product_name']).size())
doses = doses.reset_index()

# Lets now find out what the most common route of administration is 
roa = pd.DataFrame(clean_df['route_of_admin'].value_counts())
roa = roa.reset_index()
# looks like there might be some repeat values in ROA, lets take care of that later 


# Lets now look at some visualizations and means to understand if our continuous data is NORMAL 
# the only varialbes that are continuous that we are interested in here are doses_rxed and refills_rxed

# lets first get the mean, median, and mode + quartiles for doses_rxed
# we first need to make sure the column is not a string, but a integer 
clean_df['doses_rxed'] = pd.to_numeric(clean_df['doses_rxed'], errors='coerce')
doses_rxed_table = pd.DataFrame(clean_df.doses_rxed.describe())

# lets first get the mean, median, and mode + quartiles for refills_rxed
# we first need to make sure the column is not a string, but a integer 
clean_df['refills_rxed'] = pd.to_numeric(clean_df['refills_rxed'], errors='coerce')
refills_rxed_table = pd.DataFrame(clean_df.refills_rxed.describe())

# lets now do a box plot for doses_rxed 
ax = sns.boxplot(x=clean_df["doses_rxed"])

# lets now do a box plot for refills_rxed
ax = sns.boxplot(x=clean_df["refills_rxed"])

# lets now create a histogram of doses_rxed 
sns.distplot(clean_df['doses_rxed'], fit=norm)

# lets now create a histogram of doses_rxed 
sns.distplot(clean_df['refills_rxed'], fit=norm)

df.shape

