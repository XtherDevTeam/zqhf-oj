import database.server,config.global_config

database.server.run('0.0.0.0',5917,config=config.global_config.database_server_config)