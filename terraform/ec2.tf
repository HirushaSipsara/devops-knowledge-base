# Security Group for the EC2 Docker Host
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-${var.environment}-sg"
  description = "Security Group for DevOps Knowledge Base Application"
  vpc_id      = data.aws_vpc.default.id

  # Inbound HTTP (Application Port)
  ingress {
    description = "Allow FastAPI app traffic"
    from_port   = var.app_port
    to_port     = var.app_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound HTTP (Standard Port 80)
  ingress {
    description = "Allow standard HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound SSH
  ingress {
    description = "Allow SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound All Traffic
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-sg"
  }
}

# EC2 Instance to host the Container Application
resource "aws_instance" "app_server" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  vpc_security_group_ids      = [aws_security_group.app_sg.id]
  key_name                    = var.key_name != "" ? var.key_name : null
  associate_public_ip_address = true

  # Cloud-init User Data script to install Docker & Docker Compose
  user_data = <<-EOF
              #!/bin/bash
              set -e

              # Update system packages
              apt-get update -y
              apt-get upgrade -y

              # Install prerequisite packages
              apt-get install -y \
                ca-certificates \
                curl \
                gnupg \
                lsb-release \
                git

              # Install Docker Engine & Compose plugin
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              chmod a+r /etc/apt/keyrings/docker.gpg

              echo \
                "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null

              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

              # Enable and start Docker service
              systemctl enable docker
              systemctl start docker

              # Add ubuntu user to docker group
              usermod -aG docker ubuntu

              echo "Docker installation completed successfully."
              EOF

  tags = {
    Name = "${var.project_name}-${var.environment}-server"
  }
}
