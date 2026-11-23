
import os
import json
import tempfile
import subprocess

from pathlib import Path
from urllib.parse import urlparse

from dependency_extractor import (
    extract_dependencies,
    extract_npm_dependencies
)

from vulnerability_checker import scan_dependencies


# KAVACHAM project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Location where the scan report will be saved
REPORT_PATH = PROJECT_ROOT / "scan_report.json"


def validate_repository_url(repo_url):
    """Validate that the URL points to a public GitHub repository."""

    parsed_url = urlparse(repo_url)

    if parsed_url.scheme not in ("https", "http"):
        raise ValueError("Repository URL must use HTTP or HTTPS.")

    if parsed_url.hostname != "github.com":
        raise ValueError("Only GitHub repositories are supported.")

    if parsed_url.username or parsed_url.password:
        raise ValueError("Repository URL must not contain credentials.")

    path_parts = [
        part for part in parsed_url.path.strip("/").split("/")
        if part
    ]

    if len(path_parts) != 2:
        raise ValueError("Invalid GitHub repository URL.")

    owner, repository = path_parts

    if not owner or not repository:
        raise ValueError("Invalid GitHub repository URL.")

    return f"https://github.com/{owner}/{repository}"


def clone_repository(repo_url):
    """Clone a GitHub repository into a temporary directory."""

    repo_url = validate_repository_url(repo_url)

    workspace = tempfile.mkdtemp(prefix="kavacham_")

    repo_path = os.path.join(workspace, "repository")

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                repo_url,
                repo_path
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        print("\nRepository cloned successfully!")

        return workspace, repo_path

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"Repository cloning failed: {error.stderr.strip()}"
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError("Repository cloning timed out.")

    except Exception:
        # Remove the temporary directory if cloning fails.
        import shutil
        shutil.rmtree(workspace, ignore_errors=True)
        raise


def find_dependency_files(repo_path):
    """Find supported dependency files recursively."""

    dependency_files = []

    ignored_directories = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "build",
        "dist"
    }

    supported_files = {
        "requirements.txt",
        "package-lock.json"
    }

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in ignored_directories
        ]

        for filename in files:

            if filename in supported_files:

                full_path = os.path.join(root, filename)

                dependency_files.append(full_path)

    return dependency_files


def extract_repository_dependencies(dependency_files):
    """Extract dependencies from all supported files."""

    all_dependencies = []

    for file_path in dependency_files:

        print(f"\nProcessing: {file_path}")

        filename = os.path.basename(file_path)

        if filename == "requirements.txt":

            dependencies = extract_dependencies(file_path)

        elif filename == "package-lock.json":

            dependencies = extract_npm_dependencies(file_path)

        else:
            continue

        all_dependencies.extend(dependencies)

    # Remove duplicate package/version/ecosystem entries.
    unique_dependencies = {
        (
            dependency["name"],
            dependency["version"],
            dependency["ecosystem"]
        ): dependency
        for dependency in all_dependencies
    }

    return list(unique_dependencies.values())


def save_scan_report(scan_report):
    """Save the structured scan report as a JSON file."""

    with open(REPORT_PATH, "w", encoding="utf-8") as file:

        json.dump(
            scan_report,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== REPORT SAVED ==========")
    print(f"Report location: {REPORT_PATH}")


def process_repository(repo_url):
    """Complete repository scanning workflow."""

    workspace = None

    try:
        # Step 1: Clone repository.
        print("\n========== KAVACHAM REPOSITORY SCANNER ==========")

        workspace, repo_path = clone_repository(repo_url)

        # Step 2: Find dependency files.
        print("\nSearching for dependency files...")

        dependency_files = find_dependency_files(repo_path)

        if not dependency_files:
            print("No supported dependency files found.")

            return None

        # Step 3: Extract dependencies.
        all_dependencies = extract_repository_dependencies(
            dependency_files
        )

        print("\n========== DEPENDENCY EXTRACTION ==========")

        for dependency in all_dependencies:
            print(dependency)

        print(
            f"\nTotal dependencies extracted: "
            f"{len(all_dependencies)}"
        )

        if not all_dependencies:
            print("No dependencies available to scan.")
            return None

        # Step 4: Scan dependencies.
        print("\n========== STARTING VULNERABILITY SCAN ==========")

        scan_report = scan_dependencies(all_dependencies)

        # Step 5: Save structured report.
        save_scan_report(scan_report)

        print("\n========== KAVACHAM SCAN FINISHED ==========")

        return scan_report

    finally:
        # Step 6: Remove temporary cloned repository.
        if workspace and os.path.exists(workspace):

            import shutil

            shutil.rmtree(workspace, ignore_errors=True)

            print("\nTemporary repository files cleaned up.")


if __name__ == "__main__":

    # Temporary test repository.
    repo_url = (
        "https://github.com/Ketryx/test-project-python.git"
    )

    try:

        process_repository(repo_url)

    except (ValueError, RuntimeError) as error:

        print(f"\nKAVACHAM ERROR: {error}")

    except Exception as error:

        print(f"\nUNEXPECTED ERROR: {error}")
