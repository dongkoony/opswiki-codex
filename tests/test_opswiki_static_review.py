import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "opswiki_static_review.py"


def load_reviewer():
    spec = importlib.util.spec_from_file_location("opswiki_static_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TerraformScannerTests(unittest.TestCase):
    def test_scan_terraform_flags_public_ingress_wildcard_iam_sensitive_output_and_missing_tags(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_terraform_text(
            Path("terraform/main.tf"),
            '''
resource "aws_security_group" "web" {
  name = "web"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_policy" "wide" {
  policy = <<POLICY
{
  "Statement": [{
    "Action": "*",
    "Resource": "*",
    "Effect": "Allow"
  }]
}
POLICY
}

output "db_password" {
  value = aws_db_instance.main.password
}
''',
        )

        by_rule = {finding.rule_id: finding for finding in findings}
        self.assertEqual(by_rule["TF_PUBLIC_INGRESS"].severity, "high")
        self.assertEqual(by_rule["TF_WILDCARD_IAM_ACTION"].severity, "high")
        self.assertEqual(by_rule["TF_WILDCARD_IAM_RESOURCE"].severity, "high")
        self.assertEqual(by_rule["TF_SENSITIVE_OUTPUT"].severity, "medium")
        self.assertEqual(by_rule["TF_MISSING_TAGS"].severity, "low")
        self.assertIn("terraform/main.tf", by_rule["TF_PUBLIC_INGRESS"].path)
        self.assertGreater(by_rule["TF_PUBLIC_INGRESS"].line, 0)

    def test_scan_terraform_does_not_flag_sensitive_output_when_marked_sensitive(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_terraform_text(
            Path("terraform/outputs.tf"),
            '''
output "api_token" {
  value     = random_password.token.result
  sensitive = true
}
''',
        )

        self.assertNotIn("TF_SENSITIVE_OUTPUT", {finding.rule_id for finding in findings})


class KubernetesScannerTests(unittest.TestCase):
    def test_scan_kubernetes_flags_workload_security_and_reliability_risks(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_kubernetes_text(
            Path("kubernetes/deployment.yaml"),
            """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      hostNetwork: true
      volumes:
        - name: host-logs
          hostPath:
            path: /var/log
      containers:
        - name: web
          image: nginx:latest
          securityContext:
            privileged: true
""",
        )

        by_rule = {finding.rule_id: finding for finding in findings}
        self.assertEqual(by_rule["K8S_LATEST_IMAGE_TAG"].severity, "medium")
        self.assertEqual(by_rule["K8S_MISSING_RESOURCE_REQUESTS"].severity, "medium")
        self.assertEqual(by_rule["K8S_MISSING_RESOURCE_LIMITS"].severity, "medium")
        self.assertEqual(by_rule["K8S_MISSING_READINESS_PROBE"].severity, "medium")
        self.assertEqual(by_rule["K8S_MISSING_LIVENESS_PROBE"].severity, "low")
        self.assertEqual(by_rule["K8S_PRIVILEGED_CONTAINER"].severity, "high")
        self.assertEqual(by_rule["K8S_HOST_PATH_VOLUME"].severity, "high")
        self.assertEqual(by_rule["K8S_HOST_NETWORK"].severity, "high")
        self.assertEqual(by_rule["K8S_DEFAULT_NAMESPACE"].severity, "low")

    def test_scan_kubernetes_does_not_flag_digest_or_registry_port_images(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_kubernetes_text(
            Path("kubernetes/deployment.yaml"),
            """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: apps
spec:
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: digest
          image: registry.example.com/web@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
        - name: registry-port
          image: localhost:5000/web:1.2.3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
""",
        )

        self.assertNotIn("K8S_LATEST_IMAGE_TAG", {finding.rule_id for finding in findings})

    def test_scan_kubernetes_flags_service_selector_without_matching_scanned_workload(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_kubernetes_documents(
            Path("kubernetes/service.yaml"),
            [
                {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "api", "namespace": "apps"},
                    "spec": {"selector": {"app": "api"}},
                },
                {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {"name": "web", "namespace": "apps"},
                    "spec": {
                        "template": {
                            "metadata": {"labels": {"app": "web"}},
                            "spec": {"containers": []},
                        }
                    },
                },
            ],
        )

        selector_findings = [
            finding
            for finding in findings
            if finding.rule_id == "K8S_SERVICE_SELECTOR_WITHOUT_MATCHING_WORKLOAD"
        ]
        self.assertEqual(len(selector_findings), 1)
        self.assertIn("scanned files", selector_findings[0].message)

    def test_scan_kubernetes_invalid_yaml_returns_parse_finding(self):
        reviewer = load_reviewer()
        findings = reviewer.scan_kubernetes_text(
            Path("kubernetes/bad.yaml"),
            "apiVersion: v1\nkind: Pod\nmetadata: [bad\n",
        )

        self.assertEqual(findings[0].rule_id, "K8S_YAML_PARSE_ERROR")
        self.assertEqual(findings[0].severity, "medium")


class StaticReviewCliTests(unittest.TestCase):
    def test_sample_infra_generates_static_review_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "static-review.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-infra"),
                    "--output",
                    str(output),
                    "--project-name",
                    "sample-infra",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertIn("# Static Review: sample-infra", report)
            self.assertIn("TF_PUBLIC_INGRESS", report)
            self.assertIn("K8S_PRIVILEGED_CONTAINER", report)
            self.assertIn("Commands are documentation only", report)

    def test_focus_terraform_excludes_kubernetes_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "terraform-review.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-infra"),
                    "--output",
                    str(output),
                    "--focus",
                    "terraform",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertIn("TF_PUBLIC_INGRESS", report)
            self.assertNotIn("K8S_PRIVILEGED_CONTAINER", report)

    def test_focus_kubernetes_excludes_terraform_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "kubernetes-review.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-infra"),
                    "--output",
                    str(output),
                    "--focus",
                    "kubernetes",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertNotIn("TF_PUBLIC_INGRESS", report)
            self.assertIn("K8S_PRIVILEGED_CONTAINER", report)

    def test_missing_input_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(Path(tmp) / "missing"),
                    "--output",
                    str(Path(tmp) / "static-review.md"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not exist", result.stderr)

    def test_empty_input_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    tmp,
                    "--output",
                    str(Path(tmp) / "static-review.md"),
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("No supported files", result.stderr)

    def test_output_directory_path_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(ROOT / "examples" / "sample-infra"),
                    "--output",
                    tmp,
                ],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exists as a directory", result.stderr)

    def test_invalid_yaml_is_reported_as_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_root = Path(tmp) / "infra"
            input_root.mkdir()
            (input_root / "bad.yaml").write_text(
                "apiVersion: v1\nkind: Pod\nmetadata: [bad\n",
                encoding="utf-8",
            )
            output = Path(tmp) / "static-review.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(input_root),
                    "--output",
                    str(output),
                    "--focus",
                    "kubernetes",
                ],
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = output.read_text(encoding="utf-8")
            self.assertIn("K8S_YAML_PARSE_ERROR", report)


if __name__ == "__main__":
    unittest.main()
