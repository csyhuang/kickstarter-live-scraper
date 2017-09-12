# kickstarter-live-scraper

This module scraps the project details on kickstarter.com on all the category pages and store 
them in MySQL database using the *sqlalchemy* interface. You can refer to my [blog post](https://csyhuang.github.io/2017/09/09/install-mysql/) 
on how to set up MySQL on Mac OS X.

The script *Kickstarter-scraper-to-MySQL.py* can be run alone with the path of MySQL database,
 username and password specified (see lines 170-190). Here is an example how to call the function *kickstarter_scraper*:
 
```python

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
                        
```

The returned object will be a pandas DataFrame that lists the number of unique projects for
 each category in your MySQL database, e.g.
 
```
          Category  Number of Projects
0              Art                 275
1           Comics                  12
2           Crafts                  12
3            Dance                  23
4           Design                  12
5          Fashion                  12
6   Film_and_Video                  12
7             Food                  12
8            Games                 513
9       Journalism                  12
10           Music                 191
11     Photography                  90
12      Publishing                  12
13      Technology                  12
14         Theater                  12
``` 
 
# Python package dependencies
- pandas
- BeautifulSoup  
- urllib  
- re  
- sqlalchemy  
- sqlalchemy_utils
- time

