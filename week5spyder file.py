# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 18:15:09 2020

@author: Michael Lam
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:46:32 2020

@author: hantswilliams

Week 5 Statistics - 

NOTE -> to run this on google colab // will first need to: 
    
    
!sudo apt-get install python3-dev default-libmysqlclient-dev
!pip install pymysql



Reference: https://machinelearningmastery.com/a-gentle-introduction-to-normality-tests-in-python/
Reference: https://machinelearningmastery.com/how-to-use-correlation-to-understand-the-relationship-between-variables/

"""
# Importing the libraries

#Packages for SQL CONNECTION 
from sqlalchemy import create_engine
import sqlalchemy 

#Packages for DATAFRAME 
import pandas as pd

#Packages for STATS 
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import shapiro
from scipy.stats import norm

#Packages for VISUALIZATION 
import seaborn as sns
import plotly.express as px
from plotly.offline import plot
from matplotlib import pyplot
from statsmodels.graphics.gofplots import qqplot





### Lets load our CSV file from GITHUB: 
csvfile = pd.read_csv('https://raw.githubusercontent.com/hantsw/statistics/master/data_meds_ph.csv')

MYSQL_HOSTNAME = 'ahi.c96anxcynoyv.us-east-1.rds.amazonaws.com' # you probably don't need to change this
MYSQL_USER = 'admin'
MYSQL_PASSWORD = '46566656'
MYSQL_DATABASE = 'hospital'

connection_string = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE}'
engine = create_engine(connection_string) ##in order to run tihs we need to install sql alchemy



### Get a list of table names inside of `hospitals` 
print (engine.table_names())

hospital_table_list = engine.table_names()

#### Get a list of databases inside of our mySQL DBMS
insp = sqlalchemy.inspect(engine)
db_list = insp.get_schema_names()
## get_schema names gets us a nice list that we are connected too. Michael NOTES

#### Lets now use SQL alchemy to create a new database just to store things for right now: 
engine.execute("CREATE DATABASE dbname") #create db

#### Lets now use SQL alchemy to delete that new database that we just created
engine.execute("DROP DATABASE dbname")

#### Alright now that we see how that works, lets create a new temp one with proper naming 
engine.execute("CREATE DATABASE stats_temp")



#### NOW - the next big step, since we already have a working dataframe, e.g., that is nammed 
#### "csvfile" - which is 25k rows, 22 columns, thats see if we can move that into a NEW table 
#### that exists within our new database, which is named stats_temp 

### https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html

## Lets now make sure our ENGINE is tied into the proper Database - stats_temp 
MYSQL_DATABASE = 'stats_temp'
connection_string = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE}'
engine = create_engine(connection_string)

### Lets give the name of our table "meds" 
csvfile.to_sql('meds', con=engine, if_exists='append')

### Now, lets run a quick query to see if it actually worked: 
engine.execute("SELECT * FROM meds LIMIT 10").fetchall()
tempdf = pd.read_sql("SELECT * FROM meds LIMIT 10", con=engine)

### How can we understand what the data types are for a individual column? 
### With pd.read_sql, we can insert in any of our SQL commands and return something 
### as a nice table 
print(engine.execute("DESCRIBE meds"))
testtest = pd.read_sql("DESCRIBE meds", con=engine)

### How about converstion our dataframe to JSON ?? 
testtest_json = testtest.to_json(orient="records")


mysql_meds_return = pd.read_sql("select * from meds", con=engine);
mysql_meds_random_sample = mysql_meds_return.sample(10)












#####################
#####################
##
## CDC DATA LOADING INTO SQL - BACK DOWN 
##
#####################
#####################


### READING FROM THE API ---> 
covid19 = pd.read_csv("https://data.cdc.gov/resource/9mfq-cb36.csv")
## ?? How many results is it returning? 

covid19_json = pd.read_json("https://data.cdc.gov/resource/9mfq-cb36.json")

### Should be 14k -> https://healthdata.gov/dataset/united-states-covid-19-cases-and-deaths-state-over-time 

### Looks like something is off with their API - doesn't describe what the parameters are for 
### pageination through their dataset // 
### so to keep things simple, lets just down, upload to github, and pull from there: 
## Just download and upload to github: 
# https://healthdata.gov/dataset/united-states-covid-19-cases-and-deaths-state-over-time

covid19 = pd.read_csv("https://raw.githubusercontent.com/hantsw/statistics/master/United_States_COVID-19_Cases_and_Deaths_by_State_over_Time.csv")


### Lets now create a database and upload this as a table! 
### Lets now re-connect to our same DBMS which is located and definated earlier: ahi.c96anxcynoyv.us-east-1.rds.amazonaws.com
engine.execute("CREATE DATABASE cdc") #create db

## Lets confirm that worked: 
#### Get a list of databases inside of our mySQL DBMS
insp = sqlalchemy.inspect(engine)
db_list = insp.get_schema_names()


## Lets now create a new table within cdc that will contain this covid data 
## so lets name our new table covid19 

MYSQL_DATABASE = 'cdc'
connection_string = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOSTNAME}/{MYSQL_DATABASE}'
engine = create_engine(connection_string)

covid19.to_sql('covid19', con=engine, if_exists='append')


### Lets now dump just a sample of our table into a new dataframe within pandas 
mysqlcovid19sample = pd.read_sql("SELECT * FROM covid19 ORDER BY RAND() LIMIT 10;", con=engine)

### Now lets just select everything and place it into a new dataframe 
### so we can manipulate everything and do some general stats work 

mysqlcovid = pd.read_sql("select * from covid19;", con=engine)

## Lets just do one data cleaning issue: 
mysqlcovid['submission_date'] = pd.to_datetime(mysqlcovid['submission_date'])














#####################
#####################
##
## PARAMETRIC vs NON-PARAMETRIC  
##
#####################
#####################
##Michael Notes change name of datafame to say covid19. dataframe
##df.types = pd.dataframe(covid19.dtypes)


df.types = pd.dataframe(covid19.dtypes)
dftypes = pd.DataFrame(mysqlcovid.dtypes).reset_index()

"""
ones we are interested in here: 
3	tot_cases
6	new_case
8	tot_death
11	new_death
4	conf_cases
5	prob_cases
7	pnew_case
9	conf_death
10	prob_death
12	pnew_death
"""


# Reformatting for Simpler Graphs
temp = px.bar(mysqlcovid, x="submission_date", y=["new_case"], title="New Cases Per Day")
temp.update_layout(yaxis=dict(range=[0,10000]))
plot(temp)
#

###
temp = px.bar(mysqlcovid, x="submission_date", y=["new_death"], title="New Deaths Per Day")
temp.update_layout(yaxis=dict(range=[0,10000]))
plot(temp)
###

###
temp = px.bar(mysqlcovid, x="submission_date", y=["tot_cases"], title="Total Cases")
temp.update_layout(yaxis=dict(range=[0,10000]))
plot(temp)
###

###
temp = px.bar(mysqlcovid, x="submission_date", y=["tot_death"], title="Total Death")
temp.update_layout(yaxis=dict(range=[0,300000]))
plot(temp)
###




#### LINE OR BAR GROUPPED BY STATE ///
#### LINE OR BAR GROUPPED BY STATE ///
temp = px.line(mysqlcovid, x="submission_date", y=["new_case"], color='state', title="New Cases Per Day")
temp.update_layout(yaxis=dict(range=[0,100000]))
plot(temp)


temp = px.line(mysqlcovid, x="submission_date", y=["new_death"], color='state', title="New Deaths Per Day")
temp.update_layout(yaxis=dict(range=[0,1000]))
plot(temp)





### LETS JUST BRIEFLY LOOK AT SOME DESCRIPTIVES: 
### LETS JUST BRIEFLY LOOK AT SOME DESCRIPTIVES: 

mysqlcovid.new_case.describe()
mysqlcovid.new_death.describe()






### Because there is alot here, lets just FOCUS IN ON ONE STATE FOR TONIGHT -> NYC 
### Because there is alot here, lets just FOCUS IN ON ONE STATE FOR TONIGHT -> NYC 
### Because there is alot here, lets just FOCUS IN ON ONE STATE FOR TONIGHT -> NYC 
### Because there is alot here, lets just FOCUS IN ON ONE STATE FOR TONIGHT -> NYC 
### Because there is alot here, lets just FOCUS IN ON ONE STATE FOR TONIGHT -> NYC 

nyc = mysqlcovid[mysqlcovid['state'] == "NYC"]
nyc['submission_date'] = pd.to_datetime(nyc['submission_date'])


### NEW CASES
plt.rc('font', size=12)
fig, ax = pyplot.subplots(figsize=(10, 6))
ax.plot(nyc.submission_date, nyc.new_case, color='tab:blue', label='New Cases')
pyplot.ylim([0,10000])
###


### NEW DEATHS 
plt.rc('font', size=12)
fig, ax = pyplot.subplots(figsize=(10, 6))
ax.plot(nyc.submission_date, nyc.new_death, color='tab:green', label='New Deaths')
pyplot.ylim([0,10000])
###


### NEW CASES vs NEW DEATHS 
pyplot.plot(nyc.submission_date, nyc.new_case, color='tab:blue', label='New Cases')
pyplot.plot(nyc.submission_date, nyc.new_death, color='tab:green', label='New Deaths')
pyplot.ylim([0,10000])
###


#
# multiple line plot
pyplot.plot( 'submission_date', 'new_case', data=nyc, marker='o', markerfacecolor='blue', markersize=5, color='skyblue', linewidth=1)
pyplot.plot( 'submission_date', 'new_death', data=nyc, marker='o', markerfacecolor='green', markersize=5, color='lightgreen', linewidth=1)
pyplot.legend()
pyplot.xticks(rotation=90)
pyplot.ylim([0,10000])
#


# Reformatting for Simpler Graphs
from plotly.offline import plot
temp = px.bar(nyc, x="submission_date", y=["new_case", "new_death"], title="New Cases vs New Deaths in NYC")
temp.update_layout(yaxis=dict(range=[0,15000]))
plot(temp)




### GENERAL DESCRIPTIVE 
### GENERAL DESCRIPTIVE 
nyc.new_case.describe()
nyc.new_death.describe()

nycnewdf = pd.DataFrame()
nycdeath = pd.DataFrame()

nycdescriptives = pd.merge(nycnewdf,nycdeath, .....)


print('mean=%.3f stdv=%.3f' % (np.mean(nyc.new_case), np.std(nyc.new_case)))
print('mean=%.3f stdv=%.3f' % (np.mean(nyc.new_death), np.std(nyc.new_death)))

#Histograms Plots
pyplot.hist(nyc.new_case) # default = 10 
pyplot.hist(nyc.new_case, bins=10) # default = 10 
pyplot.hist(nyc.new_case, bins='auto')
pyplot.show()
pyplot.hist(nyc.new_case, bins='auto', range=[0,2000])




###
pyplot.hist(nyc.new_death)
pyplot.hist(nyc.new_death, bins='auto')
pyplot.show()
pyplot.hist(nyc.new_death, bins='auto', range=[0,500])
pyplot.hist(nyc.new_death, bins='auto', range=[0,100])
###


#Box plots 

###
ax = sns.boxplot(x = nyc.new_death)
ax = sns.boxplot(x = nyc.new_death).set(xlim=(-250, 300))
###

###
ax = sns.boxplot(x = nyc.new_case)
ax = sns.boxplot(x = nyc.new_case).set(xlim=(-250, 3000))
###



#Quantile Plots _Q-Q_

"""

