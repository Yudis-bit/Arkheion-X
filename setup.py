from setuptools import setup, find_packages

setup(
    name='arkheionx_quant_engine',
    version='0.1.0',
    packages=find_packages(),
    author='Yudis-bit',
    description='ARKHEION-X Intelligence Agents',
    install_requires=[
        'python-dotenv',
        'web3',
        'requests',
        'streamlit',
        'pandas',
        'plotly',
        'python-telegram-bot'
    ],
)