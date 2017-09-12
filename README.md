### kickstarter-live-scraper

This module scraps the project details on kickstarter.com on all the category pages and store 
them in MySQL database using the *sqlalchemy* interface. You can refer to my [blog post](https://csyhuang.github.io/2017/09/09/install-mysql/) 
on how to set up MySQL on Mac OS X.

### Python package dependencies
- pandas
- BeautifulSoup  
- urllib  
- re  
- sqlalchemy  
- sqlalchemy_utils
- time

### How to use it

The script *Kickstarter_scraper_to_MySQL.py* can be run alone with the path of MySQL database,
 username and password specified (see lines 170-190). Here is an example how to call the function *kickstarter_scraper*:
 
```python

# === Input parameters ===
dbname = 'kickstarter_db'  # Name of your database
user_id = 'username'  # User name
user_password = 'password'  # Password

# Connection to the MySQL database
engine = create_engine("mysql+pymysql://%s:%s@localhost:3306/%s?charset=utf8"
                       % (user_id, user_password, dbname), encoding='utf8')

table_name_prefix = 'kickstarter' # The name / prefix of table that stores the data
separate_table_for_each_day = False # Whether to build a new table with date as its name, e.g. kickstarter_20170912
restart_drop_table = False # Drop existing table when running the code

# === Run the scraper ===
kickstarter_scraper(engine, table_name_prefix,
                    separate_table_for_each_day=separate_table_for_each_day,
                    restart_drop_table=restart_drop_table)
                        
```

The returned object will be a pandas DataFrame that lists the number of unique projects for
 each category in your MySQL database, e.g.
 
```
          Category  Number of Projects
0              Art                 299
1           Comics                 163
2           Crafts                 131
3            Dance                  35
4           Design                 515
5          Fashion                 375
6   Film_and_Video                 443
7             Food                 270
8            Games                 550
9       Journalism                  73
10           Music                 394
11     Photography                 102
12      Publishing                 452
13      Technology                 558
14         Theater                  78
``` 
 
