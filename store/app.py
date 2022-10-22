from datetime import datetime
from typing import Dict
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

from store.utils.consts import SERVER_HOST, SERVER_PORT, POSTGRESQL_URI
from store.utils.logger import logger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRESQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Peers(db.Model):
    __tablename__ = 'peers'
    public_key = db.Column(db.String(), primary_key=True)
    ip_address = db.Column(db.String(), primary_key=True)
    registration_time = db.Column(db.DateTime)

    def __init__(self, public_key: str, ip_address: str, registration_time: datetime):
        self.public_key = public_key
        self.ip_address = ip_address
        self.registration_time = registration_time


db.create_all()
db.session.commit()


@app.route('/new_peer', methods=['POST'])
async def add_new_peer() -> Dict[str, str]:
    data = request.get_json()
    if not data or type(data) != dict:
        msg = 'request body invalid!'
        logger.error(msg)
        return {'status': 'failure', 'msg': msg}
    peer_public_key = data.get('public_key', '')
    peer = Peers(
        public_key=peer_public_key,
        ip_address=data.get('virtual_ip_address', ''),
        registration_time=datetime.now()
    )
    try:
        db.session.add(peer)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        msg = f'{peer_public_key} already exists!'
        logger.info(msg)
        return {'status': 'failure', 'msg': msg}
    return {'status': 'success', 'msg': 'peer added successfully!'}


@app.route('/remove_peer', methods=['DELETE'])
async def remove_peer() -> Dict[str, str]:
    public_key = request.args.get('public_key', '')
    peer = Peers.query.filter_by(public_key=public_key).first()
    if not peer:
        msg = f'peer with ip public_key: {public_key} not found'
        logger.info(msg)
        return {'status': 'failure', 'msg': msg}
    Peers.query.filter_by(public_key=public_key).delete()
    db.session.commit()
    return {'status': 'success', 'ip_address': peer.virtual_ip_address,
            'msg': f'peer with public_key: {public_key} disconnected', }


@app.errorhandler(404)
def default_handler(e):
    return Response(status=404)


if __name__ == '__main__':
    logger.debug('starting db server...')
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
