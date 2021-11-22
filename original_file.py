# -*- coding: utf-8 -*-
"""
Created on Sun Jun 21 2020

@author: Stanislav "Stas" Lukashevich
"""
#
# TODO:
# PROCESS:
# - Login
# - Scrape
# - Find Nodes
# ----
# - Visualize
#

########################################################
#____________STEP_1:_OPEN_YOUR_LINKEDIN________________#
########################################################

#importing packages for managing web scrapping
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time

# TODO: Store this in an environment variable
# https://www.askpython.com/python/environment-variables-in-python

print("Please enter the exact LinkedIn username you use to login (email/phone?):")
username_string = str(input())
print()
print("Please enter the exact LinkedIn password:")
password_string = str(input())
print()
print("Please enter your usernmae exactly how it appears in your profile link (after '/in') :")
link_username = str(input())
print()
print("Please enter the number of the last posts you want to analyse:")
number_of_posts = int(input())

# TODO:
# -  Decide if and how we would really want ot include further platforms

browser = webdriver.Chrome(
    "C:/Users/Stas/Documents/Analytics_Career/Chrome_Driver/chromedriver.exe.")

#open the LinkedIn login page and login under a specified account:
browser.get('https://www.linkedin.com/login')
#enter the specified information to login to LinkedIn:
elementID = browser.find_element_by_id('username')
elementID.send_keys(username_string)
elementID = browser.find_element_by_id('password')
elementID.send_keys(password_string)
elementID.submit()

#open the recent post activity page of the LinkedIn user you specified:
recent_activity_link = "https://www.linkedin.com/in/" + \
    link_username + "/detail/recent-activity/shares/"
browser.get(recent_activity_link)


