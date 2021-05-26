import subprocess
import urllib
import urllib.error
import docker


def run_command(cmd):
    try:
        process = subprocess.run(
            cmd.split(), stdout=subprocess.PIPE)
        if process.returncode > 0:
            return None
        return process.stdout.decode("utf-8").strip()
    except:
        return None


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
