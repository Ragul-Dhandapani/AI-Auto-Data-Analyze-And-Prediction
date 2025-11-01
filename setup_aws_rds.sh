#!/bin/bash

# ================================================================
# PROMISE AI - AWS RDS Database Setup Script
# ================================================================

set -e  # Exit on error

echo "=========================================="
echo "PROMISE AI - AWS RDS Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ================================================================
# STEP 1: Prerequisites Check
# ================================================================

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}ERROR: Terraform is not installed${NC}"
    echo "Install from: https://www.terraform.io/downloads"
    exit 1
fi
echo -e "${GREEN}✓ Terraform found: $(terraform version -json | jq -r '.terraform_version')${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}ERROR: AWS CLI is not installed${NC}"
    echo "Install from: https://aws.amazon.com/cli/"
    exit 1
fi
echo -e "${GREEN}✓ AWS CLI found${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}ERROR: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials configured${NC}"

# Check psql (optional)
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ psql not found (optional for PostgreSQL connection)${NC}"
else
    echo -e "${GREEN}✓ psql found${NC}"
fi

# Check mysql (optional)
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}⚠ mysql not found (optional for MySQL connection)${NC}"
else
    echo -e "${GREEN}✓ mysql found${NC}"
fi

echo ""

# ================================================================
# STEP 2: Terraform Init
# ================================================================

echo -e "${BLUE}Step 2: Initializing Terraform...${NC}"
cd terraform
terraform init
echo -e "${GREEN}✓ Terraform initialized${NC}"
echo ""

# ================================================================
# STEP 3: Review Configuration
# ================================================================

echo -e "${BLUE}Step 3: Configuration Review${NC}"
echo -e "${YELLOW}Please review terraform.tfvars and update:${NC}"
echo "  - db_password (change default password!)"
echo "  - allowed_cidr_blocks (restrict access!)"
echo ""
echo "To get your IP: curl ifconfig.me"
echo ""
read -p "Have you updated terraform.tfvars? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Please update terraform.tfvars first${NC}"
    exit 1
fi
echo ""

# ================================================================
# STEP 4: Terraform Plan
# ================================================================

echo -e "${BLUE}Step 4: Planning infrastructure...${NC}"
terraform plan -out=tfplan
echo ""
read -p "Do you want to proceed with creating these resources? (yes/no): " proceed
if [ "$proceed" != "yes" ]; then
    echo -e "${YELLOW}Setup cancelled${NC}"
    exit 0
fi
echo ""

# ================================================================
# STEP 5: Terraform Apply
# ================================================================

echo -e "${BLUE}Step 5: Creating AWS RDS instances...${NC}"
echo -e "${YELLOW}This will take 5-10 minutes...${NC}"
terraform apply tfplan
echo -e "${GREEN}✓ Infrastructure created!${NC}"
echo ""

# ================================================================
# STEP 6: Get Connection Details
# ================================================================

echo -e "${BLUE}Step 6: Retrieving connection details...${NC}"

# Get outputs
PG_HOST=$(terraform output -raw postgresql_address)
PG_PORT=$(terraform output -raw postgresql_port)
MYSQL_HOST=$(terraform output -raw mysql_address)
MYSQL_PORT=$(terraform output -raw mysql_port)

# Get credentials from tfvars
DB_USERNAME=$(grep db_username terraform.tfvars | cut -d'=' -f2 | tr -d ' "')
DB_PASSWORD=$(grep db_password terraform.tfvars | cut -d'=' -f2 | tr -d ' "')

echo ""
echo "=========================================="
echo "CONNECTION DETAILS"
echo "=========================================="
echo ""
echo -e "${GREEN}PostgreSQL:${NC}"
echo "  Host: $PG_HOST"
echo "  Port: $PG_PORT"
echo "  Database: testdb"
echo "  Username: $DB_USERNAME"
echo "  Password: $DB_PASSWORD"
echo "  Connection String: postgresql://$DB_USERNAME:$DB_PASSWORD@$PG_HOST:$PG_PORT/testdb"
echo ""
echo -e "${GREEN}MySQL:${NC}"
echo "  Host: $MYSQL_HOST"
echo "  Port: $MYSQL_PORT"
echo "  Database: testdb"
echo "  Username: $DB_USERNAME"
echo "  Password: $DB_PASSWORD"
echo "  Connection String: mysql://$DB_USERNAME:$DB_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/testdb"
echo ""

# Save to file
cat > ../aws_db_credentials.txt << EOF
PROMISE AI - AWS RDS Connection Details
========================================

