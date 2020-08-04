import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spinal-tap", # Replace with your own username
    version="0.0.1",
    author="qporest",
    author_email="ihor.husar@gmail.com",
    description="Inject your code with failures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Pytest"
    ],
    entry_points={"pytest11": ["chaos_test = chaos_test.hooks"]},
)
