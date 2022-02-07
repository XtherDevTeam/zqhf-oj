import database.client,config.global_config,web.users,database.dbapis,os

if not os.access('database/main.db',os.F_OK):
    database.dbapis.saveDBFile()

database.client.open_connection(
    config.global_config.global_config['database-server-host'],
    config.global_config.global_config['database-server-port'],
    config.global_config.global_config['database-server-username'],
    config.global_config.global_config['database-server-password']
)

if database.client.table_operate('oj_records','info')[0] == 'FAIL': database.client.table_operate('oj_records@list','new')
if database.client.table_operate('oj_problems','info')[0] == 'FAIL': database.client.table_operate('oj_problems@list','new')
if database.client.table_operate('oj_board','info')[0] == 'FAIL': database.client.table_operate('oj_board@dict','new')
if database.client.table_operate('oj_ranking','info')[0] == 'FAIL': database.client.table_operate('oj_ranking@list','new')
if database.client.table_operate('oj_users','info')[0] == 'FAIL': database.client.table_operate('oj_users@dict','new')
if database.client.table_operate('oj_problem_lists','info')[0] == 'FAIL': database.client.table_operate('oj_problem_lists@dict','new')
if database.client.table_operate('oj_article','info')[0] == 'FAIL': database.client.table_operate('oj_article@list','new')
if database.client.table_operate('oj_notebook','info')[0] == 'FAIL': database.client.table_operate('oj_notebook@dict','new')
if database.client.table_operate('oj_contests','info')[0] == 'FAIL': database.client.table_operate('oj_contests@list','new')
if database.client.table_operate('oj_users','admin','info')[0] == 'FAIL': web.users.new_user('admin',0,'admin')