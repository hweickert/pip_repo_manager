import setuptools



setuptools.setup(
    name="pip_repo_manager",
    packages=setuptools.find_packages(),
    version="1.0.4",
    install_requires=[
        "mock==2.0.0",
        "colorama==0.3.3"
    ]
)
