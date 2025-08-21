import json

import requests
from fastmcp import FastMCP

mcp = FastMCP(name="PyPiPackageScanner")

OSV_URL = "https://api.osv.dev/v1/query"


@mcp.tool
def scan_pypi_package(package_name: str, package_version: str) -> str:
    data = {"version": package_version, "package": {"name": package_name, "ecosystem": "PyPI"}}

    response = requests.post(OSV_URL, json=data)

    return json.dumps(response.json())


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=9000)
