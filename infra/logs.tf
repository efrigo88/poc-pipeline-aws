resource "aws_cloudwatch_log_group" "poc_task" {
  name              = "/ecs/poc-task"
  retention_in_days = 30
}
