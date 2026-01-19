def read_config(config_file: "str") -> dict:
    with open(config_file, "r") as config:
        for line in config:
            if line.startswith("#"):
                continue
            if lin
