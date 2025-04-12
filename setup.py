from setuptools import setup, find_packages

setup(
    name="fonteco",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "scipy",
        "Pillow",
        "fontTools",
        "opencv-python",
        "potrace",
    ],
    python_requires=">=3.6",
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    package_data={
        "fonteco": ["fonts/*.ttf"],
    },
) 