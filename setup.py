from setuptools import setup, find_packages

setup(
    name="RBFMeshGen",
    version="1.0.2",
    author="Louis Breton",
    author_email="louis.breton@ciencias.unam.mx",
    description="A Python package for generating random meshes based on radial basis functions.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LDBreton/RBFMeshGen",
    packages=find_packages(),
    install_requires=[
        'numpy',        # For numerical operations
        'matplotlib',   # For any plotting capabilities
        'shapely'       # Shapely for geometrical operations
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
