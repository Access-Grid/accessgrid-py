import re
from pathlib import Path

import pytest

# ══════════════════════════════════════════════════════════════════════════════
# TARGET VERSION - Update this when upgrading Python
# ══════════════════════════════════════════════════════════════════════════════
TARGET_PYTHON = "3.12.13"

ROOT = Path(__file__).resolve().parent.parent


def read_tool_versions():
    content = (ROOT / ".tool-versions").read_text()
    versions = {}
    for line in content.strip().splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            versions[parts[0]] = parts[1]
    return versions


def read_ci_jobs():
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    content = ci_path.read_text()

    jobs = {}
    # Split into job blocks by top-level job keys (2-space indent)
    job_blocks = re.split(r"\n  (?=\w[\w-]*:)", content)

    for block in job_blocks:
        name_match = re.match(r"^([\w-]+):", block)
        if not name_match:
            continue
        job_name = name_match.group(1)

        versions = []

        # Matrix arrays: python: ['3.10', '3.12', '3.13']
        matrix_match = re.search(r"python:\s*\[([^\]]+)\]", block)
        if matrix_match:
            for v in matrix_match.group(1).split(","):
                versions.append(v.strip().strip("'\""))

        # Standalone: python-version: '3.12'
        for m in re.finditer(r"python-version:\s*['\"]?([\d.]+)['\"]?", block):
            if m.group(1) not in versions:
                versions.append(m.group(1))

        if versions:
            jobs[job_name] = versions

    return jobs


def major_minor(version):
    parts = version.split(".")
    return f"{parts[0]}.{parts[1]}"


class TestToolVersions:
    def test_python_version_matches_target(self):
        tool_versions = read_tool_versions()
        assert tool_versions["python"] == TARGET_PYTHON


class TestCIWorkflow:
    @pytest.fixture(scope="class")
    def jobs(self):
        return read_ci_jobs()

    def test_every_job_includes_target_minor(self, jobs):
        target_minor = major_minor(TARGET_PYTHON)
        for job_name, versions in jobs.items():
            assert target_minor in versions, (
                f"Job '{job_name}' is missing target "
                f"version {target_minor}: {versions}"
            )

    def test_every_version_is_valid_format(self, jobs):
        for job_name, versions in jobs.items():
            for v in versions:
                assert re.match(r"^\d+\.\d+$", v), (
                    f"Job '{job_name}' has invalid " f"version format: {v}"
                )

    def test_tool_versions_minor_in_every_job(self, jobs):
        tool_minor = major_minor(read_tool_versions()["python"])
        for job_name, versions in jobs.items():
            assert tool_minor in versions, (
                f"Job '{job_name}' doesn't test "
                f".tool-versions minor {tool_minor}: {versions}"
            )
