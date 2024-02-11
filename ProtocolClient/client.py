import socket, json, threading, argparse
from time import sleep
from ProtocolClient.Types.PacketType import PacketType
from typing import Tuple, Callable, Dict

class MessagingChannelHandler ():
    def __init__(self, address: Tuple[str, int], timeout: float = 0.1, sleepingTime: int = 1, side: str = PacketType.ALL, isDebug: bool = False) -> None:
        self._native_address = address
        self._isDebug = isDebug 
        self._timeout = timeout
        self._side = side
        self._sleeping = sleepingTime

        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.connect(self._native_address)
        self._srv_sock.settimeout(self._timeout)
        self._thread = threading.Thread(target=self._MainThread)
        self._isWorking = False
        self._isAuthed = False
        self.fa_responses: list[Tuple[str, bool]] = {}
        self._functions: Dict[str, Callable] = {}

        self._functions[PacketType.AUTH_RESPONSE] = self._AuthResponse
        self._functions[PacketType.SERVER_PING] = self._PingResponse
        self._functions[PacketType.MESSAGING_CHANNEL_ERROR] = self._MessagingError
        self._functions[PacketType.CONNECTION_WILL_BE_CLOSED] = self._CloseResponce

    def registrateExecutor (self, executor: Callable[[dict], None], packetType: str):
        self._functions[packetType] = executor

    def isWorking (self) -> bool:
        return self._isWorking

    def isAuthed (self) -> bool:
        return self._isAuthed
    
    def start (self, password: str, protocol: str) -> None:
        self._isWorking = True
        self._thread.start()
        self.sendPacket(PacketType.get_AUTH_PACKET(
            self._side,
            password,
            protocol
        ))
        print ("Started messaging channel!")

    def close (self) -> None:
        self._srv_sock.close()
        self._isWorking = False
        self._thread.join()
        self._thread = None
        print ("Closed connection of server!")

    def sendPacket (self, packet: dict) -> None:
        if (self._srv_sock != None):
            try:
                self._srv_sock.send(json.dumps(packet).encode(PacketType.ENCODING))
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError): #ignored
                pass
        return self._srv_sock != None
    
    def _MainThread (self) -> None:
        while self._isWorking:
            self._receive()

            for data in self.fa_responses:
                player, isAuthed = data
                if isAuthed: self.sendPacket(PacketType.get_SITESIDE_2FA_RESPONSE(player, PacketType.SUCCESS, ""))
                else: self.sendPacket(PacketType.get_SITESIDE_2FA_RESPONSE(player, PacketType.DENIED, "UNAFTORIZED"))
                self.fa_responses.remove(data)

            sleep(self._sleeping)

    def _AuthResponse (self, packet: dict, ignored) -> None:
        if packet["status"]==PacketType.SUCCESS:
            print ("Successfully authed on server!")
            self._isAuthed = True
            #self.sendPacket(PacketType.get_BOTSIDE_2FA_NEEDED("overdrive1"))
        else:
            print ("Error while auth: "+packet["reason"])
    
    def _PingResponse (self, packet: dict, ignored) -> None:
        self.sendPacket(packet=PacketType.get_SERVER_PING())

    def _CloseResponce (self, packet: dict, ignored) -> None:
        self.close()

    def _MessagingError (self, packet: dict, ignored) -> None:
        print ("Messaging error: "+str(packet))

    def _containsAll (data, values):
        try:
            return all(key in data for key in values)
        except TypeError as e:
            print ("Generated TypeError: "+str(e)+" from data "+str(data)+" and values "+str(values))

    def _receive (self) -> dict:
        try:
            data = b""
            while True:
                chunk = self._srv_sock.recv(1024)
                if not chunk:
                    break
                data += chunk
                try:
                    data = "["+data.decode(PacketType.ENCODING).replace("}{", "},{")+"]"
                    data = json.loads(data)
                    break
                except json.JSONDecodeError: #invalid packet
                    if (self._isDebug):
                        print ("Invalid packet "+str(data.decode(PacketType.ENCODING))+" with type "+type(data))
                    return

            for packet in data:
                if PacketType.validatePacket(packet, self._isDebug):
                    print ("Packet received "+str(packet))
                    if MessagingChannelHandler._containsAll(self._functions, [packet["type"]]):
                        self._functions[packet["type"]](packet, self)
                    else: 
                        if (self._isDebug):
                            print ("Can't find executor for packet "+str(packet))
                        return
                else:
                    if (self._isDebug):
                            print ("Unsupported packet "+str(packet))
                    return
        except socket.timeout:
            pass

def executePingPacket(packet: dict, channel: MessagingChannelHandler) -> None:
    print ("Handshaked!")
    channel.sendPacket(PacketType.get_SERVER_PING())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', type=str, default="localhost")
    parser.add_argument('--port', type=int, default=12345)
    parser.add_argument('--passw', type=str, default="?thisIsPassword?")
    parser.add_argument('--forceProtocol', type=str, default=PacketType.PROTOCOL_VERSION)

    args = parser.parse_args()

    channel = MessagingChannelHandler((args.host, args.port))
    channel.start(args.passw, args.forceProtocol)

    channel.registrateExecutor(executor=executePingPacket, packetType=PacketType.SERVER_PING)
    
    while channel.isWorking():
        sleep(2)
        #channel.sendPacket(PacketType.get_BOTSIDE_2FA_NEEDED("overdrive1"))
    else:
        print ("Programm closed")