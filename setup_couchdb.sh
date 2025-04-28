#!/bin/sh -xe

cat >/opt/couchdb/etc/local.ini <<EOF
[couchdb]
single_node=true

[admins]
${COUCHDB_USER} = ${COUCHDB_PASSWORD}

[chttpd]
port = ${COUCHDB_PORT}
bind_address = 0.0.0.0

[httpd]
port = ${COUCHDB_PORT}
bind_address = 0.0.0.0

[log]
level = info

[metrics]
rate = 1.0

EOF

nohup bash -c "/docker-entrypoint.sh /opt/couchdb/bin/couchdb &"
sleep 15


response=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://127.0.0.1:${COUCHDB_PORT}/_users)
if [ "$response" -ne "200" ]; then
    curl -X PUT http://127.0.0.1:5984/_users
    echo "Database _users was configured properly"
fi

response=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://127.0.0.1:${COUCHDB_PORT}/_replicator)
if [ "$response" -ne "200" ]; then
    curl -X PUT http://127.0.0.1:${COUCHDB_PORT}/_replicator
    echo "Database _replicator was configured properly"
fi

response=$(curl -s -o /dev/null -w "%{http_code}" -X GET http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:${COUCHDB_PORT}/grm)
if [ "$response" -ne "200" ]; then
    curl -X PUT http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:${COUCHDB_PORT}/grm
    curl -X PUT http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:${COUCHDB_PORT}/eadls
    curl -X PUT http://${COUCHDB_USER}:${COUCHDB_PASSWORD}@localhost:${COUCHDB_PORT}/grm_attachment
    echo "Database grm was configured properly"
fi