
import json
import os
import re


def normalize_pypi_name(name):
    """Normalize Python package names according to PyPI conventions."""
    return re.sub(r"[-_.]+", "-", name).lower()


def extract_dependencies(file_path):
    """Extract exact-version dependencies from requirements.txt."""
    dependencies = []
    seen = set()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Ignore pip options, URLs and editable installs.
            if line.startswith(("-", "http://", "https://")):
                continue

            # Remove inline comments.
            line = line.split("#", 1)[0].strip()

            # Remove environment markers.
            line = line.split(";", 1)[0].strip()

            # Match exact-version requirements, including optional extras.
            match = re.match(
                r"^([A-Za-z0-9][A-Za-z0-9._-]*)"
                r"(?:\[[^\]]+\])?\s*==\s*([^\s]+)$",
                line
            )

            if not match:
                continue

            name = normalize_pypi_name(match.group(1))
            version = match.group(2).strip()

            if not name or not version:
                continue

            key = (name, version, "PyPI")

            if key not in seen:
                dependencies.append({
                    "name": name,
                    "version": version,
                    "ecosystem": "PyPI"
                })
                seen.add(key)

    return dependencies


def extract_npm_dependencies(file_path):
    """Extract dependencies from npm package-lock v1, v2 and v3."""
    dependencies = []
    seen = set()

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    def add_dependency(name, details):
        version = details.get("version")

        if not name or not version:
            return

        key = (name, version, "npm")

        if key not in seen:
            dependencies.append({
                "name": name,
                "version": version,
                "ecosystem": "npm"
            })
            seen.add(key)

    # package-lock v2 and v3
    packages = data.get("packages", {})

    if packages:
        for package_path, details in packages.items():

            if not package_path or "node_modules/" not in package_path:
                continue

            # Handle nested node_modules correctly.
            name = package_path.rsplit("node_modules/", 1)[-1]

            add_dependency(name, details)

    # package-lock v1
    else:
        def process_dependencies(package_dependencies):
            for name, details in package_dependencies.items():

                add_dependency(name, details)

                nested = details.get("dependencies", {})

                if nested:
                    process_dependencies(nested)

        process_dependencies(data.get("dependencies", {}))

    return dependencies


if __name__ == "__main__":
    print("Testing dependency extractor...")

    python_file = "backend/scanner/sample_requirements.txt"
    npm_file = "sample_node/package-lock.json"

    if os.path.exists(python_file):
        python_deps = extract_dependencies(python_file)
        print("\nPython dependencies:")
        for dependency in python_deps:
            print(dependency)

    if os.path.exists(npm_file):
        npm_deps = extract_npm_dependencies(npm_file)
        print("\nJavaScript dependencies:")
        for dependency in npm_deps:
            print(dependency)
