import os


if os.getenv("DYNAMODB_HOST"):
    print("Running in local mode. Setting dummy AWS credentials.")
    os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"

from app.models import Ticket, TicketHistory

def create_dynamodb_tables():

    print("Connecting to DynamoDB...")
    
    if not Ticket.exists():
        print(f"Creating table: {Ticket.Meta.table_name}...")
        Ticket.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)
        print("Table created successfully.")
    else:
        print(f"Table '{Ticket.Meta.table_name}' already exists.")

    if not TicketHistory.exists():
        print(f"Creating table: {TicketHistory.Meta.table_name}...")
        TicketHistory.create_table(wait=True, read_capacity_units=1, write_capacity_units=1)
        print("Table created successfully.")
    else:
        print(f"Table '{TicketHistory.Meta.table_name}' already exists.")

    print("Database setup complete.")

if __name__ == "__main__":
    # Ensure environment variables are set before running
    # Example for PowerShell:
    # > $env:DYNAMODB_REGION="us-east-1"
    # > $env:DYNAMODB_HOST="http://localhost:8002"
    # > python create_tables.py
    create_dynamodb_tables()
