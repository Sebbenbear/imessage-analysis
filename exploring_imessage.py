import os
import sys
import sqlite3
from datetime import date, datetime
import pandas as pd
import matplotlib.pyplot as plt
import nltk
import json

USERNAME = os.popen('whoami').read().strip()


chat_db = '/Users/'+USERNAME+'/Library/Messages/chat.db'

conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        SELECT name 
        FROM sqlite_master 
        WHERE type='table';
        '''
df = pd.read_sql_query(query, conn)
conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        PRAGMA table_info (message);
        '''
df = pd.read_sql_query(query, conn)

pd.set_option('display.max_rows', 1000) # Display all columns
conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        SELECT ROWID, date, text 
        FROM message;
        '''
df = pd.read_sql_query(query, conn)
print(df[:5])

conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        SELECT ROWID, text,
        datetime(message.date/1000000000 + strftime("%s", "2001-01-01") ,"unixepoch","localtime") as date
        FROM `message`;
        '''
# Less than OSX 10.13 use this query
# query = '''
#         SELECT ROWID, text,
#         datetime(message.date + strftime("%s", "2001-01-01") ,"unixepoch","localtime") as date
#         FROM `message`;
#         '''
df = pd.read_sql_query(query, conn)
print(df[:5])

conn = sqlite3.connect(chat_db, check_same_thread=False)        
query = '''
        SELECT * 
        FROM `message`;
        '''
df = pd.read_sql_query(query, conn)

df.describe()
conn = sqlite3.connect(chat_db, check_same_thread=False)        
query = '''
        SELECT count(ROWID) as count 
        FROM `message`;
        '''
df = pd.read_sql_query(query, conn)
number_of_messages = df['count'][0]
print(number_of_messages)

conn  =  sqlite3.connect(chat_db, check_same_thread=False)        

query = '''
        SELECT
        sum(case when is_from_me = 1 then 1 else 0 end) as from_me,
        sum(case when is_from_me = 0 then 1 else 0 end) as from_others,
        count(ROWID) as total
        FROM `message`
        '''

df = pd.read_sql_query(query, conn)

conn  =  sqlite3.connect(chat_db, check_same_thread =False)

date_time_conversion = 'datetime(message.date/1000000000 + strftime("%s", "2001-01-01") ,"unixepoch","localtime")'
# Less than OSX 10.13 use this query
# date_time_conversion = 'datetime(message.date + strftime("%s", "2001-01-01") ,"unixepoch","localtime")'

query = '''
        SELECT min({}) as min_date, max({}) as max_date
        FROM `message`;
        '''.format(date_time_conversion, date_time_conversion)
        
df = pd.read_sql_query(query, conn)
min_date_string = df['min_date'][0]
min_date = datetime.strptime(min_date_string, "%Y-%m-%d %H:%M:%S")

max_date_string = df['max_date'][0]
max_date = datetime.strptime(max_date_string, "%Y-%m-%d %H:%M:%S")

delta = (max_date - min_date).days

average = number_of_messages / delta
print('I exchange {:.3f} messages on average per day.'.format(average))

conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        SELECT ROWID, text,
        datetime(message.date/1000000000 + strftime("%s", "2001-01-01"), "unixepoch","localtime") as date
        FROM `message`;
        '''
# Less than OSX 10.13 use this query
# query = '''
#         SELECT ROWID, text,
#         datetime(message.date + strftime("%s", "2001-01-01"), "unixepoch","localtime") as date
#         FROM `message`;
#         '''

df = pd.read_sql_query(query, conn)
df['Dates'] = df['date'].apply(lambda x: x[:10])

frequencies = df.groupby('Dates')['ROWID'].count()
frequencies.plot(kind='line', figsize=(15, 10))
plt.show()
conn = sqlite3.connect(chat_db, check_same_thread=False)
query = '''
        SELECT count(handle.ROWID) as total, handle.id, message.text 
        FROM `handle` JOIN `message` 
        ON handle.ROWID = message.handle_id 
        GROUP BY handle.id 
        ORDER BY total DESC 
        LIMIT 10;
        '''
df = pd.read_sql_query(query, conn)
# my_plot = df.plot(kind='bar', x=df['id']) # display who they are

my_plot = df.plot(kind='bar')
my_plot.set_xlabel("Contacts")
my_plot.set_ylabel("Exchanged messages")
plt.show()
conn = sqlite3.connect(chat_db, check_same_thread=False)        

query = '''
        SELECT
        text
        FROM `message`
        WHERE is_from_me = 1
        '''

my_imessage_df = pd.read_sql_query(query, conn)
my_imessage_df[:3]

# we need to account for empty messages# we nee 
messages = [msg for msg in my_imessage_df["text"] if msg]

msg_tokens = []
for msg in messages:
    new_set = nltk.word_tokenize(msg)
    msg_tokens.extend(new_set)
    

text = nltk.Text(msg_tokens)
text.dispersion_plot([
    "hungry", "happy", "sad", "sleepy", "jealous", "angry", "gutted"
])
text.dispersion_plot([
    "breakfast", "brunch", "lunch", "dinner", "snack", "dessert"
])
