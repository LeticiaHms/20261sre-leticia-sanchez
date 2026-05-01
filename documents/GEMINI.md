# Project Gemini Context: Olist ETL Pipeline

This project is a Site Reliability Engineering (SRE) and Data Engineering initiative focused on building a high-volume, reliable, and observable data pipeline for Olist transactions using AWS cloud infrastructure.

## Project Overview
The pipeline is designed to process ~100k daily orders from marketplaces, ensuring data integrity, zero duplicates, and pro-active monitoring. It follows an **Event-Driven Architecture**.

### Core Architecture
- **Storage:** **AWS S3** for raw (landing), processed, and failed data files.
- **Trigger:** **AWS Lambda** reacts to S3 events to initiate the process.
- **Compute:** **AWS ECS Fargate** runs the ETL container (Python-based) to handle long-running tasks.
- **Database:** **AWS RDS Postgres** serves as the analytical storage.
- **Security:** **IAM Roles**, **Secrets Manager**, and **VPC Endpoints** for secure, private internal traffic.
- **Observability:** **CloudWatch** for real-time logs and numerical metrics (ingestion volume, error rates, latency).

### Main Technologies
- **Infrastructure:** Terraform (IaC)
- **Containerization:** Docker
- **Language:** Python (ETL logic)
- **Database Logic:** Postgres `COPY` for bulk loading and `ON CONFLICT` for idempotency.

## Building and Running
*Note: Commands are inferred from the technical specification.*

### Infrastructure Management
- `terraform init`: Initialize Terraform workspace.
- `terraform plan`: Preview infrastructure changes.
- `terraform apply`: Deploy resources to AWS.

### ETL Container
- `docker build -t olist-etl .`: Build the ETL processing image.
- `docker push [ECR_REPOSITORY_URL]`: Push image to AWS ECR.

### Testing and CI/CD
- CI/CD pipelines are expected to run unit tests and update ECS Task Definitions automatically.
- **TODO:** Define specific local execution commands for the Python ETL script.

## Development Conventions
- **Idempotency:** All data loads must be idempotent. Use `UPSERT` logic (`ON CONFLICT`) to prevent duplicates during re-runs.
- **Performance:** Use the native Postgres `COPY` command for bulk loads instead of individual `INSERT` statements.
- **Circuit Breaker:** The script must abort and `ROLLBACK` the transaction if the record error rate exceeds a threshold (e.g., 5%).
- **Staging Area:** Load data into a staging table for validation before moving to production tables in an atomic transaction.
- **Observability First:** Every component must report numerical metrics to CloudWatch. The system should never "suffer silently."
- **Security:** Adhere to the principle of least privilege using IAM Task Roles and ensure all traffic remains within the VPC.

## Key Files
- `spec/00_problem.md`: Comprehensive technical specification, problem modeling, and architectural rationale.
- `README.md`: Project identification.
