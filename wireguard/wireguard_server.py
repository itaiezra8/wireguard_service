import pika
from flask import Flask, Response, Request
from typing import Dict

from wireguard.utils.peer import Peer
from wireguard.utils.consts import SERVER_HOST, SERVER_PORT
from wireguard.utils.helpers import (
    publish_msg_with_rabbit, get_overlay_network, get_new_ip_address, add_new_peer_to_db, remove_peer_from_db
)
from wireguard.utils.logger import logger


app = Flask(__name__)


def connect_to_rabbitmq() -> None:
    logger.info('connecting to rabbit ...')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='peers', durable=True)
    app.config['RABBITMQ_CHANNEL'] = channel


@app.route('/new_peer', methods=['POST'])
async def new_peer_handler(request: Request) -> Dict[str, str]:
    logger.debug('handling new peer request...')
    peer_public_key = request.args.get('public_key', '')
    overlay_network = get_overlay_network()
    virtual_ip_address = get_new_ip_address(overlay_network)
    if not virtual_ip_address:
        return {'status': 'failure', 'msg': 'there is currently no available IP to assign to you'}
    new_peer = Peer(peer_public_key, virtual_ip_address)
    db_res = await add_new_peer_to_db(new_peer)
    if db_res.get('status', '') != 'success':
        return {'msg': f'peer registration request was not accepted: {db_res.get("msg", "")}'}
    new_peer_msg = {'type': 'POST', 'body': new_peer}
    await publish_msg_with_rabbit(channel=app.config['RABBITMQ_CHANNEL'], msg=str(new_peer_msg))
    return {
        'status': 'success',
        'msg': 'peer registration request accepted!',
        'ip_address': virtual_ip_address
    }


@app.route('/remove_peer', methods=['DELETE'])
async def remove_peer_handler(request: Request) -> Dict[str, str]:
    logger.debug('handling disconnect request...')
    peer_public_key = request.args.get('public_key', '')
    db_res = await remove_peer_from_db(peer_public_key)
    if db_res.get('status', '') != 'success':
        return {'msg': f'remove peer request was not accepted: {db_res.get("msg", "")}'}
    disconnect_peer_msg = {'type': 'DELETE', 'body': peer_public_key}
    await publish_msg_with_rabbit(channel=app.config['RABBITMQ_CHANNEL'], msg=str(disconnect_peer_msg))
    return {
        'status': 'success',
        'msg': 'remove peer request accepted!'
    }


@app.errorhandler(404)
def default_handler(e):
    return Response(status=404)


if __name__ == '__main__':
    connect_to_rabbitmq()
    logger.debug('starting wireguard server...')
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True, threaded=True)