It is a plot where the axes are purposely transformed in order to 
make a normal (or Gaussian) distribution appear in a straight line. 
In other words, a perfectly normal distribution would exactly follow 
a line with slope = 1 and intercept = 0.

Therefore, if the plot does not appear to be - roughly - a straight line, 
then the underlying distribution is not normal. 

https://en.wikipedia.org/wiki/Q%E2%80%93Q_plot

"""

qqplot(nyc.new_case, line='s')
pyplot.show()

qqplot(nyc.new_death, line='s')
pyplot.show()



#Shapiro Wilk normality 
#Shapiro Wilk normality 
#Shapiro Wilk normality 

# normality test
stat, p = shapiro(nyc.new_case)
print('Statistics=%.3f, p=%.3f' % (stat, p))

# interpret
alpha = 0.05
if p > alpha:
	print('Sample looks Gaussian (fail to reject H0)')
else:
	print('Sample does not look Gaussian (reject H0)')


#D' Agostino K/2 Test
#D' Agostino K/2 Test
#D' Agostino K/2 Test

from scipy.stats import normaltest

"""
The D’Agostino’s K^2 test calculates summary statistics from the data, 
namely kurtosis and skewness, to determine if the data distribution departs f
rom the normal distribution, named for Ralph D’Agostino.
"""

# normality test
stat, p = normaltest(nyc.new_case)
print('Statistics=%.3f, p=%.3f' % (stat, p))
# interpret
alpha = 0.05
if p > alpha:
	print('Sample looks Gaussian (fail to reject H0)')
else:
	print('Sample does not look Gaussian (reject H0)')




### At this point, it is pretty clear that for new death and new cases, 
### this is NOT NORMALLY distributed, so now when we want to look at correlations, 
### we know that we should use specific tests that DO NOT MEET 



### QUESTION THAT WE CAN ASK: 
"""
 Is the number of new cases CORRELATED with the number of new deaths 
"""

# Scatter plot between the two variables 
# plot
pyplot.scatter(nyc.new_case, nyc.new_death)
pyplot.show()


# Lets look at potential COVARIANCE between two variables 
"""
Variables can be related by a linear relationship.

This relationship can be summarized between two variables, called the covariance. It is calculated as the average of the product between the values from each sample, where the values haven been centered (had their mean subtracted).


"""
from numpy import cov
covariance = cov(nyc.new_case, nyc.new_death)
print(covariance)

# The covariance between the two variables is 320,362. 
# We can see that it is positive, suggesting the variables 
# change in the same direction as we expect.



# calculate spearman's correlation // non-Gaussian distribution - more powerful here for us 
# calculate spearman's correlation // non-Gaussian distribution
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
from scipy.stats import spearmanr
corr, _ = spearmanr(nyc.new_case, nyc.new_death)
print('Spearmans correlation: %.3f' % corr)


# calculate pearson's correlation // Gaussian distribution - less powerful here for us 
# calculate pearson's correlation // Gaussian distribution 
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
from scipy.stats import pearsonr
corr, _ = pearsonr(nyc.new_case, nyc.new_death)
print('Pearsons correlation: %.3f' % corr)
