from typing import Dict


def read_config(config_file: "str") -> dict:
    configs: Dict[str, str] = {}
    with open(config_file, "r") as config:
        for line in config:
            if line.startswith("#") or '=' not in line:
                continue
            if line.startswith("WIDTH"):
                if configs.get("width") is None:
                    configs["width"] = line.split("=")[1].strip("\n")
                    if int(configs["width"]) <= 0:
                        raise ValueError("width cannot be less than 1")
                else:
                    raise ValueError("Width is defined multiple times!")
            if line.startswith("HEIGHT"):
                if configs.get("height") is None:
                    configs["height"] = line.split("=")[1].strip("\n")
                    if int(configs["height"]) <= 0:
                        raise ValueError("height cannot be less than 1")
                else:
                    raise ValueError("Height is defined multiple times!")
            if line.startswith("ENTRY"):
                if configs.get("entry") is None:
                    configs["entry"] = line.split("=")[1].strip("\n")
                else:
                    raise ValueError("Entry is defined multiple times!")
            if line.startswith("EXIT"):
                if configs.get("exit") is None:
                    configs["exit"] = line.split("=")[1].strip("\n")
                else:
                    raise ValueError("Exit is defined multiple times!")
            if line.startswith("PERFECT"):
                if configs.get("perfect") is None:
                    configs["perfect"] = line.split("=")[1].strip("\n")
                    if configs["perfect"] not in ["True", "False"]:
                        raise ValueError(
                            'Perfect needs to be either "True" or "False"'
                        )
                else:
                    raise ValueError("Perfect is defined multiple times!")
    if configs.get("width") is None or configs.get("height") is None:
        raise ValueError(
            '"WIDTH" and "HEIGHT" must be defined in the config file'
        )
    return configs


try:
    print(read_config("config.txt"))
except Exception as e:
    print(e)
