from setuptools import setup, find_packages

setup(
    name="Create-OHLC-Dataset-From-API",
    version="1.0",
    author="Nasir Imran Bukhari",
    author_email="nasir.bukhari86@yahoo.com",
    description="Set of scripts to automate downloading OHLC data from any API endpoint using only the API_CONFIG for new exchanges.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[  
        "dataframe_image==0.2.5",
        "kaggle==1.6.17",
        "matplotlib==3.9.2",
        "pandas==2.2.2",
        "requests==2.32.3",
        "setuptools==75.1.0",
        "typing_extensions==4.12.2", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
    ],
    python_requires=">=3.12",  # Minimum Python version required
)