def scrape(browser):
    #calculate number of scrolls depending on the input
    # 5 is LinkedIn's number of posts per scroll
    number_of_scrolls = -(-number_of_posts // 5)
    #we need a loop because we have a particular number of scrolls...
    SCROLL_PAUSE_TIME = 5
    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    for scroll in range(number_of_scrolls):
        # Scroll down to bottom
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script(
            "return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    #query the contents (returns service reponse object with web contents, url headers, status and other):
    src = browser.page_source
    #beautiful soup instance:
    return src


def find_nodes(browser, type_of_node, tag, attrs):
    soup = BeautifulSoup(scrape(browser), features="lxml")  # lxml
    results_bs4tags = soup.find_all(tag, attrs=attrs)
    #converts a list of 1 string to int, appends to likes list
    for node in results_bs4tags:
        strnode = str(node)
        #the first argument in findall (below) is a regular expression (accounts for commas in the number)
        list_of_matches = re.findall('[,0-9]+', strnode)
        #converts the last element (string) in the list to int, appends to likes list
        last_string = list_of_matches.pop()
        without_comma = last_string.replace(',', '')
        results_int = int(without_comma)
        data[type_of_node].append(results_int)

    return data


# input
config = {
    'likes': ["span", {"class": "v-align-middle social-details-social-counts__reactions-count"}],
    'comments': ["li", {"class": "social-details-social-counts__item social-details-social-counts__comments"}],
    'views': ["span", {"class": "icon-and-text-container t-14 t-black--light t-normal"}]
}

# output
data = {
    'likes': [],
    'comments': [],
    'views': []
}

for node in config.keys():
    find_nodes(browser, config[node], config[node][0], config[node][1])

print(data)


########################################################
#______________STEP_3:_DATA_VISUALISATION______________#
########################################################


# Reverse the lists
likes.reverse()
comments.reverse()
views.reverse()

# Convert lists into pandas DataFrames
likes_df = pd.DataFrame(likes, columns=['Likes'])
comments_df = pd.DataFrame(comments, columns=['Comments'])
views_df = pd.DataFrame(views, columns=['Views'])

# Get rid of the outliers
#   remove data points if further than 3 standard deviations away...
likes_df_no_outliers = likes_df[np.abs(
    likes_df-likes_df.median()) <= (3*likes_df.std())]
comments_df_no_outliers = comments_df[np.abs(
    comments_df-comments_df.median()) <= (3*comments_df.std())]
views_df_no_outliers = views_df[np.abs(
    views_df-views_df.median()) <= (3*views_df.std())]
#   replace NaN values (deleted outliers) with the median values
likes_df_no_outliers['Likes'].fillna(
    (likes_df_no_outliers['Likes'].median()), inplace=True)
comments_df_no_outliers['Comments'].fillna(
    (comments_df_no_outliers['Comments'].median()), inplace=True)
views_df_no_outliers['Views'].fillna(
    (views_df_no_outliers['Views'].median()), inplace=True)

# Need trend lines and slopes for analysis  & Visualize
print('**************************')
print('********* LIKES **********')
print('**************************')
coefficients_likes, residuals_likes, _, _, _ = np.polyfit(
    range(len(likes_df_no_outliers)), likes_df_no_outliers, 1, full=True)
mse_likes = (residuals_likes[0])/(len(likes_df_no_outliers))
nrmse_likes = (np.sqrt(mse_likes)) / \
    (likes_df_no_outliers.max() - likes_df_no_outliers.min())
slope_likes = coefficients_likes[0]
print('Slope: ' + str(slope_likes))
print('NRMSE Error: ' + str(nrmse_likes))
plt.plot(likes_df_no_outliers)
plt.plot([slope_likes*x + coefficients_likes[1]
         for x in range(len(likes_df_no_outliers))])
plt.title('Linkedin Post Likes for ' + link_username)
plt.xlabel('Posts')
plt.ylabel('Likes')
plt.savefig(link_username + '-linkedin-likes-last-' +
            str(number_of_posts) + '-posts-GRAPH.png', dpi=600)
plt.show()
plt.clf()

print('**************************')
print('******* COMMENTS *********')
print('**************************')
coefficients_comments, residuals_comments, _, _, _ = np.polyfit(
    range(len(comments_df_no_outliers)), comments_df_no_outliers, 1, full=True)
mse_comments = (residuals_comments[0])/(len(comments_df_no_outliers))
nrmse_comments = (np.sqrt(mse_comments)) / \
    (comments_df_no_outliers.max() - comments_df_no_outliers.min())
slope_comments = coefficients_comments[0]
print('Slope: ' + str(slope_comments))
print('NRMSE Error: ' + str(nrmse_comments))
plt.plot(comments_df_no_outliers)
plt.plot([slope_comments*x + coefficients_comments[1]
         for x in range(len(comments_df_no_outliers))])
plt.title('LinkedIn Post Comments for ' + link_username)
plt.xlabel('Posts')
plt.ylabel('Comments')
plt.savefig(link_username + '-linkedin-comments-last-' +
            str(number_of_posts) + '-posts-GRAPH.png', dpi=600)
plt.show()
plt.clf()

print('**************************')
print('********* VIEWS **********')
print('**************************')
coefficients_views, residuals_views, _, _, _ = np.polyfit(
    range(len(views_df_no_outliers)), views_df_no_outliers, 1, full=True)
mse_views = (residuals_views[0])/(len(views_df_no_outliers))
nrmse_views = (np.sqrt(mse_views)) / \
    (views_df_no_outliers.max() - views_df_no_outliers.min())
slope_views = coefficients_views[0]
print('Slope: ' + str(slope_views))
print('NRMSE Error: ' + str(nrmse_views))
plt.plot(views_df_no_outliers)
plt.plot([slope_views*x + coefficients_views[1]
         for x in range(len(views_df_no_outliers))])
plt.title('LinkedIn Post Views for ' + link_username)
plt.xlabel('Posts')
plt.ylabel('Views')
plt.savefig(link_username + '-linkedin-views-last-' +
            str(number_of_posts) + '-posts-GRAPH.png', dpi=600)
plt.show()
plt.clf()


# Save dataframes as CSV files
likes_df_no_outliers.to_csv(
    link_username + '-linkedin-likes-last-' + str(number_of_posts) + '-posts.csv')
comments_df_no_outliers.to_csv(
    link_username + '-linkedin-comments-last-' + str(number_of_posts) + '-posts.csv')
views_df_no_outliers.to_csv(
    link_username + '-linkedin-views-last-' + str(number_of_posts) + '-posts.csv')

# Save plots as images
#    did that above for every plot

########################################################
#_______________________THE_END________________________#
########################################################