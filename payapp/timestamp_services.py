from timestamp_service import TimestampService
import datetime
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class TimestampHandler:
    def getTimestamp(self):
        return datetime.datetime.now().isoformat()

def start_thrift_server():
    handler = TimestampHandler()
    processor = TimestampService.Processor(handler)
    transport = TSocket.TServerSocket(port=10000)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()

if __name__ == '__main__':
    start_thrift_server()