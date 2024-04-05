import os
import json

def load_config(
        required_config_params=[],
        load_from_env='required',
        load_from_file='all',
        config_file='config.json',
        config_env_prefix='',
        env_vars_are_upper_case=True,
        priority='env',
        ignore_missing_file=False
    ):
    """
    Load the configuration parameters from environment variables and a config file.

    Args:
        required_config_params (list, optional): List of required configuration parameters. Defaults to [].
        load_from_env (str, optional): Determines which parameters to load from environment variables. 
            Possible values are 'required', 'all', or a list of environment variable names. Defaults to 'required'.
        load_from_file (str, optional): Determines which parameters to load from the config file. 
            Possible values are 'required', 'all', or a list of config file keys. Defaults to 'all'.
        config_file (str, optional): Path to the config file. Defaults to 'config.json'.
        config_env_prefix (str, optional): Prefix to be added to the environment variable names. Defaults to ''.
        env_vars_are_upper_case (bool, optional): Whether the environment variables are in upper case. Defaults to True. If false, the environment variables are expected to be in the same case as the config file keys.
        priority (str, optional): Determines the priority of merging the config from environment and config file. 
            Possible values are 'env' or 'file'. Defaults to 'env'.
        ignore_missing_file (bool, optional): Whether to ignore if the config file is missing. Defaults to False.

    Notes:
        - The environment variables are expected to be in upper case.
        - The config file should be a JSON file with the configuration parameters as key-value pairs.

    Returns:
        dict: A dictionary containing the loaded configuration parameters.
    """

    # determine which parameters to load from environment variables
    if load_from_env == 'required':
        params_to_load_from_env = required_config_params
    elif load_from_env == 'all':
        params_to_load_from_env = [os.environ]
    elif type(load_from_env) == list:
        params_to_load_from_env = load_from_env
    else:
        raise ValueError("load_from_env must be 'required', 'all', or a list of environment variable names")

    # determine which parameters to load from the config file
    if load_from_file == 'required':
        params_to_load_from_file = required_config_params
    elif load_from_file == 'all':
        params_to_load_from_file = config_from_file.keys()
    elif type(load_from_file) == list:
        params_to_load_from_file = load_from_file
    else:
        raise ValueError("load_from_file must be 'required', 'all', or a list of config file keys")

    config_from_env = {}
    config_from_file = {}

    # get all required config parameters from environment variables
    for param in params_to_load_from_env:
        param_modified = (config_env_prefix + param)
        if env_vars_are_upper_case:
            param_modified = param_modified.upper()
        if param_modified in os.environ:
            config_from_env[param] = os.environ[param_modified]

    # Load the configuration file
    try:
        with open(config_file) as f:
            config_from_file = json.load(f)
    except FileNotFoundError:
        if not ignore_missing_file:
            raise FileNotFoundError(f"Config file not found: {config_file}")

    for param in config_from_file:
        if param not in params_to_load_from_file:
            del config_from_file[param]

    # Merge the config from the environment and the config file
    if priority == 'env':
        config = {**config_from_file, **config_from_env}
    elif priority == 'file':
        config = {**config_from_env, **config_from_file}
    else:
        raise ValueError("priority must be 'env' or 'file'")

    # Check that all required config parameters are present
    for param in required_config_params:
        if param not in config:
            print(f"Missing required config parameter: {param}. It can be set either as an environment variable (as {param.upper()}) or in {config_file} (as {param}).")
            exit(1)

    return config
