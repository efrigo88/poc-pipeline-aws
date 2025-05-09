resource "aws_db_instance" "pg" {
  identifier = "pgvector-db"
  engine     = "postgres"
  # https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-versions.html
  engine_version         = "17.4"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  username               = var.db_username
  password               = var.db_password
  db_name                = var.db_name
  publicly_accessible    = true
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.pg.id]
  db_subnet_group_name   = aws_db_subnet_group.pg.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  tags = {
    Name = "pgvector-db"
  }
}

# Output the full connection string
output "rds_connection_string" {
  description = "The full connection string for the database"
  value       = nonsensitive("postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.pg.address}:${aws_db_instance.pg.port}/${var.db_name}")
}

# Output formatted for .env file
output "env_format" {
  description = "Connection details formatted for .env file"
  value = nonsensitive(<<-EOT
    POSTGRES_HOST=${aws_db_instance.pg.address}
    POSTGRES_PORT=${aws_db_instance.pg.port}
    POSTGRES_DB=${var.db_name}
    POSTGRES_USER=${var.db_username}
    POSTGRES_PASSWORD=${var.db_password}
  EOT
  )
}
