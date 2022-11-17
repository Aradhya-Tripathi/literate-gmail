from setuptools import setup, find_packages

with open("./requirements.txt", "r") as req:
    requirements = req.read().strip().split("\n")

setup(
    name="googleatclient",
    author_email="aradhyatripathi51@gmail.com",
    version="0.1.0",
    packages=find_packages(),
    license="MIT",
    install_requires=requirements,
)
