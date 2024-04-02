from setuptools import setup

setup(
    name="PostsRepo",
    version="1.0",
    packages=[
        "app",
        "app.utils",
        "app.config",
        "app.models",
        "app.schema",
        "app.services",
        "app.controllers",
        "app.repositories",
    ],
    url="https://www.vibeosys.com",
    license="Vibeosys Software",
    author="anandvb",
    author_email="info@vibeosys.com",
    description="Posts sample python project",
)
