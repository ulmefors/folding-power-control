from datetime import datetime
import os
import socket

import lxml.html as lh
import requests
import yaml


dir_name = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(dir_name, 'config.yaml'), 'r') as stream:
    config = yaml.safe_load(stream)

URL = f'https://elen.nu/timpriser-pa-el-for-elomrade-{config["area"]}'
UNIT = ' öre/kWh'
HOUR_FORMAT = '%Y-%m-%d %H'
PRICE_THRESHOLD = config['price_threshold']
ADDRESS = config['address']
PORT = config['port']
SLOTS = config['slots']
ENCODING = config['encoding']


def get_rows_from_table(tr_elements):
    """
    Expected data format
    Tidpunkt            Timpris (spotpris)
    2020-03-16 19:00    65.11 öre/kWh
    2020-03-16 20:00    45.22 öre/kWh
    2020-03-16 21:00    36.04 öre/kWh
    2020-03-16 22:00    10.18 öre/kWh
    """
    return {tr[0].text_content().replace(':00', ''): float(tr[1].text_content().rstrip(UNIT)) for tr in tr_elements[1:]}


def main():
    page = requests.get(URL)
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')
    rows = get_rows_from_table(tr_elements)
    hour_now = datetime.now().strftime(format=HOUR_FORMAT)
    price_now = rows[hour_now]
    print(f'Price (threshold) at {hour_now}: {price_now} ({PRICE_THRESHOLD})')
    command = 'pause' if price_now > PRICE_THRESHOLD else 'unpause'
    send_folding_command(command)


def send_folding_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = sock.connect_ex((ADDRESS, PORT))
    if err != 0:
        print(f'Socket connection error: {err}')
        return

    write_buf = ''
    for slot in SLOTS:
        write_buf += f'{command} {slot}\n'

    if len(write_buf):
        while True:
            count = sock.send(bytes(write_buf, ENCODING))
            if count:
                print(f'Sent {count} bytes: {write_buf[:count]}')
                write_buf = write_buf[count:]
            else:
                return


if __name__ == '__main__':
    main()
