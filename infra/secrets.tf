resource "aws_secretsmanager_secret" "db_username" {
  name = "${var.project_name}-db-username"
}

resource "aws_secretsmanager_secret_version" "db_username" {
  secret_id     = aws_secretsmanager_secret.db_username.id
  secret_string = var.db_username
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.project_name}-db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

resource "aws_secretsmanager_secret" "db_name" {
  name = "${var.project_name}-db-name"
}

resource "aws_secretsmanager_secret_version" "db_name" {
  secret_id     = aws_secretsmanager_secret.db_name.id
  secret_string = var.db_name
}
