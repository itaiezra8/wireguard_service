import pika
import random
import requests
import ipaddress
from typing import Dict

from core.utils.consts import RABBIT_EXCHANGE, ROUTING_KEY
from wireguard.utils.peer import Peer
from wireguard.utils.consts import DB_URL, OVERLAY_NETWORKS
from wireguard.utils.logger import logger


NOT_AVAILABLE_IPS = set()


async def add_new_peer_to_db(peer: Peer) -> Dict[str, str]:
    body = {'ip_address': peer.virtual_ip_address, 'public_key': peer.public_key}
    try:
        res = requests.post(f'{DB_URL}/new_peer', json=body)
    except requests.exceptions.RequestException as err:
        return {'status': 'failure', 'msg': str(err)}
    return res.json()


async def remove_peer_from_db(public_key: str) -> Dict[str, str]:
    try:
        res = requests.delete(f'{DB_URL}/remove_peer/{public_key}')
    except requests.exceptions.RequestException as err:
        return {'status': 'failure', 'msg': str(err)}
    data = res.json()
    if data.get('status', '') == 'success':
        ip_address = data.get('public_key', '')
        NOT_AVAILABLE_IPS.remove(ip_address)
    return res.json()


def get_overlay_network() -> str:
    return random.choice(OVERLAY_NETWORKS)


def get_new_ip_address(overlay_network: str) -> str:
    net4 = ipaddress.ip_network(overlay_network)
    for ip in net4.hosts():
        ip_address = str(ip)
        if ip_address not in NOT_AVAILABLE_IPS:
            NOT_AVAILABLE_IPS.add(ip_address)
            return str(ip_address)


async def publish_msg_with_rabbit(channel, msg: str) -> None:
    channel.basic_publish(
        exchange=RABBIT_EXCHANGE,
        routing_key=ROUTING_KEY,
        body=msg,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    logger.info(f'published msg: {msg} to all peers')
