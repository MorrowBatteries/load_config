# load_config

A simple library to load config parameters from environment variables and/or config files (JSON format).
Published as a library just to prevent duplication.

## Features

### reads from a json config file and/or OS environment variables

you can set what to prioritize (default: environment)

### nested config params in environment variables

If you define OS environment variables like this:

```bash
PARAM.SUB_PARAM1 = "p1"
PARAM.SUB_PARAM2 = "p2"
```

You will get a config parameter `config['param']` like this:

```json
"param": {
    "sub_param1": "p1",
    "sub_param2": "p2"
}
```

Note that on Azure App Services, when setting these environment variables in Configuration / Application Settings, Azure converts any periods to underscores even it they say periods are allowed. load_config will detect if it is running in an Azure environment, but you can also force it by setting the optonal parameter "azure_app_services" to True.

```python
config = load_config(required_config_params=["param"], azure_app_services=True)
# your setting in Azure App Services / Configuration / Application Settings:
# PARAM.SUB_PARAM1 = "p1"
# PARAM.SUB_PARAM2 = "p2"

# actual environment variables set in the OS:
# APPSETTING_PARAM_SUB_PARAM1 = "p1"
# APPSETTING_PARAM_SUB_PARAM2 = "p2"

config["param"] # gives you { "sub_param1": "p1", "sub_param2": "p2" }
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Run tests and generate coverage report

```coverage run -m pytest ; coverage xml```

## Author

Ronny Ager-Wick, Morrow Batteries ASA

## License

[MIT](https://choosealicense.com/licenses/mit/)
