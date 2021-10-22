import database.client,config.global_config

database.client.open_connection(
    config.global_config.global_config['database-server-host'],
    config.global_config.global_config['database-server-port'],
    config.global_config.global_config['database-server-username'],
    config.global_config.global_config['database-server-password']
)

database.client.table_operate('oj_records','new')
database.client.table_operate('oj_problems','new')
database.client.table_operate('oj_board','new')
database.client.table_operate('oj_ranking','new')
database.client.table_operate('oj_users','new')
