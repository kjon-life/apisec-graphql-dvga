# EC2 Deployment Design Document for SpaceX GraphQL API

## Problem Statement
Deploy the SpaceX GraphQL API to an EC2 instance with proper security, monitoring, and high availability considerations.

## Requirements
✅ 1. Validate IAM connection and SSH access
✅ 2. Create automated deployment script
✅ 3. Configure systemd service for automatic startup
✅ 4. Set up nginx reverse proxy
⬜ 5. Configure SSL with Let's Encrypt
✅ 6. Configure AWS security group for port access (9070-9079)

## Technical Design

### 1. IAM and SSH Validation ✅
- ✅ Verify SSH access using the configured key pair
- ✅ Test command: `ssh -i <key_pair.pem> ec2-user@<instance-ip>`

### 2. Deployment Script ✅
Create `deploy.sh` with the following steps:
```bash
✅ 1. Clone repository
✅ 2. Install dependencies (Python, uv)
✅ 3. Set up virtual environment
✅ 4. Install application dependencies
✅ 5. Copy configuration files
✅ 6. Restart systemd service
```

### 3. Systemd Service Configuration ✅
Create service file: `/etc/systemd/system/spacexdata.service`
```ini
[Unit]
Description=SpaceX GraphQL API Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/apps/spacexdata
Environment=PATH=/home/ec2-user/apps/spacexdata/.venv/bin:$PATH
ExecStart=/home/ec2-user/apps/spacexdata/.venv/bin/uvicorn spacexdata.main:app --host 0.0.0.0 --port 9070
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration ✅
Create nginx config: `/etc/nginx/conf.d/spacexdata.conf`
```nginx
server {
    listen 80;
    server_name spacexdata.kjon.life;

    location / {
        proxy_pass http://localhost:9070;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 5. SSL Configuration ⬜
Use Certbot for Let's Encrypt SSL:
```bash
1. Install certbot
2. Generate certificate
3. Configure automatic renewal
```

### 6. AWS Security Group Configuration ✅
Required ports:
- ✅ 22 (SSH)
- ✅ 80 (HTTP)
- ⬜ 443 (HTTPS) - Pending SSL setup
- ✅ 9070 (Application)

## Implementation Plan

### Phase 1: Initial Setup and Validation ✅
1. ✅ Validate SSH access
2. ✅ Create deployment script
3. ✅ Test manual deployment

### Phase 2: Service Configuration ✅
1. ✅ Set up systemd service
2. ✅ Configure nginx
3. ✅ Test service reliability

### Phase 3: Security and SSL ⬜
1. ⬜ Configure Let's Encrypt
2. ✅ Set up AWS security groups
3. ⬜ Test SSL configuration

### Phase 4: Monitoring and Maintenance ⬜
1. ⬜ Set up logging
2. ⬜ Configure monitoring
3. ⬜ Document maintenance procedures

## Current Status
- ✅ Application is deployed and running
- ✅ Available at http://54.234.103.190:9070/graphql
- ⬜ DNS configuration pending
- ⬜ SSL configuration pending
- ⬜ Monitoring setup pending

## Testing Strategy
1. Deployment validation
2. Service startup tests
3. SSL certificate validation
4. Load testing
5. Failover testing

## Rollback Plan
1. Keep previous deployment version
2. Document rollback procedures
3. Test rollback process

## Security Considerations
1. Use secure key management
2. Implement proper firewall rules
3. Regular security updates
4. SSL certificate monitoring

## Monitoring and Logging
1. Application logs
2. Nginx access logs
3. System metrics
4. SSL certificate expiration monitoring 