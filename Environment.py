import os


def read_env_variables(path: str):
    env_file = open(path)

    for line in env_file:
        if line.find("=") == -1:
            continue

        data = line.split('=')
        os.environ[data[0]] = data[1]
