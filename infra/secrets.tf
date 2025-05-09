locals {
  db_password = "P0stgr3s!" # Put here as this is for development purposes
}

resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.project_name}-db-password"
  description             = "Password for the database"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = local.db_password
}
