# Skill: Elicit Functional Requirements (RF)

This skill guides the agent in identifying and documenting the functional requirements for the Olist Data Pipeline, ensuring all business needs and technical flows are covered.

## Objective
To capture what the system must do to fulfill the business goal of processing marketplace orders into an analytical database.

## Workflow
1. **Analyze Input:** Review the problem specification (`00_problem.md`) and any stakeholder notes.
2. **Identify Critical Flows:** Map the journey of a record from S3 upload to RDS persistence.
3. **Draft Requirements:** Formulate RFs using the standard format: `RFXX: [Requirement Name] - [Description]`.
4. **Validation:** Check if each RF is atomic, verifiable, and necessary.

## Standard Requirements for this Project
- **Ingestion:** Must handle CSV files from S3.
- **Validation:** Must validate schema (headers, data types).
- **Transformation:** Must transform raw CSV data into the analytical schema.
- **Persistence:** Must load data into Postgres.
- **Idempotency:** Must handle updates to existing records (Upsert).
- **Error Handling:** Must isolate invalid records into a Dead Letter Table (DLT).
- **Lineage:** Must tag records with ingestion timestamps and source file names.

## Output Format
All requirements should be added to `documents/01_functional_requirements.md` in a table or list format.
