# Fix for Kerberos Oracle Connection with external_auth=True

## Problem
When using `external_auth=True` with cx_Oracle 8.3.0 and Python 3.10.11 for Kerberos authentication, you get an error because:

1. **`external_auth=True` means "use OS-level authentication" (Kerberos, Wallet, etc.)**
2. When using external authentication, you **MUST NOT** pass `user` and `password` parameters
3. The DSN should be created without credentials

## Error in Your Code
```python
return cx_Oracle.SessionPool(
    dsn=dsn,
    min=2,
    max=self.pool_size,
    increment=1,
    threaded=True,
    external_auth=True  # ❌ This expects NO user/password in dsn
)
```

## Solution

### Option 1: Kerberos Authentication (external_auth=True)

```python
def _create_pool_with_kerberos(self):
    """Create Oracle SessionPool with Kerberos authentication"""
    import os
    
    # Get connection details (NO user/password)
    host = os.getenv('ORACLE_HOST')
    port = os.getenv('ORACLE_PORT', '1521')
    service_name = os.getenv('ORACLE_SERVICE_NAME')
    
    # Create DSN without credentials
    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
    
    print(f"🔐 Creating Kerberos-authenticated connection to {host}:{port}/{service_name}")
    
    # Create SessionPool with external auth
    # DO NOT pass user/password when using external_auth=True
    return cx_Oracle.SessionPool(
        dsn=dsn,
        min=2,
        max=self.pool_size,
        increment=1,
        threaded=True,
        external_auth=True  # ✅ Uses Kerberos/OS authentication
    )
```

### Option 2: Standard Username/Password Authentication

```python
def _create_pool_with_credentials(self):
    """Create Oracle SessionPool with username/password"""
    import os
    
    # Get all connection details INCLUDING credentials
    host = os.getenv('ORACLE_HOST')
    port = os.getenv('ORACLE_PORT', '1521')
    user = os.getenv('ORACLE_USER')
    password = os.getenv('ORACLE_PASSWORD')
    service_name = os.getenv('ORACLE_SERVICE_NAME')
    
    # Create DSN without credentials
    dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
    
    print(f"🔑 Creating credential-based connection for {user}@{host}:{port}/{service_name}")
    
    # Create SessionPool with credentials
    # DO NOT use external_auth=True when passing user/password
    return cx_Oracle.SessionPool(
        user=user,
        password=password,
        dsn=dsn,
        min=2,
        max=self.pool_size,
        increment=1,
        threaded=True
        # external_auth=False is default, no need to specify
    )
```

### Option 3: Dynamic Selection (Recommended for PROMISE AI)

Add this to your Oracle Adapter:

```python
def _create_pool(self):
    """Create Oracle connection pool - auto-detect auth method"""
    import os
    
    # Check if using Kerberos/external auth
    use_kerberos = os.getenv('ORACLE_USE_KERBEROS', 'false').lower() == 'true'
    
    if use_kerberos:
        # Kerberos authentication
        host = os.getenv('ORACLE_HOST')
        port = os.getenv('ORACLE_PORT', '1521')
        service_name = os.getenv('ORACLE_SERVICE_NAME')
        
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        logger.info(f"🔐 Using Kerberos authentication for {host}:{port}/{service_name}")
        
        return cx_Oracle.SessionPool(
            dsn=dsn,
            min=2,
            max=self.pool_size,
            increment=1,
            threaded=True,
            external_auth=True  # Kerberos/OS auth
        )
    else:
        # Standard username/password authentication
        user = os.getenv('ORACLE_USER')
        password = os.getenv('ORACLE_PASSWORD')
        host = os.getenv('ORACLE_HOST')
        port = os.getenv('ORACLE_PORT', '1521')
        service_name = os.getenv('ORACLE_SERVICE_NAME')
        
        dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
        logger.info(f"🔑 Using username/password for {user}@{host}:{port}/{service_name}")
        
        return cx_Oracle.SessionPool(
            user=user,
            password=password,
            dsn=dsn,
            min=2,
            max=self.pool_size,
            increment=1,
            threaded=True
        )
```

