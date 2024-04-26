import os
import json

def load_config(
        required_config_params=[],
        load_from_env='required',
        load_from_file='all',
        config_file='config.json',
        config_env_prefix='',
        priority='env',
        ignore_missing_file=False,
        azure_app_services=False
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
        azure_app_services (bool, optional): Whether to treat the environment as an Azure App Service environment. Defaults to False, but will be set to True if the environment variables 'WEBSITE_SITE_NAME' and 'WEBSITE_RESOURCE_GROUP' are present, as this indicates that the code is running in an Azure App Service environment.

    Notes:
        - The environment variables are expected to be in upper case.
        - The config file should be a JSON file with the configuration parameters as key-value pairs.

    Returns:
        dict: A dictionary containing the loaded configuration parameters.
    """

    config_from_env = {}
    config_from_file = {}

    # Load the configuration file
    try:
        with open(config_file) as f:
            config_from_file = json.load(f)
            config_from_file = {k.lower(): v for k, v in config_from_file.items()} # Convert all keys to lower case
    except FileNotFoundError:
        if not ignore_missing_file:
            raise FileNotFoundError(f"Config file not found: {config_file}")

    # Convert all keys to lower case
    required_config_params = [param.lower() for param in required_config_params]
    os_environ_lower = {k.lower(): v for k, v in os.environ.items()}
    config_env_prefix = config_env_prefix.lower()

    # detect if we're in an azure app service environment
    if 'website_site_name' in os_environ_lower and "website_resource_group" in os_environ_lower:
        # we're definitely in an azure app service environment
        azure_app_services = True

    # determine which parameters to load from environment variables
    if load_from_env == 'required':
        params_to_load_from_env = {k.lower() for k in required_config_params}
    elif load_from_env == 'all':
        params_to_load_from_env = {k[len(config_env_prefix):] for k in os_environ_lower.keys() if k.startswith(config_env_prefix)}
    elif type(load_from_env) == list:
        params_to_load_from_env = load_from_env
    else:
        raise ValueError("load_from_env must be 'required', 'all', or a list of environment variable names")

    if load_from_env == 'all':
        # filter out the env.vars that do not start with the config_env_prefix and remove the prefix from the ones that do
        config_from_env = {k[len(config_env_prefix):]: v for k, v in os_environ_lower.items() if k.startswith(config_env_prefix) and k[len(config_env_prefix):] in params_to_load_from_env}
    else:
        # if we're in an azure app service environment, we need to convert dots to underscores in the environment variables
        # unless we got the env.vars from the environment (load_from_env == 'all'), as they are already in the correct format
        if azure_app_services:
            params_to_load_from_env = {k.replace('.', '_') for k in params_to_load_from_env}

    # determine which parameters to load from the config file
    if load_from_file == 'required':
        params_to_load_from_file = required_config_params
    elif load_from_file == 'all':
        params_to_load_from_file = config_from_file.keys()
    elif type(load_from_file) == list:
        params_to_load_from_file = load_from_file
    else:
        raise ValueError("load_from_file must be 'required', 'all', or a list of config file keys")

    # filter out the config parameters that are not in the list of parameters to load from the file
    for param in config_from_file.copy():
        if param not in params_to_load_from_file:
            del config_from_file[param]

    # get all required config parameters from environment variables
    # Note about Azure App Services: 
    # Azure converts dots to underscores in environment variables and adds a prefix (in addition to keeping the original name as well -- although still with underscores instead of dots)
    # This applies to all settings in Azure App Services / Configuration / Application Settings -- but not system environment variables
    for param in params_to_load_from_env:
        env_var_to_lookup = f"{config_env_prefix}{param}"
        env_var_to_lookup_in_azure = f"appsetting_{env_var_to_lookup}" # azure app services prefix
        
        # if we're in an azure app service environment and the env.var with the prefix is set, then load it
        if azure_app_services and not load_from_env == 'all' and env_var_to_lookup_in_azure in os_environ_lower:
            config_from_env[param] = os_environ_lower.get(f"appsetting_{env_var_to_lookup}")

        # if we're not in an azure app service environment, then just load the env.var without the prefix
        # also if we're in an azure app service environment and the env.var with the prefix is not set, then try to get the env.var without the prefix, as this applies to system environment variables
        if env_var_to_lookup in os_environ_lower:
            if not config_from_env.get(param):
                config_from_env[param] = os_environ_lower.get(env_var_to_lookup)

        # check if there are any sub-parameters for this parameter and load them as a dictionary
        if azure_app_services:
            prefix = f"{env_var_to_lookup_in_azure}_"
        else:
            prefix = f"{env_var_to_lookup}." # all other places than Azure App Services (as far as we know)
        # if there are env.vars that start with param and a dot, then load them as a dictionary
        # e.g. PREFIX_PARAM1.KEY1=value1, PREFIX_PARAM1.KEY2=value2
        # results in: config['param1'] = {'key1': 'value1', 'key2': 'value2'}
        for k, v in os_environ_lower.items():
            if k.startswith(prefix):
                config_from_env[param] = config_from_env.get(param, {})
                config_from_env[param][k[len(prefix):].lower()] = v

    # if there are dots in the required config parameters, they now have underscores if they are from Azure App Services environment variables
    # example:
    # config_from_env  = {'param127_key2': 'env_value2', 'param127_key1': 'env_value1'}
    # config_from_file = {'param127.key1': 'file_value1', 'param127.key2': 'file_value2'}
    # convert them back to dots (but not ALL, just the underscores that used to be a dot)
    if azure_app_services:
        if load_from_env == 'required':
            env_vars_to_convert = required_config_params
        elif type(load_from_env) == list:
            env_vars_to_convert = load_from_env
        else:
            env_vars_to_convert = []
        for param in env_vars_to_convert:
            # if the parameter, with dots converted to underscores, is in the environment variables, then convert it back to dots
            if param.replace('.', '_') in config_from_env:
                config_from_env[param] = config_from_env.pop(param.replace('.', '_'))
        # now the environment variables are back to the original format 
        # (with dots instead of underscores if specified in the config file)
        # so we can merge the environment variables and the config file

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
