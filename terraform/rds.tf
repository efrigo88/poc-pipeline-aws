resource "aws_db_instance" "pg" {
  identifier             = "pgvector-db"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.medium"
  allocated_storage      = 20
  username               = "youruser"
  password               = "yourpass"
  db_name                = "yourdb"
  publicly_accessible    = true
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.pg.id]
  db_subnet_group_name   = aws_db_subnet_group.pg.name
  parameter_group_name   = aws_db_parameter_group.pgvector.name
}

resource "aws_db_parameter_group" "pgvector" {
  name   = "pgvector-params"
  family = "postgres15"
  parameter {
    name  = "shared_preload_libraries"
    value = "vector"
  }
}
