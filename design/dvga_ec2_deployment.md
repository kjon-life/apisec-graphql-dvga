# DVGA EC2 Deployment Design Document

## Overview
This document outlines the plan for deploying the Damn Vulnerable GraphQL Application (DVGA) on AWS EC2.

## Current State
- DVGA is a Flask-based GraphQL application
- Currently has Docker support but no direct EC2 deployment configuration
- Uses pip and requirements.txt for dependency management
- No structured deployment scripts or configuration

## Target State
1. Modern Python Development Environment
   - asdf for Python version management
   - uv for dependency management
   - Structured project configuration using pyproject.toml

2. Deployment Infrastructure
   - EC2 instance configuration
   - Systemd service for process management
   - Nginx as reverse proxy
   - SSL/TLS configuration
   - Environment variable management

3. Deployment Scripts
   - Instance setup scripts
   - Application deployment scripts
   - Monitoring and logging setup

## Implementation Phases

### Phase 1: Development Environment Modernization
1. Add .tool-versions for asdf
2. Convert requirements.txt to pyproject.toml
3. Generate uv.lock file
4. Update documentation

### Phase 2: EC2 Configuration
1. Create EC2 instance setup script
2. Configure security groups
3. Set up Nginx configuration
4. Create systemd service file

### Phase 3: Deployment Automation
1. Create deployment scripts
2. Set up logging and monitoring
3. Document deployment process

## Security Considerations
- As this is a deliberately vulnerable application, it should be deployed in a controlled environment
- Restrict access to specific IP ranges
- Use security groups to limit exposure
- Document security warnings and usage guidelines

## Testing Strategy
1. Local deployment testing using similar configuration
2. EC2 deployment testing
3. Load testing
4. Security configuration verification

## Rollback Plan
- Document rollback procedures
- Keep backup of previous configurations
- Version control for all configuration files

## Timeline
- Phase 1: 1 day
- Phase 2: 2 days
- Phase 3: 1 day

## Success Criteria
1. Application successfully runs on EC2
2. All vulnerabilities remain functional (as intended)
3. Deployment process is documented and repeatable
4. Monitoring and logging in place 