# decoding=utf-8
# -*- coding: utf-8 -*-
from flask import Flask, session, request, redirect, render_template, url_for
import sys
import json
import redis
import re
import time
import psycopg2

app = Flask(__name__)

reload(sys)
sys.setdefaultencoding("utf-8")


class Nearby(object):
    record_id = 0
    mac = ""
    rssi = 0


class Record(object):
    id = 0
    node = ""
    nearby = Nearby()


def mac_standard(mac):
    if re.match(r'[A-F\d]{1,2}:[A-F\d]{1,2}:[A-F\d]{1,2}:[A-F\d]{1,2}:[A-F\d]{1,2}:[A-F\d]{1,2}', mac,
                re.M | re.I):
        hexs = mac.split(':')
        hexs_process = []
        for _hex in hexs:
            if len(_hex) == 1:
                hexs_process.append("0" + _hex)
            else:
                hexs_process.append(_hex)
        return ":".join(hexs_process)

    else:
        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " incorrect input:" + mac
        return None


@app.route('/', methods=['GET'])
def index():
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    active_str = r.get('sunhaobomac.active')
    if active_str is None:
        return render_template('main.html', model='[]')
    active = json.loads(active_str)

    names = []
    for mac in active['nearby']:
        name = r.get('sunhaobomac.' + mac)
        if name is not None:
            names.append({"name": name})
    return render_template('main.html', model=json.dumps(names))


# web-api
@app.route('/input/do', methods=['POST'])
def api_input():
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)

    mac = request.form['mac'].encode(encoding='utf-8').upper()
    if not re.match(r'[A-F\d]{2}:[A-F\d]{2}:[A-F\d]{2}:[A-F\d]{2}:[A-F\d]{2}:[A-F\d]{2}', mac, re.M | re.I):
        return '["false","mac_not_correct"]'

    name = request.form['name'].encode(encoding='utf-8')

    if mac is None or mac == "":
        return '["false","need_mac"]'
    if name is None or name == "":
        return '["false","need_name"]'

    r.set('sunhaobomac.' + mac, name)
    return '["true"]'


# web-api
@app.route('/refresh', methods=['POST'])
def api_refresh():
    pool = redis.ConnectionPool(host='localhost', port=6379)
    r = redis.Redis(connection_pool=pool)
    active_str = r.get('sunhaobomac.active')
    if active_str is None:
        return '[]'
    active = json.loads(active_str)

    names = []
    for mac in active['nearby']:
        name = r.get('sunhaobomac.' + mac)
        if name is not None:
            names.append({"name": name})
    return json.dumps(names)


# embedded api
@app.route('/mac/post', methods=['POST'])
def api_mac_post():
    try:

        print request.get_data()
        data = json.loads(request.get_data())

        # 标准化处理
        # nearby_process = []
        for nearby in data['nearby']:
            if 'mac' not in nearby:
                return '["false","mac not in nearby"]'
            if 'rssi' not in nearby:
                return '["false","rssi not in nearby"]'
            mac_process = mac_standard(nearby['mac'])
            if mac_process is not None:
                nearby["mac"] = mac_process.upper()
                # nearby_process.append(nearby)

        # data['nearby'] = nearby_process

        # pool = redis.ConnectionPool(host='localhost', port=6379)
        # r = redis.Redis(connection_pool=pool)
        # r.set('sunhaobomac.active', json.dumps({"nearby": data['nearby']}))

    except Exception, e:
        print Exception, e
        return '["false","unknown"]'

    try:
        conn = psycopg2.connect(database="sunhaobomac", user="postgres", password="postgres", host="127.0.0.1",
                                port="5432")
        if conn is None:
            print '["false","db_connect_error"]'
        cur = conn.cursor()
        cur.execute(
            "insert into records(node) values(%s)", (data['node'],))

        for nearby in data["nearby"]:
            cur.execute(
                "insert into nearby(record_id,mac,rssi) values(currval('records_id_seq'),%s,%s)",
                (nearby['mac'], nearby['rssi']))
            # , json.dumps(data['nearby'])

        conn.commit()
    except Exception, e:
        print Exception, ":", e
    finally:
        cur.close()
        conn.close()
    return '["true"]'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9091)
