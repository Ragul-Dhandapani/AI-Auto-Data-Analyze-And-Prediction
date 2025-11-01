# ================================================================
# TERRAFORM VARIABLES - CUSTOMIZE THESE
# ================================================================

# AWS Region (change to your preferred region)
aws_region = "us-east-1"

# Database Credentials (CHANGE THESE!)
db_username = "testuser"
db_password = "YourSecurePassword123!" # CHANGE THIS!

# Project Name
project_name = "promise-ai-test"

# Allowed IP addresses to connect to databases
# SECURITY WARNING: ["0.0.0.0/0"] allows ALL IPs - restrict this!
# To allow only your IP: ["YOUR_IP_ADDRESS/32"]
allowed_cidr_blocks = ["0.0.0.0/0"]

# To get your IP address, run: curl ifconfig.me
# Then use: allowed_cidr_blocks = ["YOUR_IP/32"]
