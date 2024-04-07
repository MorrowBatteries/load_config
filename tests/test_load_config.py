import pytest
import os
from unittest.mock import patch, mock_open
from load_config import load_config

# WARNING: when running all tests at once, keep in mind the os.environ is global and will be modified by the tests

def test_priority_env():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PARAM1'] = 'env_value1'
        os.environ['PARAM2'] = 'env_value2'
        config = load_config(priority='env', load_from_env='all', load_from_file='all')
        m.assert_called_once_with('config.json')
        assert config['param1'] == 'env_value1'
        assert config['param2'] == 'env_value2'

def test_priority_file():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PARAM1'] = 'env_value1'
        os.environ['PARAM2'] = 'env_value2'
        config = load_config(priority='file', load_from_env='all', load_from_file='all')
        m.assert_called_once_with('config.json')
        assert config['param1'] == 'file_value1'
        assert config['param2'] == 'file_value2'

def test_required_param():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        config = load_config(required_config_params=['param1', 'param2'], ignore_missing_file=True, priority='file') # pragma: no cover
        m.assert_called_once_with('config.json')
        assert config['param1'] == 'file_value1'
        assert config['param2'] == 'file_value2'

def test_missing_required_param():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        with pytest.raises(SystemExit) as e:
            load_config(required_config_params=['param1', 'param2', 'param3'], ignore_missing_file=True) # pragma: no cover
        assert str(e.value) == "1"  # exit code

def test_invalid_priority():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        with pytest.raises(ValueError) as e:
            load_config(priority='invalid') # pragma: no cover
        assert str(e.value) == "priority must be 'env' or 'file'"

def test_config_env_prefix_with_env_priority():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PREFIX_PARAM1'] = 'env_value1'
        os.environ['PREFIX_PARAM2'] = 'env_value2'
        config = load_config(priority='env', load_from_env='all', load_from_file='all', config_env_prefix='PREFIX_')
        m.assert_called_once_with('config.json')
        assert config['param1'] == 'env_value1'
        assert config['param2'] == 'env_value2'

def test_config_env_prefix_with_file_priority():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PREFIX_PARAM1'] = 'env_value1'
        os.environ['PREFIX_PARAM2'] = 'env_value2'
        config = load_config(priority='file', load_from_env='all', load_from_file='all', config_env_prefix='PREFIX_')
        m.assert_called_once_with('config.json')
        assert config['param1'] == 'file_value1'
        assert config['param2'] == 'file_value2'

def test_invalid_load_from_env():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        with pytest.raises(ValueError) as e:
            load_config(load_from_env='invalid') # pragma: no cover
        assert str(e.value) == "load_from_env must be 'required', 'all', or a list of environment variable names"

def test_invalid_load_from_file():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        with pytest.raises(ValueError) as e:
            load_config(load_from_file='invalid') # pragma: no cover
        assert str(e.value) == "load_from_file must be 'required', 'all', or a list of config file keys"

def test_load_from_env_required():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PARAM3'] = 'env_value1'
        os.environ['PARAM4'] = 'env_value2'
        config = load_config(load_from_env='required', load_from_file='all', required_config_params=['param3', 'param4'])
        m.assert_called_once_with('config.json')
        assert config['param3'] == 'env_value1'
        assert config['param4'] == 'env_value2'

def test_load_from_env_list():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PARAM3'] = 'env_value1'
        os.environ['PARAM4'] = 'env_value2'
        config = load_config(load_from_env=['param3'], load_from_file='all')
        m.assert_called_once_with('config.json')
        assert config['param3'] == 'env_value1'

def test_load_from_env_list_with_prefix():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        os.environ['PREFIX_PARAM3'] = 'env_value1'
        os.environ['PREFIX_PARAM4'] = 'env_value2'
        config = load_config(load_from_env=['param3', 'param4'], load_from_file='all', config_env_prefix='PREFIX_')
        m.assert_called_once_with('config.json')
        assert config['param3'] == 'env_value1'
        assert config['param4'] == 'env_value2'

def test_load_from_env_list_not_present():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        config = load_config(load_from_env=['param3_not_present'], load_from_file='all')
        m.assert_called_once_with('config.json')
        assert config.get('param3_not_present') is None

def test_load_from_file_list_not_present():
    mock_json = '{"param1": "file_value1", "param2": "file_value2"}'
    with patch('builtins.open', mock_open(read_data=mock_json), create=True) as m:
        config = load_config(load_from_env='all', load_from_file=['param4_not_present'])
        m.assert_called_once_with('config.json')
        assert config.get('param3_not_present') is None
