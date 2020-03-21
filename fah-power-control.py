from datetime import datetime
import logging
import os
import socket
import xml.etree.ElementTree as ET

import lxml.html as lh
import requests
import yaml


# Load config file
dir_name = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(dir_name, 'config.yaml'), 'r') as stream:
    config = yaml.safe_load(stream)

# Data config
URL = f'https://elen.nu/timpriser-pa-el-for-elomrade-{config["area"]}'
UNIT = ' öre/kWh'
TIME_FORMAT = '%Y-%m-%d %H:%M'
PRICE_THRESHOLD = config['price_threshold']

# Message config
ADDRESS = config['address']
PORT = config['port']
SLOTS = config['slots']
ENCODING = config['encoding']
FAH_CONFIG_FILES = config['config_files']


def f_price(p):
    """ Format price to fixed length string """
    return f'{p:.2f}'.rjust(6, ' ')


def get_data():
    """
    Expected data input format (html table)
    Tidpunkt            Timpris (spotpris)
    2020-03-16 19:00    65.11 öre/kWh
    2020-03-16 20:00    45.22 öre/kWh
    2020-03-16 21:00    36.04 öre/kWh
    2020-03-16 22:00    10.18 öre/kWh

    Data output format
    {
        '2020-03-16 19:00': 65.11, '2020-03-16 20:00': 45.22,
        '2020-03-16 21:00': 36.04, '2020-03-16 22:00': 10.18,
    }
    """
    page = requests.get(URL)
    doc = lh.fromstring(page.content)
    tr_elements = doc.xpath('//tr')
    return {tr[0].text_content(): float(tr[1].text_content().rstrip(UNIT)) for tr in tr_elements[1:]}


def get_slots():
    slots = SLOTS if SLOTS else []
    for file in FAH_CONFIG_FILES:
        try:
            tree = ET.parse(file)
        except FileNotFoundError as e:
            logging.warning(e)
            continue

        for child in tree.getroot().findall('slot'):
            try:
                slots.append(int(child.attrib['id']))
            except ValueError as e:
                logging.error(f'Failed to parse slot: {e}')
    return set(slots)


def get_write_buffer(command):
    """ Create write buffer with identical command for all slots """
    write_buf = ''
    slots = get_slots()
    if slots:
        for slot in slots:
            write_buf += f'{command} {slot}\n'
    else:
        logging.warning(f'No slots provided')
    return write_buf


def main():
    rows = get_data()
    hour_now = datetime.now().replace(minute=0).strftime(format=TIME_FORMAT)
    price_now = rows[hour_now]
    price_msg = f'{hour_now} price (threshold): {f_price(price_now)} ({f_price(PRICE_THRESHOLD)})'
    logging.info(price_msg)
    command = 'pause' if price_now > PRICE_THRESHOLD else 'unpause'
    send_folding_command(command)


def send_folding_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = sock.connect_ex((ADDRESS, PORT))
    if err != 0:
        logging.error(f'Socket connection error: {err}')
        return

    write_buf = get_write_buffer(command)
    if len(write_buf):
        while True:
            count = sock.send(bytes(write_buf, ENCODING))
            if count:
                logging.debug(f'Sent {count} bytes: {write_buf[:count]}'.strip())
                write_buf = write_buf[count:]
                logging.debug(f'Write buffer: {write_buf}'.strip())
            else:
                return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
