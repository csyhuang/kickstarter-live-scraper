# coding: utf-8
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import re
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import time


def scraper_prototype(text_profile, prefix):

    if '"name"' in text_profile:
        text_profile = re.sub('"', '', text_profile)

    text2 = text_profile.split(',')
    dummy2 = [re.findall('[A-Za-z0-9_]+:', ww) for ww in text2]
    itemname = [dum_part[0] for dum_part in dummy2 if len(dum_part) > 0]
    ans_array = [re.search(xxy1+'(.*?)'+xxy2, text_profile).group(1).rstrip(',')
                 for xxy1, xxy2 in zip(itemname[:-1], itemname[1:])]
    itemnames = [x.rstrip(':') for x in itemname]

    info_dict = dict()
    for item, ans in zip(itemnames, ans_array):
        info_dict[prefix+'_'+item] = ans
    return info_dict


def kickstarter_scraper(engine, table_name_prefix,
                        separate_table_for_each_day=False,
                        restart_drop_table=False):

    """
    This function will scrap pages of different categories on  kickstarter
    website and store the data into the database specified in engine.

    Args:
        engine (obj): An instance of create_engine() in sqlalchemy
        table_name_prefix (str): Prefix of table that stores the data, or the
        name of it if no datestring suffix is used
        separate_table_for_each_day (bool): Whether to create tables with
        datestring (True), or keep inserting data into the same table (False)
        restart_drop_table (bool): Whether to drop the table (True) whenever
        the function is called.

    Returns:
        data_from_sql (pandas DataFrame): The number of distinct project names
        in each category in the database

    """

    category_dict = {'Art': '1', 'Comics': '3', 'Crafts': '26', 'Dance': '6',
                     'Design': '7', 'Fashion': '9', 'Film_and_Video': '11',
                     'Food': '10', 'Games': '12', 'Journalism': '13',
                     'Music': '14', 'Photography': '15', 'Publishing': '18',
                     'Technology': '16', 'Theater': '17'}

    if not database_exists(engine.url):
        create_database(engine.url)
    print('Database exist? ' + str(database_exists(engine.url)))

    con = engine.connect()
    if separate_table_for_each_day:
        table_name = table_name_prefix+'_'+str(time.strftime("%Y%m%d"))
    else:
        table_name = table_name_prefix

    if restart_drop_table:
        command = "DROP TABLE IF EXISTS "+table_name+";"
        con.execute(command)

    # Loading the project info on a page using a scraper prototype and save into database.
    for category_key in category_dict:

        # === Create the table (if not exist) ===
        category = category_key
        print(category_key)

        # === Start scraping ===
        total_num_of_items = 0
        for pageno in range(100):

            time_stamp = time.strftime("%d/%m/%Y %H:%M:%S")

            r = urllib.request.urlopen('https://www.kickstarter.com/discover/advanced?state=live&category_id='
                                       + category_dict[category]+'&sort=popularity&seed=2506137&page='+str(pageno)).read()
            soup = BeautifulSoup(r, 'html.parser')

            kk = soup.find_all('div', class_="js-react-proj-card")
            total_num_of_items += len(kk)

            # Last page to scrap
            if len(kk) == 0:
                print('page number = %s, total number of items = %s'
                      % (str(pageno), str(total_num_of_items)))
                break

            for i in range(len(kk)):
                whole_string = str(kk[i]).replace('&amp', '').replace('&quot;', '')

                # === Overall project info ===
                if '"name"' in whole_string:
                    project_info = '"name"' + re.findall('"name"(.+?)"creator"', whole_string)[0]
                else:
                    project_info = 'name' + re.findall('name(.+?)creator', whole_string)[0]
                project_info_dict = scraper_prototype(project_info, 'project')
                df1 = pd.DataFrame.from_dict(project_info_dict, orient='index').transpose()

                # === Scrap creater string ===
                if '"creator"' in whole_string:
                    creator_string = re.findall(r'\"creator\"\:\{(.+?)\}', whole_string)[0]
                else:
                    creator_string = re.findall(r'creator\:\{(.+?)\}', whole_string)[0]
                creator_info_dict = scraper_prototype(creator_string, 'creator')
                creator_info_dict['creator_slug'] = creator_info_dict.get('creator_slug', 'Null')
                df2 = pd.DataFrame.from_dict(creator_info_dict, orient='index').transpose()

                # === Scrap location string ===
                if '"location"' in whole_string:
                    location_string = re.findall(r'\"location\"\:\{(.+?)\}', whole_string)[0]
                else:
                    location_string = re.findall(r'location\:\{(.+?)\}', whole_string)[0]
                location_info_dict = scraper_prototype(location_string, 'location')
                df3 = pd.DataFrame.from_dict(location_info_dict, orient='index').transpose()

                # === Scrap profile string ===
                if '"profile"' in whole_string:
                    profile_string = re.findall(r'\"profile\"\:\{(.+?)\}', whole_string)[0]
                else:
                    profile_string = re.findall(r'profile\:\{(.+?)\}', whole_string)[0]

                profile_info_dict = scraper_prototype(profile_string, 'profile')
                df4 = pd.DataFrame.from_dict(profile_info_dict, orient='index').transpose()

                df = pd.concat((df1, df2, df3, df4), axis=1)
                df['category'] = category_key
                df['retrieval_time'] = time_stamp

                # Record down columns
                if pageno == 0 and i==0:
                    df_columns = df.columns

                try:
                    df.to_sql(table_name, engine, if_exists='append')
                except:
                    to_eliminate = set(df.columns.values) - set(df_columns.values)
                    for to_drop in to_eliminate:
                        df.drop(to_drop, axis=1, inplace=True)
                    df.to_sql(table_name, engine, if_exists='append')

    # Check what's on the SQL database
    sql_query = """
    SELECT COUNT(*) FROM %s;
    """
    kickstarter_data_from_sql = pd.read_sql_query(sql_query % (table_name), con)
    print('number of rows in table "'+table_name+'" = ' +
          str(kickstarter_data_from_sql.values[0][0]))

    sql_query = """
    SELECT category as 'Category', COUNT(DISTINCT(project_name)) as 'Number of Projects' FROM %s
    GROUP BY category;
    """
    data_from_sql = pd.read_sql_query(sql_query % (table_name),con)

    return data_from_sql


if __name__ == "__main__":

    # === Input parameters ===
    dbname = 'kickstarter_db'  # Name of your database
    user_id = 'username'  # User name
    user_password = 'password'  # Password

    # Connection to the MySQL database
    engine = create_engine("mysql+pymysql://%s:%s@localhost:3306/%s?charset=utf8"
                           % (user_id, user_password, dbname), encoding='utf8')

    # The name / prefix of table that stores the data
    table_name_prefix = 'kickstarter'

    # Whether to build a new table with date as its name,
    # e.g. kickstarter_20170912
    separate_table_for_each_day = False

    # Drop existing table when running the code
    restart_drop_table = False

    # === Run the scraper ===
    kickstarter_scraper(engine, table_name_prefix,
                        separate_table_for_each_day=separate_table_for_each_day,
                        restart_drop_table=restart_drop_table)
