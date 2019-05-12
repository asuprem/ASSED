import sys, os
sys.path.append(os.getcwd())


import click
import utils.helper_utils as helper_utils
import time, pdb, json
import kafka, redis
from datetime import datetime, timedelta


@click.command()
@click.argument("logdir")
@click.argument("importkey")
@click.argument("exportkey")
@click.argument("processscript")
@click.argument("processscriptdir")
@click.argument("pidname")
def main(logdir, importkey, exportkey, processscript, processscriptdir, pidname):
    pid_name = pidname
    #helper_utils.setup_pid(pid_name, logdir=logdir)

    # Import processscript

    moduleImport = __import__("pipelines.%s.%s"%(processscriptdir, processscript), fromlist=[processscript])
    MessageProcessor = getattr(moduleImport, processscript)
    MessageProcessor = MessageProcessor()
    
    kafka_import = importkey.replace(":","_")
    kafka_export = exportkey.replace(":","_")
    pool = redis.ConnectionPool(host='localhost',port=6379, db=0)
    r=redis.Redis(connection_pool = pool)
    
    seek_partition = r.get(exportkey+":partition")
    seek_offset = r.get(exportkey+":offset")
    seek_partition = 0 if seek_partition is None else int(seek_partition)
    seek_offset = 0 if seek_offset is None else int(seek_offset)+1
    
    kafka_producer = kafka.KafkaProducer()
    kafka_consumer = kafka.KafkaConsumer()
    TopicPartition = kafka.TopicPartition(kafka_import, seek_partition)
    kafka_consumer.assign([TopicPartition])
    kafka_consumer.seek(TopicPartition, seek_offset)
    
    for message in kafka_consumer:
        item = json.loads(message.value.decode())
        processedMessage = MessageProcessor.process(item)

        # Push the message to kafka...if true
        if processedMessage[0]:
            pass
            # Message failed to be encoded
        else:
            pass
            # Message succeeded. We will push to kafka.
            #helper_utils.std_flush("%s failed to parse item with id: %s"%(processscript, item["id_str"]))
        
            #byted = bytes(json.dumps(extractTweet(jsonVersion)), encoding="utf-8")
            #kafka_producer.send(kafka_key, byted)
            #kafka_producer.flush()
        
        r.set(exportkey+":partition", message.partition)
        r.set(exportkey+":offset", message.offset)
        r.set(exportkey+":timestamp", message.timestamp)
        
        
    










if __name__ == "__main__":
    main() #pylint: disable=no-value-for-parameter