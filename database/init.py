import database.client,config.global_config,web.users,database.dbapis

database.dbapis.saveDBFile()

database.client.open_connection(
    config.global_config.global_config['database-server-host'],
    config.global_config.global_config['database-server-port'],
    config.global_config.global_config['database-server-username'],
    config.global_config.global_config['database-server-password']
)

database.client.table_operate('oj_records','new','list')
database.client.table_operate('oj_problems','new','list')
database.client.table_operate('oj_board','new','dict')
database.client.table_operate('oj_ranking','new','list')
database.client.table_operate('oj_users','new','dict')
database.client.table_operate('oj_problem_lists','new','dict')
database.client.table_operate('oj_article','new','list')
web.users.new_user('admin',0,'admin')
