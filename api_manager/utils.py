import subprocess
import urllib
import urllib.error
import docker
import json
import time


def prepare_db_config(db):
    with open(f"/tmp/{db.config_file_name}", 'w') as f:
        f.write(generate_json(db))


def run_command(cmd):
    try:
        process = subprocess.run(
            cmd.split(), stdout=subprocess.PIPE)
        time.sleep(1)
        if process.returncode > 0:
            return None
        return process.stdout.decode("utf-8").strip()
    except:
        return None


def check_docker_daemon():
    try:
        client = docker.from_env()
        return client is not None
    except:
        return False


def stop_docker(docker_id):
    try:
        client = docker.from_env()
        client.containers.get(docker_id).stop()
        return True
    except:
        return False


def check_status(db):
    try:
        url = f"http://127.0.0.1:{db.port_number}{db.status_url}"
        http_req = urllib.request.urlopen(url, timeout=3)
    except urllib.error.URLError:
        return -1
    return http_req.getcode()


def generate_json(db):
    methods_dict = {i.name: i.query_text for i in db.querymethod_set.all()}
    methods = [{name: query} for name, query in methods_dict.items()]
    config = {
        'server': db.server_ip,
        'database': db.db_name,
        'user': db.db_username,
        'password': db.db_password,
        'methods': methods
    }
    return json.dumps(config)
