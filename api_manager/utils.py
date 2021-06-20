import urllib
import urllib.error
import json
import time
import socket


def check_status(db):
    """
    Checks the health of a database api by calling the 'status_url'
    of that container, if the result code is 200, then it's healthy
    """
    try:
        url = f"http://{db.server_ip}:{db.server_port}{db.status_url}"
        http_req = urllib.request.urlopen(url, timeout=3)
    except (urllib.error.URLError, socket.timeout) as e:
        print("Error: ", e)
        return - 1
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
                     # 'Health',
                     # 'Running',
                     ])
    for i in items:
        # running = Check if it's running
        # health = Check health
        writer.writerow([i.name_en, i.name_fa, i.server_name, i.server_ip, i.server_port, i.db_name,
                         i.db_username, i.db_password, i.shell_command,
                         #health, running
                         ])
