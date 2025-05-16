locals {
  bucket_name = "${var.project_name}-${var.environment}-fhslxnfjksns"
}

resource "aws_s3_bucket" "poc_pipeline_data" {
  bucket = local.bucket_name
}

# Block public access
resource "aws_s3_bucket_public_access_block" "poc_pipeline_data" {
  bucket = aws_s3_bucket.poc_pipeline_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload data directory
resource "aws_s3_object" "data_files" {
  depends_on = [aws_s3_bucket_public_access_block.poc_pipeline_data]
  for_each   = fileset("${path.module}/../data", "**/*")

  bucket = aws_s3_bucket.poc_pipeline_data.id
  key    = "data/${each.value}"
  source = "${path.module}/../data/${each.value}"
  etag   = filemd5("${path.module}/../data/${each.value}")
}

output "bucket_name" {
  value       = aws_s3_bucket.poc_pipeline_data.id
  description = "Name of the S3 bucket"
}
