# AWS RDS Setup for PROMISE AI Database Testing

## 🎯 What This Does

Creates **PostgreSQL** and **MySQL** databases in AWS RDS (Free Tier eligible) with test data for PROMISE AI testing.

---

## 📋 Prerequisites

### 1. AWS Account
- Sign up at: https://aws.amazon.com/free/
- Free tier includes 750 hours/month of RDS

### 2. AWS CLI Installed & Configured
```bash
# Install AWS CLI
# macOS:
brew install awscli

# Linux:
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure with your credentials
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

### 3. Terraform Installed
```bash
# macOS:
brew install terraform

# Linux:
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify
terraform version
```

### 4. Database Clients (Optional - for loading test data)
```bash
# PostgreSQL client
# macOS:
brew install postgresql

# Linux:
sudo apt-get install postgresql-client

# MySQL client
# macOS:
brew install mysql-client

# Linux:
sudo apt-get install mysql-client
```

---

## 🚀 Quick Start (Automated)

### Option 1: Use Setup Script (Recommended)

```bash
cd /app
./setup_aws_rds.sh
```

**What it does:**
1. ✅ Checks prerequisites
2. ✅ Initializes Terraform
3. ✅ Creates VPC, subnets, security groups
4. ✅ Creates PostgreSQL RDS instance
5. ✅ Creates MySQL RDS instance
6. ✅ Loads test data (5 tables each)
7. ✅ Tests connections
8. ✅ Saves credentials to `aws_db_credentials.txt`

**Time:** ~10-15 minutes

---

## 🔧 Manual Setup

### Step 1: Update Configuration

Edit `terraform/terraform.tfvars`:

```hcl
# CHANGE THESE VALUES!
db_username = "testuser"
db_password = "YourSecurePassword123!"  # CHANGE THIS!

# Restrict access to your IP only (recommended)
# Get your IP: curl ifconfig.me
allowed_cidr_blocks = ["YOUR_IP_ADDRESS/32"]

# Or allow from anywhere (less secure)
allowed_cidr_blocks = ["0.0.0.0/0"]
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Plan Infrastructure

```bash
terraform plan
```

Review what will be created:
- VPC with 2 subnets
- Internet gateway
- Security groups (PostgreSQL, MySQL)
- RDS PostgreSQL instance (db.t3.micro)
- RDS MySQL instance (db.t3.micro)

### Step 4: Create Infrastructure

```bash
terraform apply
```

Type `yes` to confirm.

**Wait:** 5-10 minutes for RDS instances to be created.

### Step 5: Get Connection Details

```bash
# PostgreSQL
terraform output postgresql_connection_string

# MySQL
terraform output mysql_connection_string

# All details
terraform output connection_info
```

### Step 6: Load Test Data

**PostgreSQL:**
```bash
# Get connection details
PG_HOST=$(terraform output -raw postgresql_address)
DB_USER=$(grep db_username terraform.tfvars | cut -d'=' -f2 | tr -d ' "')
DB_PASS=$(grep db_password terraform.tfvars | cut -d'=' -f2 | tr -d ' "')

# Load data
PGPASSWORD=$DB_PASS psql -h $PG_HOST -U $DB_USER -d testdb -f ../test_datasets_setup.sql
```

**MySQL:**
```bash
# Get connection details
MYSQL_HOST=$(terraform output -raw mysql_address)

# Load data
mysql -h $MYSQL_HOST -u $DB_USER -p$DB_PASS testdb < ../test_datasets_mysql.sql
```

---

## 📊 What Gets Created

### Databases

| Database | Engine | Version | Instance | Storage | Database |
|----------|--------|---------|----------|---------|----------|
| PostgreSQL | postgres | 15.4 | db.t3.micro | 20 GB | testdb |
| MySQL | mysql | 8.0.35 | db.t3.micro | 20 GB | testdb |

### Test Tables (5 per database)

| Table | Rows | Purpose |
|-------|------|---------|
| employees_small | 100 | Quick testing |
| sales_medium | 1,000 | Medium dataset |
| transactions_large | 10,000 | Large/GridFS test |
| departments | 5 | JOIN reference |
| customer_info | 5,000 | JOIN reference |

---

## 🔌 Connect from PROMISE AI

### Step 1: Get Credentials

Check `aws_db_credentials.txt` or run:
```bash
cd terraform
terraform output connection_info
```

### Step 2: Open PROMISE AI

Navigate to: http://localhost:3000

### Step 3: Connect to PostgreSQL

1. Go to Dashboard → "Database Connection" tab
2. Fill in:
   ```
   Database Type: PostgreSQL
   Host: [from terraform output]
   Port: 5432
   Username: testuser (or your custom value)
   Password: [your password from terraform.tfvars]
   Database: testdb
   ```
3. Click "Test Connection" → ✅ Should see "Connected"
4. Click "List Tables" → Should see 5 tables
5. Select a table → Click "Load Table"

### Step 4: Test Custom SQL Query

1. Go to "Custom SQL Query" tab
2. Enter connection details (same as above)
3. Click "Test Connection"
4. Enter query:
   ```sql
   SELECT e.name, e.salary, d.dept_name
   FROM employees_small e
   JOIN departments d ON e.department = d.dept_name
   WHERE e.salary > 70000
   ORDER BY e.salary DESC
   ```
5. Click "Execute Query & Load Data"
6. Run full analysis!

