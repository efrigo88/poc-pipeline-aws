resource "aws_ecr_repository" "poc_pipeline" {
  name         = "poc-pipeline"
  force_delete = true
}

resource "aws_ecr_lifecycle_policy" "poc_pipeline" {
  repository = aws_ecr_repository.poc_pipeline.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = {
        type = "expire"
      }
    }]
  })
}
