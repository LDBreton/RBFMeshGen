from setuptools import setup, find_packages

setup(
    name="RBFMeshGen",
    version="1.1.1",
    author="Louis Breton",
    author_email="louis.breton@ciencias.unam.mx",
    description="Generate random 2D point clouds within parametric geometric boundaries.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LDBreton/RBFMeshGen",
    packages=find_packages(),
    install_requires=[
        'numpy',        # For numerical operations
        'matplotlib>=3.6',   # Colormap registry and resampling APIs
        'shapely>=2.0'       # prepare and contains_properly APIs
    ],
    extras_require={'qmc': ['scipy>=1.9']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
