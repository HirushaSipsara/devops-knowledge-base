terraform {
  backend "s3" {
    bucket       = "devops-knowledge-base-tfstate-622215957056"
    key          = "dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}