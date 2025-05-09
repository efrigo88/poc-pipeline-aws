resource "aws_db_instance" "pg" {
  identifier = "pgvector-db"
  engine     = "postgres"
  # https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-versions.html
  engine_version         = "17.4"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  db_name                = var.db_name
  username               = var.db_username
  password               = aws_secretsmanager_secret_version.db_password.secret_string
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

output "connection_details" {
  description = "DB Connection details"
  value = nonsensitive(<<-EOT
    host=${aws_db_instance.pg.address}
    port=${aws_db_instance.pg.port}
    db_name=${var.db_name}
    db_user=${var.db_username}
    db_password=${aws_secretsmanager_secret_version.db_password.secret_string}
  EOT
  )
}
