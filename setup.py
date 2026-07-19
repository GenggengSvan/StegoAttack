from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
README = ROOT / "README.md"


setup(
    name="StegoAttack",
    version="0.1",
    description="Research pipeline and CLI for the StegoAttack paper implementation.",
    long_description=README.read_text(encoding="utf-8") if README.exists() else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["stego_cli"],
    include_package_data=True,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "stego-attack=stego_cli:main",
        ],
    },
)
