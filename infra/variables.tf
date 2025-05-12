# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "poc-pipeline"
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "db_username" {
  description = "Username for the RDS instance"
  type        = string
  default     = "postgres"
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  default     = "vectordb"
}

variable "ollama_host" {
  description = "Host for the Ollama instance"
  type        = string
  default     = "http://localhost:11434"
}
