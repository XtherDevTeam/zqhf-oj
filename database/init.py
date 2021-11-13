import database.client,config.global_config,web.users,database.dbapis,os

if not os.access('database/main.db',os.F_OK):
    database.dbapis.saveDBFile()

database.client.open_connection(
    config.global_config.global_config['database-server-host'],
    config.global_config.global_config['database-server-port'],
    config.global_config.global_config['database-server-username'],
    config.global_config.global_config['database-server-password']
)

if database.client.table_operate('oj_records','info')[0] == 'FAIL': database.client.table_operate('oj_records','new','list')
if database.client.table_operate('oj_problems','info')[0] == 'FAIL': database.client.table_operate('oj_problems','new','list')
if database.client.table_operate('oj_board','info')[0] == 'FAIL': database.client.table_operate('oj_board','new','dict')
if database.client.table_operate('oj_ranking','info')[0] == 'FAIL': database.client.table_operate('oj_ranking','new','list')
if database.client.table_operate('oj_users','info')[0] == 'FAIL': database.client.table_operate('oj_users','new','dict')
if database.client.table_operate('oj_problem_lists','info')[0] == 'FAIL': database.client.table_operate('oj_problem_lists','new','dict')
if database.client.table_operate('oj_article','info')[0] == 'FAIL': database.client.table_operate('oj_article','new','list')
if database.client.table_operate('oj_notebook','info')[0] == 'FAIL': database.client.table_operate('oj_notebook','new','dict')
if database.client.table_operate('oj_userimage','info')[0] == 'FAIL': database.client.table_operate('oj_userimage','new','dict')
if database.client.table_operate('oj_users','admin','info')[0] == 'FAIL': web.users.new_user('admin',0,'admin')