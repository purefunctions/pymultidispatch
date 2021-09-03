from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="pymultidispatch",
    version="1.2.0",
    author="Siva Jayaraman",
    author_email="purefunctions.os@outlook.com",
    description="Multimethods implementation in Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/purefunctions/pymultidispatch/",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
