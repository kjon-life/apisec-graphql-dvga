# DVGA API Application

A GraphQL wrapper around the SpaceX REST API, designed for use with APIsec testing.

When we run our server with `uv run uvicorn spacexdata.main:app --reload`, it creates a GraphQL endpoint that translates GraphQL queries into REST API calls to the official SpaceX API.

We are using the v5 [r-spacex/SpaceX-API](https://github.com/r-spacex/SpaceX-API) as our data source with these distinctions:  
1. Their API has tranistioned to REST v5 [https://api.spacexdata.com/v5/](https://api.spacexdata.com/v5/)  
2. We have created a GraphQL wrapper around it to:
    * Make it compatible for testing GraphQL with APIsec
    * Expose a GraphQL interface to their REST API
    * Generate SDL for current testing, and JSON introspection for future testing in APIsec
3. Run a simple introspection on the app
    ```bash
    curl -X POST http://54.234.103.190:9070/graphql -H "Content-Type: application/json" -d '{"query": "query { __schema { types { name } } }"}' | python3 -m json.tool
    ```
4. Run a more detailed introspection query, which we would expect is similar to what APIsec might generate
    ```bash
    curl -X POST http://54.234.103.190:9070/graphql -H "Content-Type: application/json" -d '{"query": "query { __schema { queryType { name fields { name type { name kind } } } } }"}' | python3 -m json.tool
    ```
5. Run the complete introspection query
    ```bash
    curl -X POST http://54.234.103.190:9070/graphql -H "Content-Type: application/json" -d '{"query": "query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } }"}' | python3 -m json.tool
    ```

## Project Structure  
```bash
spacexdata/
├── spacexdata/
│   ├── __init__.py
│   ├── main.py (FastAPI + Strawberry GraphQL app)
│   ├── schema/
│   │   └── types.py (GraphQL type definitions)
│   ├── resolvers/
│   │   └── launch_resolver.py (resolvers that call the REST API)
│   └── services/
│       └── spacex_api.py (handles REST API calls to api.spacexdata.com)
└── scripts/
    └── generate_sdl.py (generates schema for APIsec)  
```

## Setup

1. Create a virtual environment:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
# v1 did not package w pyproject.toml
#uv pip install -r requirements.txt
# v2 does
uv pip install -e .
```

## Running the Server

Start the server with:
```bash
uvicorn spacexdata.main:app --reload
```

The GraphQL playground will be available at: http://localhost:8000/graphql

## Generating Schema

To generate the introspection schema for APIsec:
```bash
uv run python scripts/generate_schema.py
```

SDL Schema is generated as 'schema.graphql'
JSON Introspection Schema is generated as 'schema.json'

Note:  To generate just the SDL for APIsec:
```bash
uv run python scripts/generate_sdl.py
```

## EC2 Deployment  
Based on the [list of common TCP and UDP port numbers](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers) we chose 9070-9079 to deploy APIs on EC2.

### IAM User
```bash
ssh -vvv -o "IdentitiesOnly yes" -i "/Users/trust/.ssh/jonwilliams.pem" ec2-user@ec2-54-234-103-190.compute-1.amazonaws.com
```

## Deployment Status

The API is currently deployed and accessible at:
- Production: http://54.234.103.190:9070/graphql

### Deployment Information
- Hosting: AWS EC2
- Application Port: 9070
- Reverse Proxy: nginx
- Process Manager: systemd

## Local Development

### EC2 Configuration

We need asdf to manage Python
git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0
git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0

we need go (newer than what amazon has in yum)
wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

sudo yum groupinstall "Development Tools"


  125  wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
  127  sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
  128  echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
  129  echo 'export GOPATH=$HOME/go' >> ~/.bashrc
  130  echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
  131  source ~/.bashrc
  132  go version
  133  pwd

  181  git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0
  182  cd asdf
  183  make
  184  sudo cp ./asdf /usr/local/bin
  185  sudo chmod +x /usr/local/bin
  186  asdf
  187  asdf --version

but then python buiild fails 
itried
sudo yum install -y gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel

asdf uninstall python 3.11.11

asdf install python 3.11.11

  198  asdf install python 3.11.11
  199  asdf plugin add uv
  200  asdf plugin add nodejs
  201  asdf install nodejs latest
  202  asdf install uv latest

  [ec2-user@ip-172-31-29-43 asdf]$ asdf list
nodejs
  23.9.0
python
 *3.11.11
uv
  0.6.6

asdf set -u python 3.11.11
asdf set -u nodejs 23.9.0
asdf set -u uv 0.6.6

in local
git init
git add . && git commit -m "Initial commit: SpaceX GraphQL API project setup"
created empty repo at: https://github.com/kjon-life/apisec-graphql-qa
git remote add origin https://github.com/kjon-life/apisec-graphql-qa.git && git branch -M main && git push -u origin main

we can also update the remote to use ssh
git remote set-url origin git@github.com:kjon-life/apisec-graphql-qa.git && git branch -M main && git push -u origin main

so we have an environment on EC2
[ec2-user@ip-172-31-29-43 asdf]$ uv --version
uv 0.6.6
[ec2-user@ip-172-31-29-43 asdf]$ python --version
Python 3.11.11
[ec2-user@ip-172-31-29-43 asdf]$ node --version
v23.9.0

and the git repo to clone
git@github.com:kjon-life/apisec-graphql-qa.git

./scripts/deploy.sh
writes to the app directory to ~/apps/spacexdata
The repository URL uses SSH
Uses $USER instead of hardcoded ec2-user
We sudo for commands that require root access
Updated domain to spacexdata.kjon.life

copy my key to the server 
scp my deploy.sh to the server
chmod +x on deploy.sh

sudo yum install -y nginx
sudo yum install -y nginx && sudo systemctl start nginx && sudo systemctl enable nginx && ./deploy.sh
please note that deploy.sh is idempotent

(I had to run it twice because I forgot to install nginx)
Created symlink /etc/systemd/system/multi-user.target.wants/spacexdata.service → /etc/systemd/system/spacexdata.service.
[2025-03-12 17:51:49] Deployment completed successfully!
[2025-03-12 17:51:49] Next steps:
[2025-03-12 17:51:49] 1. Configure AWS security group to allow traffic on port 9070
[2025-03-12 17:51:49] 2. Set up SSL certificate with Let's Encrypt

let's check the current NETWORK
sudo ss -tulpn | grep -E ':80|:443|:9070'

check the status of the appllication
systemctl status spacexdata

why did it fail to start?
journalctl -u spacexdata.service -n 50 | cat

systemd was configured to run main:app from the root dir not the apps/spacexdata
sudo sed -i 's/main:app/spacexdata.main:app/' /etc/systemd/system/spacexdata.service && sudo systemctl daemon-reload && sudo systemctl restart spacexdata && systemctl status spacexdata

now we check if it is listeing on the port 9070
ss -tulpn | grep 9070

so I can configure this with DNS
http://spacexdata.kjon.life
http://spacexdata.kjon.life:9070

but for now we will 
http://54.234.103.190:9070
http://54.234.103.190

we need the instance-id for EC2
curl http://54.234.108.190/latest/meta-data/instance-id


In the EC2 console, select the running instance
`sg-0c8ce9629b0959a93 - launch-wizard-2`
In the "Security" tab, click on the security group link 
Click "Edit inbound rules"
Click "Add rule"
Set the following values:

Type: Custom TCP
Protocol: TCP
Port range: 9070
Source: Anywhere (0.0.0.0/0) for public access or your specific IP
Description: SpaceXdata

```bash
http://54.234.103.190:9070/graphql
```

now we go to NG
https://cst.dev.apisecapps.com/
jon+dev@apisec.ai (CST DEV in pwSafe)

Add the application `SpaceXdata` with Host URL:
```
http://54.234.103.190:9070/
```
image.png

## Production Deployment

The application is deployed using a custom deployment script. To deploy:

1. SSH into the EC2 instance:
```bash
ssh -i "<key>.pem" ec2-user@54.234.103.190
```

2. Run the deployment script:
```bash
cd ~/apps/spacexdata
./scripts/deploy.sh
```

### Service Management

The application runs as a systemd service. Common commands:

```bash
# Check service status
sudo systemctl status spacexdata

# Restart service
sudo systemctl restart spacexdata

# View logs
journalctl -u spacexdata -f
```

### Monitoring

The application can be monitored through:
- systemd service status
- nginx access logs: `/var/log/nginx/access.log`
- nginx error logs: `/var/log/nginx/error.log`
- Application logs: via journalctl

# Appendix

### The Official SpaceX API is mnow primarily REST 
So we create a simple GraphQL server that wraps the SpaceX REST API
Generate the introspection schema and an SDL from our wrapper
Use the SDL file to register the application in APIsec

### Getting started
```bash
curl -X POST https://api.spacexdata.com/v4/graphql -H "Content-Type: application/json" -d '{"query": "query { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } }"}' | python3 -m json.tool > spacex_schema.json
```

No response

```
curl -X POST https://api.spacexdata.com/v4/graphql -H "Content-Type: application/json" -d '{"query": "query { __schema { types { name kind description } } }"}' -v

Note: Unnecessary use of -X or --request, POST is already inferred.
* Host api.spacexdata.com:443 was resolved.
* IPv6: (none)
* IPv4: 172.67.146.218, 104.21.79.181
*   Trying 172.67.146.218:443...
* Connected to api.spacexdata.com (172.67.146.218) port 443
* ALPN: curl offers h2,http/1.1
* (304) (OUT), TLS handshake, Client hello (1):
*  CAfile: /etc/ssl/cert.pem
*  CApath: none
* (304) (IN), TLS handshake, Server hello (2):
* (304) (IN), TLS handshake, Unknown (8):
* (304) (IN), TLS handshake, Certificate (11):
* (304) (IN), TLS handshake, CERT verify (15):
* (304) (IN), TLS handshake, Finished (20):
* (304) (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / AEAD-CHACHA20-POLY1305-SHA256 / [blank] / UNDEF
* ALPN: server accepted h2
* Server certificate:
*  subject: CN=spacexdata.com
*  start date: Feb 19 08:20:49 2025 GMT
*  expire date: May 20 09:17:57 2025 GMT
*  subjectAltName: host "api.spacexdata.com" matched cert's "*.spacexdata.com"
*  issuer: C=US; O=Google Trust Services; CN=WE1
*  SSL certificate verify ok.
* using HTTP/2
* [HTTP/2] [1] OPENED stream for https://api.spacexdata.com/v4/graphql
* [HTTP/2] [1] [:method: POST]
* [HTTP/2] [1] [:scheme: https]
* [HTTP/2] [1] [:authority: api.spacexdata.com]
* [HTTP/2] [1] [:path: /v4/graphql]
* [HTTP/2] [1] [user-agent: curl/8.7.1]
* [HTTP/2] [1] [accept: */*]
* [HTTP/2] [1] [content-type: application/json]
* [HTTP/2] [1] [content-length: 67]
> POST /v4/graphql HTTP/2
> Host: api.spacexdata.com
> User-Agent: curl/8.7.1
> Accept: */*
> Content-Type: application/json
> Content-Length: 67
> 
* upload completely sent off: 67 bytes
< HTTP/2 404 
< date: Wed, 12 Mar 2025 01:50:49 GMT
< content-type: text/plain; charset=utf-8
< content-length: 9
< access-control-allow-origin: *
< access-control-expose-headers: spacex-api-cache,spacex-api-response-time
< alt-svc: h3=":443"; ma=86400
< content-security-policy: default-src 'self';base-uri 'self';block-all-mixed-content;font-src 'self' https: data:;frame-ancestors 'self';img-src 'self' data:;object-src 'none';script-src 'self';script-src-attr 'none';style-src 'self' https: 'unsafe-inline';upgrade-insecure-requests
< expect-ct: max-age=0
< referrer-policy: no-referrer
< spacex-api-response-time: 0ms
< strict-transport-security: max-age=15552000; includeSubDomains
< vary: Origin
< x-content-type-options: nosniff
< x-dns-prefetch-control: off
< x-download-options: noopen
< x-frame-options: SAMEORIGIN
< x-permitted-cross-domain-policies: none
< x-xss-protection: 0
< cf-cache-status: DYNAMIC
< report-to: {"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v4?s=O4mvSxz92qNF%2F181IwhH1tL6T9Mva%2F%2BI0IY2%2Fmp8T3W%2Fnu8IiRjAmUkyortBDAMtacFR1RET5JP0u5wRSR3hNLN0n3Z8yRC2CWuLOyGLw4L%2FbRA8BkNK7cTn9tLyxqh1Mi%2Bz6y8%3D"}],"group":"cf-nel","max_age":604800}
< nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
< server: cloudflare
< cf-ray: 91efa495ef208114-ORD
< server-timing: cfL4;desc="?proto=TCP&rtt=25787&min_rtt=25782&rtt_var=5443&sent=4&recv=7&lost=0&retrans=0&sent_bytes=2897&recv_bytes=646&delivery_rate=112265&cwnd=247&unsent_bytes=0&cid=7b67ba1ffd1c7cd0&ts=201&x=0"
< 
* Connection #0 to host api.spacexdata.com left intact
Not Found%                                                                                                                                                                                    ```

## EC2 Configuration

We need asdf to manage Python
git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0
git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0

we need go (newer than what amazon has in yum)
wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

sudo yum groupinstall "Development Tools"


  125  wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
  127  sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
  128  echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
  129  echo 'export GOPATH=$HOME/go' >> ~/.bashrc
  130  echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
  131  source ~/.bashrc
  132  go version
  133  pwd

  181  git clone https://github.com/asdf-vm/asdf.git --branch v0.16.0
  182  cd asdf
  183  make
  184  sudo cp ./asdf /usr/local/bin
  185  sudo chmod +x /usr/local/bin
  186  asdf
  187  asdf --version

but then python buiild fails 
itried
sudo yum install -y gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel

asdf uninstall python 3.11.11

asdf install python 3.11.11

  198  asdf install python 3.11.11
  199  asdf plugin add uv
  200  asdf plugin add nodejs
  201  asdf install nodejs latest
  202  asdf install uv latest

  [ec2-user@ip-172-31-29-43 asdf]$ asdf list
nodejs
  23.9.0
python
 *3.11.11
uv
  0.6.6

asdf set -u python 3.11.11
asdf set -u nodejs 23.9.0
asdf set -u uv 0.6.6

in local
git init
git add . && git commit -m "Initial commit: SpaceX GraphQL API project setup"
created empty repo at: https://github.com/kjon-life/apisec-graphql-qa
git remote add origin https://github.com/kjon-life/apisec-graphql-qa.git && git branch -M main && git push -u origin main

we can also update the remote to use ssh
git remote set-url origin git@github.com:kjon-life/apisec-graphql-qa.git && git branch -M main && git push -u origin main

so we have an environment on EC2
[ec2-user@ip-172-31-29-43 asdf]$ uv --version
uv 0.6.6
[ec2-user@ip-172-31-29-43 asdf]$ python --version
Python 3.11.11
[ec2-user@ip-172-31-29-43 asdf]$ node --version
v23.9.0

and the git repo to clone
git@github.com:kjon-life/apisec-graphql-qa.git

./scripts/deploy.sh
writes to the app directory to ~/apps/spacexdata
The repository URL uses SSH
Uses $USER instead of hardcoded ec2-user
We sudo for commands that require root access
Updated domain to spacexdata.kjon.life

copy my key to the server 
scp my deploy.sh to the server
chmod +x on deploy.sh

sudo yum install -y nginx
sudo yum install -y nginx && sudo systemctl start nginx && sudo systemctl enable nginx && ./deploy.sh
please note that deploy.sh is idempotent

(I had to run it twice because I forgot to install nginx)
Created symlink /etc/systemd/system/multi-user.target.wants/spacexdata.service → /etc/systemd/system/spacexdata.service.
[2025-03-12 17:51:49] Deployment completed successfully!
[2025-03-12 17:51:49] Next steps:
[2025-03-12 17:51:49] 1. Configure AWS security group to allow traffic on port 9070
[2025-03-12 17:51:49] 2. Set up SSL certificate with Let's Encrypt

let's check the current NETWORK
sudo ss -tulpn | grep -E ':80|:443|:9070'

check the status of the appllication
systemctl status spacexdata

why did it fail to start?
journalctl -u spacexdata.service -n 50 | cat

systemd was configured to run main:app from the root dir not the apps/spacexdata
sudo sed -i 's/main:app/spacexdata.main:app/' /etc/systemd/system/spacexdata.service && sudo systemctl daemon-reload && sudo systemctl restart spacexdata && systemctl status spacexdata

now we check if it is listeing on the port 9070
ss -tulpn | grep 9070

so I can configure this with DNS
http://spacexdata.kjon.life
http://spacexdata.kjon.life:9070

but for now we will 
http://54.234.103.190:9070
http://54.234.103.190

we need the instance-id for EC2
curl http://54.234.108.190/latest/meta-data/instance-id


In the EC2 console, select the running instance
`sg-0c8ce9629b0959a93 - launch-wizard-2`
In the "Security" tab, click on the security group link 
Click "Edit inbound rules"
Click "Add rule"
Set the following values:

Type: Custom TCP
Protocol: TCP
Port range: 9070
Source: Anywhere (0.0.0.0/0) for public access or your specific IP
Description: SpaceXdata

```bash
http://54.234.103.190:9070/graphql
```

now we go to NG
https://cst.dev.apisecapps.com/
jon+dev@apisec.ai (CST DEV in pwSafe)

Add the application `SpaceXdata` with Host URL:
```
http://54.234.103.190:9070/
```
# dvgsa notes
```
git clone https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application.git /tmp/dvga-ref && ls -la /tmp/dvga-ref/core # schema should be found in core
cat /tmp/dvga-ref/core/models.py # understand schema structure  
ls -R /tmp/dvga-ref/core/schema/ # check the schema definition  

# root directory does not seem to have schema files   
# check the views to find out where the schema is defined
cat /tmp/dvga-ref/core/views.py

```

```

subscription_server = GeventSubscriptionServerCustom(schema)

sockets = Sockets(app)

@sockets.route('/subscriptions')
def echo_socket(ws):

  subscription_server.handle(ws)

  return []


gql_middlew = [
  middleware.CostProtectionMiddleware(),
  middleware.DepthProtectionMiddleware(),
  middleware.IntrospectionMiddleware(),
  middleware.processMiddleware(),
  middleware.OpNameProtectionMiddleware()
]

igql_middlew = [
  middleware.IGQLProtectionMiddleware()
]

class CustomBackend(GraphQLCoreBackend):
    def __init__(self, executor=None):
        super().__init__(executor)
        self.execute_params['allow_subscriptions'] = True

app.add_url_rule('/graphql', view_func=OverriddenView.as_view(
  'graphql',
  schema=schema,
  middleware=gql_middlew,
  backend=CustomBackend(),
  batch=True
))

app.add_url_rule('/graphiql', view_func=OverriddenView.as_view(
  'graphiql',
  schema = schema,
  backend=CustomBackend(),
  graphiql = True,
  middleware = igql_middlew,
  format_error=format_custom_error
))
```
update our schema.graphql file with DVGA's schema:
```bash
schema.graphql
```
this inbcludes
Custom directives (@show_network, @skip, @deprecated)
All types (User, Paste, Owner, Audit)
Input types (UserInput)
All queries with their parameters
All mutations with their payloads
Subscription support
Union type for search results
*  all the vulnerable functionality from DVGA, such as:
System diagnostics with command execution
System debug with PS command access
Import paste with potential SSRF
File upload capabilities
Authentication system
```
we are matrching the DVGA structure exactly in ouyr app
we have a main app.py in the root
we have a basic config.py in the root (includes db settings)

