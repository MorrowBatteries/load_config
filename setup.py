from setuptools import setup, find_packages
import subprocess

def get_last_commit_datetime():
    return subprocess.check_output(["git", "log", "-1", "--date=format:%Y.%m.%d.%H%M", "--format=%cd"]).strip().decode('utf-8')

setup(
    name='load_config',
    version=get_last_commit_datetime(),
    packages=find_packages(),
    description='A library for loading configuration parameters from environment variables and a JSON file',
    author='Ronny Ager-Wick (Morrow Batteries ASA)',
    author_email='ronny.ager-wick@mmorrowbatteries.com',
    url='https://github.com/MorrowBatteries/load_config'
)