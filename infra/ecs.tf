# ECS Configuration
locals {
  task_cpu    = 4096  # CPU units for the ECS task (1024 units = 1 vCPU)
  task_memory = 16384 # Memory for the ECS task in MiB
  disk_size   = 100   # Disk size for the ECS task in GiB
}

# ECS Cluster
resource "aws_ecs_cluster" "poc_pipeline" {
  name = "poc-pipeline-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "poc_task" {
  family                   = "poc-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = local.task_cpu
  memory                   = local.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  ephemeral_storage {
    size_in_gib = local.disk_size
  }

  container_definitions = jsonencode([
    {
      name      = "ollama"
      image     = "ollama/ollama:latest"
      essential = true
      portMappings = [
        {
          containerPort = 11434
          hostPort      = 11434
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/poc-task"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs-ollama"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "ollama list || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    },
    {
      name      = "poc-container"
      image     = "${aws_ecr_repository.poc_pipeline.repository_url}:latest"
      essential = true
      dependsOn = [
        {
          containerName = "ollama"
          condition     = "HEALTHY"
        }
      ]
      environment = [
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "S3_BUCKET"
          value = aws_s3_bucket.poc_pipeline_data.id
        },
        {
          name  = "OLLAMA_HOST"
          value = var.ollama_host
        },
        {
          name  = "POSTGRES_HOST"
          value = aws_db_instance.pg.address
        },
        {
          name  = "POSTGRES_PORT"
          value = tostring(aws_db_instance.pg.port)
        },
        {
          name  = "POSTGRES_DB"
          value = var.db_name
        },
        {
          name  = "POSTGRES_USER"
          value = var.db_username
        },
        {
          name  = "POSTGRES_PASSWORD"
          value = aws_secretsmanager_secret_version.db_password.secret_string
        },
        {
          name  = "SPARK_THREADS"
          value = var.spark_threads
        },
        {
          name  = "SPARK_DRIVER_MEMORY"
          value = var.spark_driver_memory
        },
        {
          name  = "SPARK_SHUFFLE_PARTITIONS"
          value = var.spark_shuffle_partitions
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/poc-task"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs-poc"
        }
      }
      entryPoint = ["/bin/sh", "-c"]
      command = [
        "curl -X POST ${var.ollama_host}/api/pull -d '{\"name\":\"nomic-embed-text\"}' && python -m src.main"
      ]
    }
  ])
}

# Output the task definition ARN for easy reference
output "task_definition_arn" {
  value       = aws_ecs_task_definition.poc_task.arn
  description = "ARN of the ECS task definition"
}
