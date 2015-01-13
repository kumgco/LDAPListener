#!/usr/bin/python

from config import Config
from subprocess import call
import ldap
import redis
import umsgpack
import yaml
import pdb


def get_ldap_data():
    """ Return a list representation of all current employees in LDAP.
    """

    temp = open("ldap.yaml", "r")
    config_file = yaml.load(temp)
    temp.close()

    ldap_serv = ldap.open("%s" % config_file["ldapserver"])
    ldap_serv.simple_bind("%s" % config_file["ldapinfo"])

    all_info = ldap_serv.search_s("%s" % config_file["ldapinfo"],
                                 ldap.SCOPE_SUBTREE)

    return all_info


def put_rs_data(allinfo):
    """ Put the given LDAP data into the local redis server. Use uid as key.
    """

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Msgpack is like JSON but it doesn't suck. Also handles UTF-8 correctly
    for user in allinfo:
	    r.set(user["uid"], umsgpack.packb(user))


def get_rs_data(uid):
    """ Return the redis data corresponding to the given key.
    Redis server is @ localhost.
    """

    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    if r.exists(uid):
    	return umsgpack.unpackb(str(r.get(uid)))

	return {}

def act_on(user_diff, uid):
    """ Evaluate the conditions YAML file and execute commands appropriately
    if any of the conditions are true. The YAML file references both user_info
    and uid variables.
    """

    temp = open("conditions.yaml", "r")
    conditions_cfg = yaml.load(temp)
    index = 0
    temp.close()

    # Syntax of YAML file is outlined in YAML file
    while index < len(conditions_cfg["conditions"]):

	clause = conditions_cfg["conditions"][index]
	command = conditions_cfg["conditions"][index + 1]

	# Eval runs strings as Python code
	if eval(clause):
            # shell=True means it will run any command as a shell command
            call(command, shell=True)

	index += 2


def check_for_changes():
    """ Compare the old redis data to the new LDAP data, and record and act on
    any changes. Store the new LDAP data in redis upon completion, overwriting
    the current informdation.
    """

    # Uncomment the lines containing 'changes' if you ever need a list of
    # all the changes for all users.

    current = get_ldap_data()
    changes = []

    for user in current:

        user_diff = {}
        uid = user["uid"]

	old = get_rs_data(uid)

	for key in user:

        user_diff.update({uid: {}})
		user_diff[uid].update({key: {"new": user[1][key], "old": old[key]}})

	act_on(user_diff, uid)
	changes.append(user_diff)

    put_rs_data(current)
    return changes


if __name__ == "__main__":

    x = check_for_changes()
    print x

