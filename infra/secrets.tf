# If the secret is marked as deleted, restore it with:
# aws secretsmanager delete-secret --secret-id db_username --force-delete-without-recovery --region eu-west-1 | cat
resource "aws_secretsmanager_secret" "db_username" {
  name                    = "${var.project_name}-db-username"
  description             = "Username for the database"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_username" {
  secret_id     = aws_secretsmanager_secret.db_username.id
  secret_string = var.db_username
}

resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.project_name}-db-password"
  description             = "Password for the database"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

resource "aws_secretsmanager_secret" "db_name" {
  name                    = "${var.project_name}-db-name"
  description             = "Name of the database"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db_name" {
  secret_id     = aws_secretsmanager_secret.db_name.id
  secret_string = var.db_name
}
