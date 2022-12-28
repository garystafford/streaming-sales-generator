import configparser


def get_configs():
    config = configparser.ConfigParser()
    config.read("configuration/configuration.ini")

    bootstrap_servers = config["KAFKA"]["bootstrap_servers"]
    auth_method = config["KAFKA"]["auth_method"]
    sasl_username = config["KAFKA"]["sasl_username"]
    sasl_password = config["KAFKA"]["sasl_password"]

    configs = {"bootstrap_servers": bootstrap_servers}

    if auth_method == "sasl_scram":
        configs["security_protocol"] = "SASL_SSL"
        configs["sasl_mechanism"] = "SCRAM-SHA-512"
        configs["sasl_plain_username"] = sasl_username
        configs["sasl_plain_password"] = sasl_password

    # print("configs: {0}".format(str(configs)))

    return configs
