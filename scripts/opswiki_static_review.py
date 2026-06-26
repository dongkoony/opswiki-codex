#!/usr/bin/env python3
"""Run local static review checks for Terraform and Kubernetes files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


SEVERITY_BY_RULE = {
    "TF_PUBLIC_INGRESS": "high",
    "TF_WILDCARD_IAM_ACTION": "high",
    "TF_WILDCARD_IAM_RESOURCE": "high",
    "TF_SENSITIVE_OUTPUT": "medium",
    "TF_MISSING_TAGS": "low",
    "K8S_PRIVILEGED_CONTAINER": "high",
    "K8S_HOST_PATH_VOLUME": "high",
    "K8S_HOST_NETWORK": "high",
    "K8S_LATEST_IMAGE_TAG": "medium",
    "K8S_MISSING_RESOURCE_REQUESTS": "medium",
    "K8S_MISSING_RESOURCE_LIMITS": "medium",
    "K8S_MISSING_READINESS_PROBE": "medium",
    "K8S_MISSING_LIVENESS_PROBE": "low",
    "K8S_DEFAULT_NAMESPACE": "low",
    "K8S_SERVICE_SELECTOR_WITHOUT_MATCHING_WORKLOAD": "low",
    "K8S_YAML_PARSE_ERROR": "medium",
}

TAGGABLE_AWS_RESOURCES = {
    "aws_instance",
    "aws_security_group",
    "aws_lb",
    "aws_db_instance",
    "aws_s3_bucket",
    "aws_eks_cluster",
    "aws_lambda_function",
}

SENSITIVE_OUTPUT_TERMS = (
    "secret",
    "token",
    "password",
    "passwd",
    "private_key",
    "credential",
    "credentials",
    "api_key",
)


class ReviewError(Exception):
    """Raised when static review input or output cannot be processed."""


class SourceFile:
    def __init__(self, *, path: str, domain: str, text: str) -> None:
        self.path = path
        self.domain = domain
        self.text = text


class Finding:
    def __init__(
        self,
        *,
        domain: str,
        rule_id: str,
        path: str,
        line: int,
        message: str,
        recommendation: str,
    ) -> None:
        self.domain = domain
        self.rule_id = rule_id
        self.severity = SEVERITY_BY_RULE[rule_id]
        self.path = path
        self.line = line
        self.message = message
        self.recommendation = recommendation


class StaticReviewReport:
    def __init__(
        self,
        *,
        project_name: str,
        input_root: str,
        files_scanned: list[SourceFile],
        findings: list[Finding],
        assumptions: list[str],
        verification_questions: list[str],
    ) -> None:
        self.project_name = project_name
        self.input_root = input_root
        self.files_scanned = files_scanned
        self.findings = findings
        self.assumptions = assumptions
        self.verification_questions = verification_questions


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def make_finding(
    *,
    domain: str,
    rule_id: str,
    path: Path,
    line: int,
    message: str,
    recommendation: str,
) -> Finding:
    return Finding(
        domain=domain,
        rule_id=rule_id,
        path=path.as_posix(),
        line=max(line, 1),
        message=message,
        recommendation=recommendation,
    )


def line_number_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def find_matching_brace(text: str, open_brace_index: int) -> int:
    depth = 0
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(text) - 1


def iter_terraform_resource_blocks(text: str) -> list[tuple[str, str, int]]:
    blocks: list[tuple[str, str, int]] = []
    pattern = re.compile(r'resource\s+"([^"]+)"\s+"[^"]+"\s*\{', re.MULTILINE)
    for match in pattern.finditer(text):
        open_brace = text.find("{", match.start())
        close_brace = find_matching_brace(text, open_brace)
        blocks.append((match.group(1), text[match.start() : close_brace + 1], match.start()))
    return blocks


def iter_terraform_output_blocks(text: str) -> list[tuple[str, str, int]]:
    blocks: list[tuple[str, str, int]] = []
    pattern = re.compile(r'output\s+"([^"]+)"\s*\{', re.MULTILINE)
    for match in pattern.finditer(text):
        open_brace = text.find("{", match.start())
        close_brace = find_matching_brace(text, open_brace)
        blocks.append((match.group(1), text[match.start() : close_brace + 1], match.start()))
    return blocks


def has_tags(block_body: str) -> bool:
    return bool(re.search(r"(?m)^\s*tags\s*(=|\{)", block_body))


def scan_terraform_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []

    public_ingress_match = re.search(
        r"(cidr_blocks|ipv6_cidr_blocks)\s*=\s*\[[^\]]*(0\.0\.0\.0/0|::/0)",
        text,
        re.DOTALL,
    )
    if public_ingress_match:
        findings.append(
            make_finding(
                domain="terraform",
                rule_id="TF_PUBLIC_INGRESS",
                path=path,
                line=line_number_at(text, public_ingress_match.start()),
                message="Public ingress CIDR was found in Terraform text.",
                recommendation="Confirm this is intentionally public and restrict CIDR ranges where possible.",
            )
        )

    wildcard_action_match = re.search(r'"Action"\s*:\s*"[^"]*\*[^"]*"', text)
    if wildcard_action_match:
        findings.append(
            make_finding(
                domain="terraform",
                rule_id="TF_WILDCARD_IAM_ACTION",
                path=path,
                line=line_number_at(text, wildcard_action_match.start()),
                message="Wildcard IAM action was found in Terraform text.",
                recommendation="Scope IAM actions to the smallest required action set.",
            )
        )

    wildcard_resource_match = re.search(r'"Resource"\s*:\s*"\*"', text)
    if wildcard_resource_match:
        findings.append(
            make_finding(
                domain="terraform",
                rule_id="TF_WILDCARD_IAM_RESOURCE",
                path=path,
                line=line_number_at(text, wildcard_resource_match.start()),
                message="Wildcard IAM resource was found in Terraform text.",
                recommendation="Scope IAM resources to specific ARNs or document the exception.",
            )
        )

    for output_name, output_body, offset in iter_terraform_output_blocks(text):
        lowered_name = output_name.lower()
        if any(term in lowered_name for term in SENSITIVE_OUTPUT_TERMS) and not re.search(
            r"(?m)^\s*sensitive\s*=\s*true\b", output_body
        ):
            findings.append(
                make_finding(
                    domain="terraform",
                    rule_id="TF_SENSITIVE_OUTPUT",
                    path=path,
                    line=line_number_at(text, offset),
                    message=f"Sensitive-looking output `{output_name}` is not marked sensitive.",
                    recommendation="Add `sensitive = true` or confirm the output cannot expose secret material.",
                )
            )

    for resource_type, resource_body, offset in iter_terraform_resource_blocks(text):
        if resource_type in TAGGABLE_AWS_RESOURCES and not has_tags(resource_body):
            findings.append(
                make_finding(
                    domain="terraform",
                    rule_id="TF_MISSING_TAGS",
                    path=path,
                    line=line_number_at(text, offset),
                    message=f"No tags were found in this `{resource_type}` resource block.",
                    recommendation=(
                        "Confirm ownership, service, environment, and cost tags are provided "
                        "here or through provider defaults."
                    ),
                )
            )

    return findings


WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "Pod"}


def import_yaml():
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise ReviewError(
            "PyYAML is required for Kubernetes scanning. Run with `uv run --with pyyaml python ...`."
        ) from exc
    return yaml


def as_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    return {}


def as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    return []


def image_has_latest_or_missing_tag(image: str) -> bool:
    if "@sha256:" in image:
        return False
    image_name = image.rsplit("/", 1)[-1]
    if ":" not in image_name:
        return True
    return image_name.rsplit(":", 1)[-1] == "latest"


def labels_match(selector: dict[str, object], labels: dict[str, object]) -> bool:
    return all(labels.get(key) == value for key, value in selector.items())


def containers_from_document(document: dict[str, object]) -> list[dict[str, object]]:
    kind = document.get("kind")
    if kind == "Pod":
        pod_spec = as_dict(document.get("spec"))
    else:
        spec = as_dict(document.get("spec"))
        template = as_dict(spec.get("template"))
        pod_spec = as_dict(template.get("spec"))

    containers = [
        container
        for container in as_list(pod_spec.get("containers"))
        if isinstance(container, dict)
    ]
    init_containers = [
        container
        for container in as_list(pod_spec.get("initContainers"))
        if isinstance(container, dict)
    ]
    return containers + init_containers


def pod_spec_from_document(document: dict[str, object]) -> dict[str, object]:
    if document.get("kind") == "Pod":
        return as_dict(document.get("spec"))
    spec = as_dict(document.get("spec"))
    template = as_dict(spec.get("template"))
    return as_dict(template.get("spec"))


def workload_labels_from_document(document: dict[str, object]) -> dict[str, object]:
    if document.get("kind") == "Pod":
        metadata = as_dict(document.get("metadata"))
        return as_dict(metadata.get("labels"))
    spec = as_dict(document.get("spec"))
    template = as_dict(spec.get("template"))
    metadata = as_dict(template.get("metadata"))
    return as_dict(metadata.get("labels"))


def document_namespace(document: dict[str, object]) -> str | None:
    namespace = as_dict(document.get("metadata")).get("namespace")
    if isinstance(namespace, str) and namespace.strip():
        return namespace
    return None


def container_name(container: dict[str, object]) -> str:
    name = container.get("name")
    if isinstance(name, str) and name:
        return name
    return "unnamed"


def scan_kubernetes_workload(path: Path, document: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    pod_spec = pod_spec_from_document(document)

    if pod_spec.get("hostNetwork") is True:
        findings.append(
            make_finding(
                domain="kubernetes",
                rule_id="K8S_HOST_NETWORK",
                path=path,
                line=1,
                message="Workload uses hostNetwork in scanned files.",
                recommendation="Confirm host networking is required and document network isolation controls.",
            )
        )

    for volume in as_list(pod_spec.get("volumes")):
        if isinstance(volume, dict) and "hostPath" in volume:
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_HOST_PATH_VOLUME",
                    path=path,
                    line=1,
                    message="Workload mounts a hostPath volume in scanned files.",
                    recommendation="Prefer non-hostPath storage or document the node filesystem access requirement.",
                )
            )
            break

    if document_namespace(document) is None:
        findings.append(
            make_finding(
                domain="kubernetes",
                rule_id="K8S_DEFAULT_NAMESPACE",
                path=path,
                line=1,
                message="Workload manifest does not set metadata.namespace in scanned files.",
                recommendation="Confirm namespace is set by deployment tooling or add it explicitly.",
            )
        )

    for container in containers_from_document(document):
        name = container_name(container)
        image = container.get("image")
        if isinstance(image, str) and image_has_latest_or_missing_tag(image):
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_LATEST_IMAGE_TAG",
                    path=path,
                    line=1,
                    message=f"Container `{name}` uses a mutable or missing image tag in scanned files.",
                    recommendation="Pin images to an immutable digest or explicit non-latest tag.",
                )
            )

        resources = as_dict(container.get("resources"))
        requests = as_dict(resources.get("requests"))
        limits = as_dict(resources.get("limits"))
        if not requests.get("cpu") or not requests.get("memory"):
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_MISSING_RESOURCE_REQUESTS",
                    path=path,
                    line=1,
                    message=f"Container `{name}` is missing CPU or memory requests in scanned files.",
                    recommendation="Set CPU and memory requests based on expected steady-state usage.",
                )
            )
        if not limits.get("cpu") or not limits.get("memory"):
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_MISSING_RESOURCE_LIMITS",
                    path=path,
                    line=1,
                    message=f"Container `{name}` is missing CPU or memory limits in scanned files.",
                    recommendation="Set CPU and memory limits or document why limits are intentionally omitted.",
                )
            )

        if "readinessProbe" not in container:
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_MISSING_READINESS_PROBE",
                    path=path,
                    line=1,
                    message=f"Container `{name}` is missing a readiness probe in scanned files.",
                    recommendation="Add a readiness probe so traffic is sent only after the workload is ready.",
                )
            )
        if "livenessProbe" not in container:
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_MISSING_LIVENESS_PROBE",
                    path=path,
                    line=1,
                    message=f"Container `{name}` is missing a liveness probe in scanned files.",
                    recommendation="Add a liveness probe when restart-based recovery is appropriate.",
                )
            )

        security_context = as_dict(container.get("securityContext"))
        if security_context.get("privileged") is True:
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_PRIVILEGED_CONTAINER",
                    path=path,
                    line=1,
                    message=f"Container `{name}` runs privileged in scanned files.",
                    recommendation="Avoid privileged containers or document the isolation exception and compensating controls.",
                )
            )

    return findings


def scan_kubernetes_service_selectors(
    path: Path,
    documents: list[dict[str, object]],
) -> list[Finding]:
    workload_labels = [
        workload_labels_from_document(document)
        for document in documents
        if document.get("kind") in WORKLOAD_KINDS
    ]
    findings: list[Finding] = []

    for document in documents:
        if document.get("kind") != "Service":
            continue
        selector = as_dict(as_dict(document.get("spec")).get("selector"))
        if not selector:
            continue
        if not any(labels_match(selector, labels) for labels in workload_labels):
            findings.append(
                make_finding(
                    domain="kubernetes",
                    rule_id="K8S_SERVICE_SELECTOR_WITHOUT_MATCHING_WORKLOAD",
                    path=path,
                    line=1,
                    message="No matching workload labels were found in scanned files for this Service selector.",
                    recommendation=(
                        "Confirm the matching workload is included in the review input or generated by deployment tooling."
                    ),
                )
            )

    return findings


def scan_kubernetes_documents(
    path: Path,
    documents: list[dict[str, object]],
) -> list[Finding]:
    findings: list[Finding] = []

    for document in documents:
        if document.get("kind") in WORKLOAD_KINDS:
            findings.extend(scan_kubernetes_workload(path, document))

    findings.extend(scan_kubernetes_service_selectors(path, documents))
    return findings


def scan_kubernetes_text(path: Path, text: str) -> list[Finding]:
    yaml = import_yaml()
    try:
        loaded_documents = list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else 1
        return [
            make_finding(
                domain="kubernetes",
                rule_id="K8S_YAML_PARSE_ERROR",
                path=path,
                line=line,
                message="Kubernetes YAML could not be parsed for static review.",
                recommendation="Fix YAML syntax before relying on static review results.",
            )
        ]

    documents = [
        document
        for document in loaded_documents
        if isinstance(document, dict)
    ]
    return scan_kubernetes_documents(path, documents)


TERRAFORM_EXTENSIONS = {".tf", ".tfvars"}
KUBERNETES_EXTENSIONS = {".yaml", ".yml"}


def normalize_focus(focus: str) -> str:
    normalized = focus.lower()
    if normalized not in {"all", "terraform", "kubernetes"}:
        raise ReviewError("Focus must be one of: all, terraform, kubernetes.")
    return normalized


def domain_for_path(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in TERRAFORM_EXTENSIONS:
        return "terraform"
    if suffix in KUBERNETES_EXTENSIONS:
        return "kubernetes"
    return None


def discover_source_files(input_root: Path, focus: str) -> list[Path]:
    supported: list[Path] = []
    for path in input_root.rglob("*"):
        if not path.is_file():
            continue
        domain = domain_for_path(path)
        if domain is None:
            continue
        if focus != "all" and domain != focus:
            continue
        supported.append(path)
    return sorted(supported, key=lambda item: item.relative_to(input_root).as_posix().lower())


def load_source_files(input_root: Path, focus: str) -> list[SourceFile]:
    if not input_root.exists():
        raise ReviewError(f"Input path '{input_root}' does not exist.")
    if not input_root.is_dir():
        raise ReviewError(f"Input path '{input_root}' is not a directory.")

    paths = discover_source_files(input_root, focus)
    if not paths:
        raise ReviewError(f"No supported files found in '{input_root}'.")

    sources: list[SourceFile] = []
    for path in paths:
        relative_path = path.relative_to(input_root)
        domain = domain_for_path(path)
        if domain is None:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ReviewError(f"Input file '{relative_path}' is not valid UTF-8.") from exc
        sources.append(SourceFile(path=relative_path.as_posix(), domain=domain, text=text))
    return sources


def build_assumptions(focus: str) -> list[str]:
    assumptions = [
        "Static review does not execute commands, connect to external services, or inspect live infrastructure.",
    ]
    if focus in {"all", "terraform"}:
        assumptions.append("Terraform review does not evaluate modules, variables, provider schemas, or plan output.")
    if focus in {"all", "kubernetes"}:
        assumptions.append("Kubernetes review does not contact an API server or validate manifests against a live cluster.")
    return assumptions


def build_verification_questions(focus: str) -> list[str]:
    questions = [
        "Commands are documentation only; do not execute them from this generated report.",
    ]
    if focus in {"all", "terraform"}:
        questions.extend(
            [
                "Run `terraform validate` or `tofu validate` in the relevant module.",
                "Review `terraform plan` for replacements, public exposure, and IAM blast radius.",
            ]
        )
    if focus in {"all", "kubernetes"}:
        questions.append("Validate Kubernetes manifests with the repository's normal manifest tooling before deploy.")
    return questions


def run_static_review(input_root: Path, project_name: str | None, focus: str) -> StaticReviewReport:
    normalized_focus = normalize_focus(focus)
    sources = load_source_files(input_root, normalized_focus)
    findings: list[Finding] = []

    for source in sources:
        path = Path(source.path)
        if source.domain == "terraform":
            findings.extend(scan_terraform_text(path, source.text))
        elif source.domain == "kubernetes":
            findings.extend(scan_kubernetes_text(path, source.text))

    resolved_project_name = project_name or input_root.name
    return StaticReviewReport(
        project_name=resolved_project_name,
        input_root=input_root.as_posix(),
        files_scanned=sources,
        findings=findings,
        assumptions=build_assumptions(normalized_focus),
        verification_questions=build_verification_questions(normalized_focus),
    )


def count_findings(report: StaticReviewReport, domain: str) -> int:
    return sum(1 for finding in report.findings if finding.domain == domain)


def render_report(report: StaticReviewReport) -> str:
    lines = [
        f"# Static Review: {report.project_name}",
        "",
        "## Summary",
        "",
        f"- Files scanned: {len(report.files_scanned)}",
        f"- Findings: {len(report.findings)}",
        f"- Terraform findings: {count_findings(report, 'terraform')}",
        f"- Kubernetes findings: {count_findings(report, 'kubernetes')}",
        "",
        "## Findings",
        "",
    ]

    if report.findings:
        for finding in sorted(
            report.findings,
            key=lambda item: (item.domain, item.path, item.line, item.rule_id),
        ):
            lines.append(
                f"- [{finding.severity}] {finding.domain} "
                f"`{finding.path}:{finding.line}` {finding.rule_id} - {finding.message}"
            )
            lines.append(f"  Recommendation: {finding.recommendation}")
    else:
        lines.append("- No findings from local static review.")

    lines.extend(["", "## Assumptions", ""])
    lines.extend(f"- {assumption}" for assumption in report.assumptions)
    lines.extend(["", "## Verification Questions", ""])
    lines.extend(f"- {question}" for question in report.verification_questions)
    return "\n".join(lines) + "\n"


def generate_static_review(
    input_root: Path,
    output_path: Path,
    project_name: str | None,
    focus: str,
) -> Path:
    if output_path.exists() and output_path.is_dir():
        raise ReviewError(f"Output path '{output_path}' exists as a directory.")
    report = run_static_review(input_root=input_root, project_name=project_name, focus=focus)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(report), encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local static review checks for Terraform and Kubernetes files."
    )
    parser.add_argument("--input", required=True, help="Input directory containing Terraform or Kubernetes files.")
    parser.add_argument("--output", required=True, help="Output Markdown report path.")
    parser.add_argument("--project-name", help="Project name for the report title.")
    parser.add_argument(
        "--focus",
        default="all",
        choices=["all", "terraform", "kubernetes"],
        help="Limit review to Terraform, Kubernetes, or both.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output_path = generate_static_review(
            input_root=Path(args.input),
            output_path=Path(args.output),
            project_name=args.project_name,
            focus=args.focus,
        )
    except ReviewError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
