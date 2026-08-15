output "instance_id" {
  description = "ID of the provisioned EC2 instance"
  value       = aws_instance.app_server.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.app_server.public_dns
}

output "application_url" {
  description = "Direct URL to access the running application"
  value       = "http://${aws_instance.app_server.public_ip}:${var.app_port}"
}

output "ssh_connection_command" {
  description = "Example command to SSH into the EC2 instance"
  value       = var.key_name != "" ? "ssh -i <path-to-${var.key_name}.pem> ubuntu@${aws_instance.app_server.public_ip}" : "SSH key not configured"
}
