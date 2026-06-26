resource "aws_iam_policy" "wide" {
  name = "sample-wide"

  policy = <<POLICY
{
  "Statement": [{
    "Effect": "Allow",
    "Action": "*",
    "Resource": "*"
  }]
}
POLICY
}

output "api_token" {
  value = aws_iam_policy.wide.arn
}
