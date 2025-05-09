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

variable "spark_threads" {
  description = "Number of threads for the Spark application"
  type        = string
  default     = "local[2]"
}

variable "spark_driver_memory" {
  description = "Driver memory for the Spark application"
  type        = string
  default     = "4g"
}

variable "spark_shuffle_partitions" {
  description = "Number of shuffle partitions for the Spark application"
  type        = number
  default     = 2
}

# TODO: Remove this variable
variable "db_password" {
  description = "Password for the RDS instance"
  type        = string
  default     = "P0stgr3s!"
}