---

## 💰 Cost Information

### Free Tier (First 12 months)
- ✅ 750 hours/month of db.t3.micro usage
- ✅ 20 GB storage per database
- ✅ 20 GB backup storage

**Both PostgreSQL and MySQL run within free tier if:**
- Total usage < 750 hours/month
- Only one is running, OR
- Both run part-time totaling < 750 hours

### After Free Tier
- **db.t3.micro:** $0.017/hour = ~$12.50/month per instance
- **Storage:** $0.115/GB-month
- **Total for both:** ~$25-30/month

### 💡 Cost Saving Tips

1. **Stop when not testing:**
   ```bash
   # Stop RDS instances (saves compute costs)
   aws rds stop-db-instance --db-instance-identifier promise-ai-test-postgresql
   aws rds stop-db-instance --db-instance-identifier promise-ai-test-mysql
   ```

2. **Destroy when done:**
   ```bash
   cd terraform
   terraform destroy
   ```

3. **Use only one database** (PostgreSQL is recommended)

---

## 🧪 Testing Checklist

Once databases are set up:

- [ ] Test PostgreSQL connection from PROMISE AI
- [ ] List tables in PostgreSQL
- [ ] Load employees_small table (100 rows)
- [ ] Load transactions_large table (10,000 rows)
- [ ] Test custom SQL query with JOIN
- [ ] Run Data Profiler on query results
- [ ] Run Predictive Analysis on query results
- [ ] Save workspace
- [ ] Test MySQL connection
- [ ] Repeat tests with MySQL

---

## 🛠️ Troubleshooting

### Connection Timeout

**Problem:** Can't connect to RDS instance

**Solutions:**
1. Check security group allows your IP:
   ```bash
   curl ifconfig.me  # Get your current IP
   ```
   Update `terraform.tfvars`:
   ```hcl
   allowed_cidr_blocks = ["YOUR_IP/32"]
   ```
   Then:
   ```bash
   terraform apply
   ```

2. Verify RDS instance is running:
   ```bash
   aws rds describe-db-instances --db-instance-identifier promise-ai-test-postgresql
   ```

3. Check VPC and subnet configuration

### Database Not Ready

**Problem:** "Connection refused" immediately after creation

**Solution:** Wait 2-3 minutes after `terraform apply` completes. RDS instances take time to initialize.

### Wrong Credentials

**Problem:** "Authentication failed"

**Solution:** 
1. Check `terraform.tfvars` for correct password
2. Verify username matches
3. PostgreSQL username is case-sensitive

### psql/mysql Not Found

**Problem:** Can't load test data

**Solution:** Install database clients (see Prerequisites) or load data manually using a GUI tool like DBeaver or pgAdmin.

---

## 🗑️ Cleanup

### Destroy All Resources

```bash
cd terraform
terraform destroy
```

Type `yes` to confirm.

**This will:**
- ❌ Delete both RDS instances
- ❌ Delete all data (unless you created snapshots)
- ❌ Delete VPC, subnets, security groups
- ✅ Stop all charges

### Keep Data but Stop Instances

```bash
# Stop instances (free tier still applies to storage)
aws rds stop-db-instance --db-instance-identifier promise-ai-test-postgresql
aws rds stop-db-instance --db-instance-identifier promise-ai-test-mysql

# Note: AWS will automatically restart stopped instances after 7 days
```

---

## 📁 Files Structure

```
/app/
├── terraform/
│   ├── main.tf                 # Terraform configuration
│   └── terraform.tfvars        # Your custom variables (EDIT THIS!)
├── setup_aws_rds.sh            # Automated setup script
├── test_datasets_setup.sql     # PostgreSQL test data
├── test_datasets_mysql.sql     # MySQL test data
├── aws_db_credentials.txt      # Generated after setup (DO NOT COMMIT!)
└── AWS_RDS_SETUP.md           # This file
```

---

## 🔒 Security Best Practices

### For Testing (Current Setup)
- ⚠️ Publicly accessible (for easy testing)
- ⚠️ Broad IP access (0.0.0.0/0)
- ⚠️ Simple password

### For Production
1. **Restrict IP Access:**
   ```hcl
   allowed_cidr_blocks = ["YOUR_OFFICE_IP/32", "YOUR_HOME_IP/32"]
   ```

2. **Use Strong Password:**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols

3. **Enable Encryption:**
   - Already enabled: `storage_encrypted = true`

4. **Private Subnet:**
   - Use private subnets with bastion host or VPN

5. **Enable Deletion Protection:**
   ```hcl
   deletion_protection = true
   ```

6. **Regular Backups:**
   ```hcl
   backup_retention_period = 7
   ```

---

## 📞 Support

### Terraform Issues
- Docs: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

### AWS RDS Issues
- Docs: https://docs.aws.amazon.com/rds/
- Support: AWS Support Center

### PROMISE AI Issues
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Check frontend console (F12)

---

## ✅ Success Criteria

Setup is successful when:
1. ✅ `terraform apply` completes without errors
2. ✅ Both RDS instances show "available" status
3. ✅ Connection test from PROMISE AI succeeds
4. ✅ Tables list correctly
5. ✅ Test data loads (5 tables each)
6. ✅ Custom SQL queries execute
7. ✅ Full analysis pipeline works

---

**You're all set! Start testing with real cloud databases! 🎉**
