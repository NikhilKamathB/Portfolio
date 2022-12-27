# Fab file to automate django website deployment.

import os
from dotenv import load_dotenv
from fabric.tasks import task
from fabric import Connection
from invoke import run as local
load_dotenv()


USER = os.getenv("USER")
HOST = os.getenv("HOST")
SERVER_NAME = os.getenv('SERVER_NAME')
PEM_FILE = os.getenv("PEM_FILE")
GIT_REPO = os.getenv("GIT_REPO")
PROJECT = os.getenv("PROJECT")
PROJECT_500_HTML = os.getenv("PROJECT_500_HTML")
PROJECT_DJANGO_ROOT = os.getenv("PROJECT_DJANGO_ROOT")
PROJECT_DJANGO_WSGI_APP = os.getenv("PROJECT_DJANGO_WSGI_APP")
PROJECT_STATIC_FOLDER_NAME = os.getenv("PROJECT_STATIC_FOLDER_NAME")

print('\nBasic settings')
print(f'User = {USER}')
print(f'HOST = {HOST}')
print(f'SERVER_NAME = {SERVER_NAME}')
print(f'PEM_FILE = {PEM_FILE}')
print(f'PROJECT = {PROJECT}')
print(f'PROJECT_500_HTML = {PROJECT_500_HTML}')
print(f'PROJECT_DJANGO_ROOT = {PROJECT_DJANGO_ROOT}')
print(f'PROJECT_DJANGO_WSGI_APP = {PROJECT_DJANGO_WSGI_APP}')
print(f'PROJECT_STATIC_FOLDER_NAME = {PROJECT_STATIC_FOLDER_NAME}\n')

CONNECT_KWARGS = {"key_filename":[PEM_FILE]}
CONN = Connection(host=HOST, user=USER, connect_kwargs=CONNECT_KWARGS)

@task
def demo(ctx, folder):
    with CONN.cd(f"{folder}"):
        CONN.run(f'''cat > temp.txt << EOF
This is a demo text file.
It will be deleted after running this fab function.
EOF
''')
        CONN.run("cat temp.txt")
        CONN.run("wc -c temp.txt")
        CONN.run("rm -rf temp.txt")

# Misc actions.
@task 
def pwd(ctx):
    CONN.run(f"pwd")

@task 
def ls(ctx, folder):
    CONN.run(f"ls {folder}")

@task 
def cat(ctx, folder, file):
    with CONN.cd(folder):
        CONN.run(f"cat {file}")

@task
def mv(ctx, src, dest):
    CONN.run(f"mv {src} {dest}")

@task
def mkdir(ctx, path):
    CONN.run(f"mkdir {path} -p")

@task
def touch(ctx, file):
    CONN.run(f"touch {file}")

@task
def rm(ctx, path):
    CONN.run(f"rm -rf {path}")

# System setup.
@task
def apt_update(ctx):
    CONN.sudo("apt-get update -y")

@task
def install_nginx(ctx):
    CONN.sudo("apt install nginx -y")

@task
def install_git(ctx):
    CONN.sudo("apt install git -y")

@task
def install_virtualenv(ctx):
    CONN.sudo("apt-get install python3-pip -y")
    CONN.run("python3 -m pip install virtualenv")

# Git actions.
@task
def git_clone(ctx):
    print(f"git clone {GIT_REPO}")
    with CONN.cd(f"~/"):
        CONN.run(f"rm -rf {PROJECT}")
        CONN.run(f"git clone {GIT_REPO}", pty=True)

# Application specific.
@task
def create_venv(ctx):
    with CONN.cd(f"~/{PROJECT}"):
        CONN.run("python3 -m virtualenv venv")

@task
def install_requirements(ctx, branch='master'):
    with CONN.cd(f"~/{PROJECT}/"):
        CONN.run(f"git checkout -f origin/{branch}")
        CONN.run("source venv/bin/activate")
        with CONN.cd(f"~/{PROJECT}/{PROJECT_DJANGO_ROOT}/"):
            CONN.run(f"~/{PROJECT}/venv/bin/pip install -r requirements.txt")

