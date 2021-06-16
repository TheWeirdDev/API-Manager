import subprocess
import urllib
import urllib.error
import docker
from docker.errors import DockerException, NotFound, ContainerError
import json
import time


def prepare_db_config(db):
    """
    Preapares the database config file to be used in a container
    The config will be saved in /tmp/ if it's not already saved.
    """
    with open(f"/tmp/{db.config_file_name}", 'w') as f:
        f.write(generate_json(db))


def run_command(cmd):
    """
    Runs the shell command to start a database api

    the docker process will print a docker id,
    and it will be captured and saved.
    The program will use this id to check the status of the container.

    The return value of this function is a tuple,
    the first item of which is the docker id and
    the second item is the error message (if any)
    """
    try:
        process = subprocess.run(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(1)
        # The output will be either the docker id or error message based on the error code
        # If there was an error, docker id should be `None`
        if process.returncode > 0:
            return (None, process.stderr.decode("utf-8").strip())
        # If it was successful, error message should be `None`
        return (process.stdout.decode("utf-8").strip(), None)
    except:
        return (None, process.stderr.decode("utf-8").strip())


def check_docker_daemon():
    """
    Check if the docker service is running by simply calling `from_env` function
    If the service is not running, a DockerException will be raised
    """
    try:
        client = docker.from_env()
        return client is not None
    except DockerException:
        return False


def check_container_exists(docker_id):
    """
    Given a docker id, this function returns a boolean
    corresponding to the existance of that container.
    The result is only 'True' if the container is running
    """
    try:
        client = docker.from_env()
        container = client.containers.get(docker_id)
        return container is not None and container.status == 'running'
    except (DockerException, NotFound, ContainerError) as e:
        return False


def stop_docker_container(docker_id):
    """
    Stops a docker container and returns 'True' if the opeation
    was successful
    """
    try:
        client = docker.from_env()
        client.containers.get(docker_id).stop(timeout=5)
        return True
    except (DockerException, NotFound, ContainerError) as e:
        return False


def check_status(db):
    """
    Checks the health of a database api by calling the 'status_url'
    of that container, if the result code is 200, then it's healthy
    """
    try:
        url = f"http://127.0.0.1:{db.port_number}{db.status_url}"
        http_req = urllib.request.urlopen(url, timeout=3)
    except urllib.error.URLError:
        return -1
    return http_req.getcode()


def generate_json(db):
    """
    Generates a json config for the database api
    """

    # Make a dictionary of the query methods for the database
    methods_dict = {i.name: i.query_text for i in db.querymethod_set.all()}
    # Split each method name and query into a new dictionary
    # then add each of them to a list
    methods = [{name: query} for name, query in methods_dict.items()]

    config = {
        'server': db.server_ip,
        'database': db.db_name,
        'user': db.db_username,
        'password': db.db_password,
        'methods': methods
    }
    return json.dumps(config)


def write_method_csv(writer, items):
    writer.writerow(['Project Name (EN)',
                     'Project Name (FA)',
                     'Database',
                     'Method Name',
                     'Query', ])
    for i in items:
        db = i.parent_db
        writer.writerow(
            [db.name_en, db.name_fa, db.db_name, i.name, i.query_text])


def write_db_csv(writer, items):
    writer.writerow(['Project Name (EN)',
                     'Project Name (FA)',
                     'Server Name',
                     'Server IP',
                     'Port',
                     'Database',
                     'DB Username',
                     'DB Password',
                     'Shell Command',
                     'Health',
                     'Running', ])
    for i in items:
        running = i.docker_id != ""
        health = i.health if running else ""
        writer.writerow([i.name_en, i.name_fa, i.server_name, i.server_ip, i.port_number, i.db_name,
                         i.db_username, i.db_password, i.shell_command, health, running])
