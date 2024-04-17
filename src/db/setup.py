from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "python=^3.8",
    "pymysql=^1.1.0",
    "sqlalchemy=^2.0.27",
    "pandas=^1.5.3",
    "requests=^2.31.0",
]

setup(
    name="FPL Data Ingestion",
    author= "Okeks",
    author_email="freelanceokeks@gmail.com",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
    package_data={"": ["*.json", "*.yaml"]},
)