from setuptools import setup, find_packages

setup(
    name="pdf-merger-tool",
    version="1.0.0",
    author="PDF Merger Tool",
    description="Windows 11対応PDF結合ツール",
    packages=find_packages(),
    install_requires=[
        "customtkinter>=5.2.0",
        "pypdf>=5.6.0",
        "Pillow>=10.0.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "pdf-merger=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)