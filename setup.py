import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = [
    "PyYAML",
    "toml",
    "Werkzeug",
    "pytest"
]

setuptools.setup(
    name="pytest-exception-script",  # Replace with your own username
    version="0.1.0",
    author="qporest",
    author_email="ihor.husar@gmail.com",
    description="Walk your code through exception script to check it's resiliency to failures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qporest/pytest-exception-script",
    packages=setuptools.find_packages(),
    install_requires=dependencies,
    tests_require=dependencies,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    entry_points={"pytest11": ["chaos_test = chaos_test.hooks"]},
)
