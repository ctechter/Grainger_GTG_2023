#!/usr/bin/env python

import sys
import json
from random import choice
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

if __name__ == '__main__':
    # Parse the command line.
    argparser = ArgumentParser()
    argparser.add_argument('ConfigFile',type=FileType('r'))
    args = argparser.parse_args()

    # Parse the configuration.
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    config_parser = ConfigParser()
    config_parser.read_file(args.ConfigFile)
    config = dict(config_parser['ConfluentCloudEndpoint'])
 
    # Create Producer instance
    producer = Producer(config)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).
    def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

    # Produce data by selecting random values from these lists.
    
    topic = config_parser["misc"]["topic"]
    user_ids = ['eabara', 'jsmith', 'sgarcia', 'jbernard', 'htanaka', 'awalther']
    products = ['book', 'alarm clock', 't-shirts', 'gift card', 'batteries']
    price = ['$5.99', '$10.25', '$2.49', '$4.83']
    color = ['blue','green','yellow','red','orange']
    num_records = int(input("Enter the # of records to generate.  Enter '0' for a continuous stream of records [use control+c to interrupt]: "))
    if num_records > 0:
        for count in range(num_records):
            record_json = json.dumps({'product': choice(products), 'price': choice(price), 'color': choice(color)})
            producer.produce(topic, value=record_json, key=choice(user_ids), callback=delivery_callback)
            count += 1
            producer.poll(10000)
            producer.flush()  
    else:
        while True:
            try:
                record_json = json.dumps({'product': choice(products), 'price': choice(price), 'color': choice(color)})
                producer.produce(topic, value=record_json, key=choice(user_ids), callback=delivery_callback)
                producer.poll(10000)
                producer.flush()  
            except KeyboardInterrupt:
                break

    print('program complete')