# Gunicorn setup.
@task
def create_gunicorn_service(ctx):
    CONN.run(f'''cat > {PROJECT}.socket << EOF
[Unit]
Description={PROJECT} socket

[Socket]
ListenStream=/run/{PROJECT}.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
EOF
''')
    print("Created socket file")
    CONN.sudo(f'''cat > {PROJECT}.service << EOF
[Unit]
Description={PROJECT} daemon
Requires={PROJECT}.socket
After=network.target

[Service]
Type=notify
User={USER}
Group={USER}
RuntimeDirectory=gunicorn
WorkingDirectory=/home/{USER}/{PROJECT}/{PROJECT_DJANGO_ROOT}
ExecStart=/home/{USER}/{PROJECT}/venv/bin/gunicorn {PROJECT_DJANGO_WSGI_APP}.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
''')
    print("Created service file")
    CONN.sudo(f"mv {PROJECT}.socket /etc/systemd/system/")
    CONN.sudo(f"mv {PROJECT}.service /etc/systemd/system/")
    CONN.sudo("systemctl daemon-reload")
    CONN.sudo(f"systemctl enable --now {PROJECT}.socket")

@task
def test_gunicorn(ctx):
    CONN.sudo(f"curl --unix-socket /run/{PROJECT}.sock http", user="www-data")

# Nginx setup.
# Note: remember to set the 'user' in '/etc/nginx/nginx.conf' to 'root'
@task
def create_nginx_config(ctx):
    CONN.sudo("rm -f /etc/nginx/sites-enabled/default")
    CONN.sudo(f"rm -f {PROJECT}.conf")
    CONN.run(f'''cat > {PROJECT}.conf << EOF
upstream {PROJECT}_server {{
  server unix:/run/{PROJECT}.sock fail_timeout=0;
}}

server {{

  listen 80;
  listen 443;
  server_name {SERVER_NAME};
  client_max_body_size 4G;
  access_log /var/log/nginx/{PROJECT}-access.log;
  error_log /var/log/nginx/{PROJECT}-error.log;
  keepalive_timeout 5;

  root /home/{USER}/{PROJECT}/{PROJECT_DJANGO_ROOT}/{PROJECT_STATIC_FOLDER_NAME};

  location / {{
    try_files \$uri @proxy_to_{PROJECT};
  }}

  location @proxy_to_{PROJECT} {{
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header Host \$http_host;
    proxy_redirect off;
    proxy_pass http://{PROJECT}_server;
  }}

  error_page 500 502 503 504 /500.html;
  location = /500.html {{
    root /home/{USER}/{PROJECT}/{PROJECT_DJANGO_ROOT}/{PROJECT_500_HTML}/500.html;
  }}

}}
EOF
''')
    CONN.sudo(f"rm -f /etc/nginx/sites-enabled/{PROJECT}.conf")
    CONN.sudo(f"mv {PROJECT}.conf /etc/nginx/sites-enabled/")
    CONN.sudo(f"nginx -t")
    CONN.sudo("systemctl restart nginx")

@task
def restart_nginx(ctx):
    CONN.sudo("systemctl restart nginx")

@task
def test_nginx(ctx):
    ctx.run(f"curl -i {HOST}")

# Deploy.
@task 
def put_env(ctx, env):
    basefile = os.path.basename(env)
    local(f"rsync -e 'ssh -i {PEM_FILE}' {env} ubuntu@{HOST}:~/{PROJECT}/{PROJECT_DJANGO_ROOT}/")
    if basefile != ".env": # rename to .env
        CONN.run(f"mv ~/{PROJECT}/{PROJECT_DJANGO_ROOT}/{basefile} ~/{PROJECT}/{PROJECT_DJANGO_ROOT}/.env")

@task
def deploy(ctx, branch="master"):
    with CONN.cd(f"~/{PROJECT}/"):
        CONN.run("git fetch --all")
        CONN.run(f"git checkout -f origin/{branch}")
        CONN.run("source venv/bin/activate")
        with CONN.cd(f"~/{PROJECT}/{PROJECT_DJANGO_ROOT}/"):
            CONN.run(f"~/{PROJECT}/venv/bin/pip install -r requirements.txt")
            CONN.run(f"~/{PROJECT}/venv/bin/python manage.py migrate")
            CONN.run(f"~/{PROJECT}/venv/bin/python manage.py collectstatic --noinput")
    CONN.sudo(f"systemctl restart {PROJECT}.service")

@task 
def clean(ctx):
    CONN.run(f"rm -rf {PROJECT}/")