# POC Pipeline AWS

This project demonstrates a proof-of-concept pipeline using various AWS services, including RDS PostgreSQL with pgvector extension, ECS Fargate, and S3 for data storage.

## Architecture

The pipeline consists of the following components:

- **RDS PostgreSQL**: Database instance with pgvector extension for vector similarity search
- **ECS Fargate**: Serverless compute platform running containerized applications
- **S3**: Object storage for pipeline data
- **ECR**: Container registry for storing Docker images
- **CloudWatch**: Logging and monitoring
- **Secrets Manager**: Secure storage of database credentials

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform ~> 1.7
- Docker (for building and pushing container images)

## Infrastructure

The infrastructure is defined using Terraform and includes:

- VPC with public subnets
- Security groups for RDS and ECS tasks
- RDS PostgreSQL instance
- ECS Fargate cluster and task definitions
- S3 bucket with appropriate access policies
- IAM roles and policies
- CloudWatch log groups
- ECR repository

## Getting Started

1. Clone the repository:

   ```bash
   git clone git@github.com:efrigo88/poc-pipeline-aws.git
   cd poc-pipeline-aws
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file and fill in any missing values.

3. Deploy the infrastructure:

   ```bash
   chmod +x scripts/*.sh
   ./scripts/deploy.sh
   ```

   This will:

   - Initialize and apply Terraform
   - Create all AWS resources
   - Update your `.env` file with the database connection details

4. Run the ECS task:

   ```bash
   ./scripts/run_ecs_task.sh
   ```

   This will start the ECS task in Fargate. You can monitor the progress in:

   - AWS ECS Console
   - CloudWatch Logs
   - RDS instance metrics

5. Clean up:
   When you're done, you can destroy all resources:
   ```bash
   ./scripts/destroy.sh
   ```
   ⚠️ WARNING: This will destroy all infrastructure and data!

## Security Notes

- The RDS instance is publicly accessible for development purposes
- Database access is controlled through security groups
- Credentials are stored in AWS Secrets Manager
- S3 bucket has public access blocked

## Development

The project uses:

- Python for the main application
- PostgreSQL 17.4 with pgvector extension
- Apache Spark for data processing
- Ollama for machine learning tasks

## Important Notes

- This is a proof-of-concept setup and may need additional security measures for production use
- The RDS instance is publicly accessible - consider using private subnets and VPN/bastion hosts for production
- Review and adjust instance sizes and configurations based on your needs

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
