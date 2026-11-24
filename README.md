# KAVACHAM – Dependency Vulnerability Scanner

## Overview

KAVACHAM is a security-focused project in the Cybersecurity and Application Security domain. It identifies vulnerable dependencies in software repositories, analyses security risks, and aims to automate vulnerability remediation using an OpenAI-powered AI agent.

## Key Features

- Automated dependency extraction from software repositories.
- Vulnerability detection using the OSV (Open Source Vulnerabilities) API.
- Identification of vulnerable and safe dependencies.
- Grouping and analysis of vulnerability advisories.
- Interactive security dashboard displaying scan results.
- Planned AI-powered vulnerability remediation and automated dependency updates.

## Supported Languages

| Language | Dependency ecosystem | Status |
|---|---|---|
| Python | requirements.txt | Implemented |
| JavaScript / Node.js | package-lock.json | Implemented |
| Java | Maven / Gradle | Under development |
| C++ | vcpkg / Conan | Under development |

## Project Architecture

```text
KAVACHAM/
│
├── backend/
│   ├── app.py
│   │
│   └── scanner/
│       ├── repository_manager.py
│       ├── dependency_extractor.py
│       └── vulnerability_checker.py
│
├── frontend/
│   └── Dashboard files
│
├── scan_report.json
├── README.md
└── .gitignore
```

## How It Works

1. User provides a software repository URL.
2. KAVACHAM clones the repository.
3. The dependency extractor identifies supported dependency manifests.
4. Dependencies and their versions are extracted.
5. The vulnerability checker queries the OSV API.
6. Vulnerability findings are grouped and analysed.
7. Results are displayed on the dashboard.

## Contribution: Extending Language Support

KAVACHAM is designed to support multiple programming languages.

Contributors can extend the existing scanner by implementing dependency extraction for additional ecosystems.

### Java Support
- Maven: `pom.xml`
- Gradle: `build.gradle` and `build.gradle.kts`
- Gradle dependency lockfiles, where available.

### C++ Support
- vcpkg: `vcpkg.json` and supported lockfiles.
- Conan: `conanfile.txt`, `conanfile.py`, and supported lockfiles.

### Contribution Guidelines

Every language integration should:

1. Identify supported dependency manifest files.
2. Extract package names and exact versions wherever available.
3. Map dependencies to the correct OSV ecosystem.
4. Pass extracted dependencies to the existing vulnerability checker.
5. Preserve the existing JSON report structure.
6. Handle missing versions and parsing errors safely.
7. Include test cases using sample dependency manifests.

**Important:** Do not create separate vulnerability-checking engines for each language. Reuse the existing OSV vulnerability checker.

## Technology Stack

- Python
- Flask
- HTML, CSS and JavaScript
- OSV API
- Git and GitHub

## Future Scope

- AI-powered automated vulnerability remediation.
- Dependency version recommendations and updates.
- Automated testing and rescanning after remediation.
- Pull request generation for proposed fixes.
- Extended support for additional programming languages.

## Project Domain

Cybersecurity | Application Security | Software Supply Chain Security | AI-powered Security Automation