## Environment Variables Configuration

### For Standard Authentication (AWS RDS)
```bash
# .env file
ORACLE_USER="testuser"
ORACLE_PASSWORD="DbPasswordTest"
ORACLE_HOST="promise-ai-test-oracle.cgxf9inhpsec.us-east-1.rds.amazonaws.com"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="ORCL"
ORACLE_USE_KERBEROS="false"  # Use username/password
```

### For Kerberos Authentication
```bash
# .env file
ORACLE_HOST="your-kerberos-db-host.example.com"
ORACLE_PORT="1521"
ORACLE_SERVICE_NAME="ORCL"
ORACLE_USE_KERBEROS="true"  # Use Kerberos
# DO NOT set ORACLE_USER and ORACLE_PASSWORD for Kerberos
```

## Additional Kerberos Requirements

If using Kerberos authentication, ensure:

1. **Kerberos client is configured**:
   ```bash
   # /etc/krb5.conf should be properly configured
   ```

2. **Valid Kerberos ticket**:
   ```bash
   # Obtain ticket
   kinit username@REALM
   
   # Verify ticket
   klist
   ```

3. **Oracle Instant Client with GSSAPI support**:
   ```bash
   # Install appropriate Oracle Client
   # Ensure libclntsh.so includes GSSAPI support
   ```

4. **Oracle sqlnet.ora configuration** (if needed):
   ```
   SQLNET.AUTHENTICATION_SERVICES = (KERBEROS5)
   ```

## Testing

### Test Kerberos Connection
```python
import cx_Oracle
import os

host = os.getenv('ORACLE_HOST')
port = os.getenv('ORACLE_PORT', '1521')
service_name = os.getenv('ORACLE_SERVICE_NAME')

dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

try:
    # Test with Kerberos
    pool = cx_Oracle.SessionPool(
        dsn=dsn,
        min=1,
        max=2,
        external_auth=True
    )
    conn = pool.acquire()
    print("✅ Kerberos connection successful!")
    print(f"Connected as: {conn.username}")
    conn.close()
    pool.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Test Standard Authentication
```python
import cx_Oracle
import os

user = os.getenv('ORACLE_USER')
password = os.getenv('ORACLE_PASSWORD')
host = os.getenv('ORACLE_HOST')
port = os.getenv('ORACLE_PORT', '1521')
service_name = os.getenv('ORACLE_SERVICE_NAME')

dsn = cx_Oracle.makedsn(host, port, service_name=service_name)

try:
    # Test with username/password
    pool = cx_Oracle.SessionPool(
        user=user,
        password=password,
        dsn=dsn,
        min=1,
        max=2
    )
    conn = pool.acquire()
    print("✅ Standard authentication successful!")
    print(f"Connected as: {conn.username}")
    conn.close()
    pool.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Common Errors

### Error 1: "ORA-01017: invalid username/password"
**Cause**: Using `external_auth=True` but Oracle isn't configured for Kerberos
**Fix**: Either configure Kerberos properly or use standard auth (remove `external_auth=True`)

### Error 2: "TypeError: keyword argument 'user' is not supported with external_auth"
**Cause**: Passing `user` and `password` with `external_auth=True`
**Fix**: Remove user/password parameters when using `external_auth=True`

### Error 3: "ORA-12154: TNS:could not resolve the connect identifier"
**Cause**: DSN is malformed or service name is incorrect
**Fix**: Verify ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME

### Error 4: "KRB5: Credentials cache file not found"
**Cause**: No valid Kerberos ticket
**Fix**: Run `kinit username@REALM` to obtain ticket

## Summary

**Key Rule**: 
- `external_auth=True` → **DO NOT** pass `user`/`password`
- Standard auth → **MUST** pass `user`/`password`, **DO NOT** use `external_auth=True`

Choose one authentication method and configure accordingly!
