# ==============================================================================
# AWS S3 Remote State & DynamoDB Locking
# ==============================================================================
# To enable remote state storage in AWS S3:
# 1. Create an S3 Bucket (e.g., `devops-knowledge-base-tfstate-<your-id>`).
# 2. (Optional) Create a DynamoDB table named `terraform-lock-table` with Partition Key `LockID` (String).
# 3. Uncomment the `backend "s3"` block below and update the bucket name & region.
# 4. Run `terraform init -migrate-state` or `terraform init`.
# ==============================================================================

terraform {
  # backend "s3" {
  #   bucket         = "devops-knowledge-base-tfstate"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-lock-table"
  #   encrypt        = true
  # }
}
