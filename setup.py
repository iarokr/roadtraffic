from setuptools import setup, find_packages

with open("README.md") as readme_file:
    README = readme_file.read()

setup_args = dict(
    name="roadtraffic",
    version="0.0.1",
    description="A python package for the fundamental diagram of \
        traffic flow estimation.",
    python_requires=">=3.8, <4",
    long_description_content_type="text/markdown",
    long_description=README,
    license="GPLv3",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    author="Iaroslav Kriuchkov",
    author_email="iaroslav.kriuchkov@aalto.fi",
    keywords=["road traffic", "fundamental diagram"],
    url="https://github.com/iarokr/roadtraffic",
    download_url="https://pypi.org/project/roadtraffic/",
    zip_safe=False,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)

install_requires = [
    "pystoned>=0.5.8",
    "pandas>=1.5.2",
    "numpy>=1.24.0",
    "scikit-learn>=1.1.3",
    "scipy>=1.9.3",
    "matplotlib>=3.6.2",
    "requests>=2.28.1",
    "datetime>=4.9",
]

if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires)
