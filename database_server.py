import database.server,config.global_config

database.server.run(config.global_config.global_config['database-server-host'],
    config.global_config.global_config['database-server-port'],
    config=config.global_config.database_server_config
)