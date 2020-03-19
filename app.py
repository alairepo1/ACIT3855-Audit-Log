import datetime
import json
import logging
import logging.config
from itertools import islice
from flask_cors import CORS, cross_origin

import connexion
import pykafka
import yaml
from connexion import NoContent

with open('log_conf.yaml', 'r') as f:
    """loads the configuration for logging"""
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open("app_conf.yaml", 'r') as f:
    """opens app_conf and sets up logger"""
    app_conf = yaml.safe_load(f.read())
    logger = logging.getLogger('basicLogger')

client = pykafka.KafkaClient(hosts=app_conf['kafka']['server'] + ':' + app_conf['kafka']['port'])
topic = client.topics[app_conf['kafka']['topic']]

# functions
def get_event_1_seq(seqNum):
    """ 
    Gets the nth event object from sequence number
    
    **Needs to get the nth order form**
    Cannot access dict key but i can print the key?
    """
    logger.info("Start event_1 request.")

    consumer = topic.get_simple_consumer(
            consumer_group="mygroup",
            auto_offset_reset=pykafka.common.OffsetType.EARLIEST,
            reset_offset_on_start=True
        )
    consumer.consume()
    consumer.commit_offsets()

    counter = 0
    for message in consumer:
        msg = json.loads(message.value.decode('utf-8', errors='replace'))
        try:
            if seqNum -1 <= 0:
                logger.info(msg)
                return msg
            if counter == seqNum -1:
                logger.info(msg)
                return msg
            if counter <= seqNum -1:
                if msg['type'] == 'order_form':
                    counter += 1
                
        except 'KeyError paramater not a number' as KeyError:
            logger.error(KeyError)
            return 404

def get_latest_request_form():
    ''' Gets the latest repair request from kafka producer'''
    consumer = topic.get_simple_consumer(
        consumer_group="mygroup",
        auto_offset_reset=pykafka.common.OffsetType.LATEST -1,
        reset_offset_on_start=True
    )
    consumer.consume()
    consumer.commit_offsets()
    for message in consumer:
        msg = json.loads(message.value.decode('utf-8', errors='replace'))
        return msg


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml")

if __name__ == "__main__":
    app.run(port=8200)