PostgreSQL:
-----------
Host: $PG_HOST
Port: $PG_PORT
Database: testdb
Username: $DB_USERNAME
Password: $DB_PASSWORD
Connection String: postgresql://$DB_USERNAME:$DB_PASSWORD@$PG_HOST:$PG_PORT/testdb

MySQL:
------
Host: $MYSQL_HOST
Port: $MYSQL_PORT
Database: testdb
Username: $DB_USERNAME
Password: $DB_PASSWORD
Connection String: mysql://$DB_USERNAME:$DB_PASSWORD@$MYSQL_HOST:$MYSQL_PORT/testdb

PROMISE AI Configuration:
-------------------------
Use these details in the PROMISE AI Dashboard -> Database Connection tab.

Created: $(date)
EOF

echo -e "${GREEN}✓ Credentials saved to: aws_db_credentials.txt${NC}"
echo ""

# ================================================================
# STEP 7: Wait for Databases to be Ready
# ================================================================

echo -e "${BLUE}Step 7: Waiting for databases to be ready...${NC}"
echo -e "${YELLOW}Waiting 60 seconds for databases to fully initialize...${NC}"
sleep 60
echo -e "${GREEN}✓ Databases should be ready${NC}"
echo ""

# ================================================================
# STEP 8: Load Test Data
# ================================================================

echo -e "${BLUE}Step 8: Loading test data...${NC}"
read -p "Do you want to load test datasets now? (yes/no): " load_data

if [ "$load_data" = "yes" ]; then
    # PostgreSQL
    if command -v psql &> /dev/null; then
        echo -e "${BLUE}Loading PostgreSQL test data...${NC}"
        PGPASSWORD=$DB_PASSWORD psql -h $PG_HOST -U $DB_USERNAME -d testdb -f ../test_datasets_setup.sql
        echo -e "${GREEN}✓ PostgreSQL data loaded${NC}"
    else
        echo -e "${YELLOW}⚠ psql not available. Load data manually:${NC}"
        echo "psql -h $PG_HOST -U $DB_USERNAME -d testdb -f test_datasets_setup.sql"
    fi
    
    # MySQL
    if command -v mysql &> /dev/null; then
        echo -e "${BLUE}Loading MySQL test data...${NC}"
        mysql -h $MYSQL_HOST -u $DB_USERNAME -p$DB_PASSWORD testdb < ../test_datasets_mysql.sql
        echo -e "${GREEN}✓ MySQL data loaded${NC}"
    else
        echo -e "${YELLOW}⚠ mysql not available. Load data manually:${NC}"
        echo "mysql -h $MYSQL_HOST -u $DB_USERNAME -p testdb < test_datasets_mysql.sql"
    fi
fi

echo ""

# ================================================================
# STEP 9: Test Connection
# ================================================================

echo -e "${BLUE}Step 9: Testing connection...${NC}"

# Test PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${BLUE}Testing PostgreSQL connection...${NC}"
    if PGPASSWORD=$DB_PASSWORD psql -h $PG_HOST -U $DB_USERNAME -d testdb -c "SELECT 'Connection successful!' as status;" &> /dev/null; then
        echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
    else
        echo -e "${RED}✗ PostgreSQL connection failed${NC}"
    fi
fi

# Test MySQL
if command -v mysql &> /dev/null; then
    echo -e "${BLUE}Testing MySQL connection...${NC}"
    if mysql -h $MYSQL_HOST -u $DB_USERNAME -p$DB_PASSWORD testdb -e "SELECT 'Connection successful!' as status;" &> /dev/null; then
        echo -e "${GREEN}✓ MySQL connection successful${NC}"
    else
        echo -e "${RED}✗ MySQL connection failed${NC}"
    fi
fi

echo ""

# ================================================================
# COMPLETION
# ================================================================

echo "=========================================="
echo -e "${GREEN}SETUP COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Open PROMISE AI: http://localhost:3000"
echo "2. Go to Dashboard -> Database Connection"
echo "3. Enter connection details from aws_db_credentials.txt"
echo "4. Test connection and load tables"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "- Connection details saved in: aws_db_credentials.txt"
echo "- Keep credentials secure"
echo "- To destroy resources: cd terraform && terraform destroy"
echo ""
echo -e "${YELLOW}Cost Warning:${NC}"
echo "- These RDS instances are running 24/7"
echo "- Free tier: 750 hours/month for db.t3.micro"
echo "- After free tier: ~$25-30/month for both databases"
echo "- Run 'terraform destroy' when done testing"
echo ""
echo "Happy testing! 🚀"
