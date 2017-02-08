from subprocess import Popen, call
import os, sys, re


# if not hasattr(sys, 'real_prefix'):
# 	print('Please Run This Script on Python virtualenv')
# 	sys.exit(0)

try:
	import settings
except:
	print('Please Execute this script in Django Project Folder where settings.py located')
	print('pwd: {}'.format(__file__))
	sys.exit(0)
else:
	print('Starting Bootstrap linkage on django project and nginx...')

PROJECT_NAME = os.path.basename(settings.BASE_DIR)
SERVER_IP = 'localhost'
SERVE_PORT = 8000
NGINX_CONF_PATH = os.path.join(settings.BASE_DIR, '{}_nginx.conf'.format(PROJECT_NAME))
UWSGI_INI_PATH = os.path.join(settings.BASE_DIR, '{}_uwsgi.ini'.format(PROJECT_NAME))
UWSGI_PARAMS_PATH = os.path.join(settings.BASE_DIR, 'uwsgi_params')
VIRTUALENV_PATH = os.path.dirname(settings.BASE_DIR)

try:
	MEDIA_ROOT = os.path.abspath(settings.MEDIA_ROOT)
except:
	MEDIA_ROOT = os.path.abspath(os.path.join(settings.BASE_DIR, '/media'))

try:
	STATIC_ROOT = os.path.abspath(settings.STATIC_ROOT)
except:
	STATIC_ROOT = os.path.abspath(os.path.join(settings.BASE_DIR, '/collectstatic'))
	# call(['python3','../manage.py', 'collectstatic','--noinput'])

# install esstional app

call(['apt-get','-y', '-f', 'install','nginx-full'])
call(['pip3', 'install', 'uwsgi'])





uwsgi_params = '''
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;

'''


uwsgi_ini = '''
[uwsgi]
chdir		= {BASE_DIR}
module		= {PROJECT_NAME}.wsgi
home		= {VIRTUALENV_PATH}
master		= true
process		= 1
socket		= /tmp/{PROJECT_NAME}.sock
chmod-socket	= 666
vacuum		= true

'''.format(BASE_DIR= settings.BASE_DIR, PROJECT_NAME= PROJECT_NAME, VIRTUALENV_PATH= VIRTUALENV_PATH)




nginx_conf = '''
# {PROJECT_NAME}_nginx.conf

upstream django {{
	server unix:///tmp/{PROJECT_NAME}.sock;
}}

server {{
	listen		{LISTEN_PORT};
	server_name	{SERVER_NAME};
	charset		utf-8;
	client_max_body_size	75M;

	location /media {{
		alias {MEDIA_ROOT};
	}}
	location /static {{
		alias {STATIC_ROOT};
	}}
	location / {{
		uwsgi_pass	django;
		include {UWSGI_PARAMS_PATH};
	}}

}}
'''.format(PROJECT_NAME= PROJECT_NAME, 
	LISTEN_PORT=SERVE_PORT, SERVER_NAME= SERVER_IP, MEDIA_ROOT=MEDIA_ROOT, STATIC_ROOT=STATIC_ROOT,
	UWSGI_PARAMS_PATH= UWSGI_PARAMS_PATH)


print('Creating {}...'.format(UWSGI_INI_PATH))
with open(UWSGI_INI_PATH, 'wt') as fp:
	fp.write(uwsgi_ini)

print('Creating {}...'.format(NGINX_CONF_PATH))
with open(NGINX_CONF_PATH, 'wt') as fp:
	fp.write(nginx_conf)

print('Creating {}...'.format(UWSGI_PARAMS_PATH))
with open(UWSGI_PARAMS_PATH, 'wt') as fp:
	fp.write(uwsgi_params)


print('Create Soft Link {} to /etc/nginx/sites-enabled/'.format(NGINX_CONF_PATH))
call(['ln','-s', NGINX_CONF_PATH, '/etc/nginx/sites-enabled/'])

print('Done!')
call(['service', 'nginx', 'restart'])
print('cd to dir where inifile located and input: uwsgi --ini *.ini')
