variable "aws_region" {
  description = "AWS region for provisioning resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name identifier"
  type        = string
  default     = "devops-knowledge-base"
}

variable "instance_type" {
  description = "EC2 instance type (Free Tier eligible: t2.micro or t3.micro)"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Optional AWS EC2 Key Pair name for SSH access"
  type        = string
  default     = ""
}

variable "app_port" {
  description = "Port on which the FastAPI application container listens"
  type        = number
  default     = 8000
}
