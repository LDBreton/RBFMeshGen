from setuptools import setup, find_packages

setup(
    name="RBFMeshGen",
    version="1.1.4",
    author="Louis Breton",
    author_email="louis.breton@ciencias.unam.mx",
    description="RBFMeshGen has moved to RBFLAB; legacy 2D point-cloud generation.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LDBreton/RBFMeshGen",
    project_urls={"Successor": "https://pypi.org/project/rbflab/",
                  "RBFLAB documentation": "https://ldbreton.github.io/RBFLAB/"},
    packages=find_packages(),
    install_requires=[
        'numpy',        # For numerical operations
        'matplotlib>=3.6',   # Colormap registry and resampling APIs
        'shapely>=2.0',      # prepare and contains_properly APIs
        'scipy>=1.9'         # Halton and Sobol sampling
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
