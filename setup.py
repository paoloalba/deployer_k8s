import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8syaml",
    version="0.1.1",
    author="Paolo Alba",
    author_email="paoloalbag@gmail.com",
    description="Programmatic generation of yaml files for K8s' objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paoloalba/deployer_k8s",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)