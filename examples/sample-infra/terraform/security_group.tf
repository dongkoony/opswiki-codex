resource "aws_security_group" "web" {
  name        = "sample-web"
  description = "Sample public web security group"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
