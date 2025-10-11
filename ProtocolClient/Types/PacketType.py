class PacketType ():
    PROTOCOL_VERSION = "1.1-UNSTABLE"
    ENCODING = "utf-8"

    #ALL
    EMPTY = "EMPTY" #system only
    AUTH_PACKET = "AUTH_PACKET"
    AUTH_RESPONSE = "AUTH_RESPONSE"
    SERVER_PING = "SERVER_PING"
    CONNECTION_WILL_BE_CLOSED = "CONNECTION_WILL_BE_CLOSED"
    MESSAGING_ERROR = "MESSAGING_ERROR"
    MESSAGE = "MESSAGE"
    MEMBER_QUIT_MESSAGING_CHANNEL = "MEMBER_QUIT_MESSAGING_CHANNEL"
    MEMBER_JOIN_MESSAGING_CHANNEL = "MEMBER_JOIN_MESSAGING_CHANNEL"
    MESSAGING_CHANNEL_ERROR = "MESSAGING_CHANNEL_ERROR"

    #BOT
    BOTSIDE_SERVER_WARNING = "SERVER_WARNING"
    BOTSIDE_SERVER_ERROR = "SERVER_ERROR"
    BOTSIDE_SERVER_STOPPED = "SERVER_STOPPED"
    BOTSIDE_2FA_NEEDED = "2FA_NEEDED"

    #SITE
    SITESIDE_2FA_RESPONSE = "2FA_RESPONSE"

    SUCCESS = "SUCCESS"
    DENIED = "DENIED"

    #SIDE TYPES
    BOTSIDE = "BOT"
    ALL = "ALL"
    SITESIDE = "SITE"
    MINECRAFTSIDE = "MINECRAFT"

    def _containsAll (data, values):
        try:
            return all(key in data for key in values)
        except TypeError as e:
            print ("Generated TypeError: "+str(e)+" from data "+str(data)+" and values "+str(values))

    def validatePacket (packet: dict, isDebug: bool) -> bool:
        if not PacketType._containsAll(packet, ["type"]): return False

        match (packet["type"]):
            case PacketType.AUTH_PACKET: 
                if not PacketType._containsAll(packet, ["sideType", "password", "protocol"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["sideType"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.AUTH_RESPONSE:
                if not PacketType._containsAll(packet, ["status", "reason"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateStatus(packet["status"]):
                    if (isDebug): print("Incurrect status "+str(packet))
                    return False
                if packet["status"]==PacketType.SUCCESS and packet["reason"]!="":
                    if (isDebug): print("Incurrect reason with status SUCCESS "+str(packet))
                    return False
            case PacketType.SERVER_PING: return True
            case PacketType.CONNECTION_WILL_BE_CLOSED: return True
            case PacketType.MESSAGE: return True
            case PacketType.MESSAGING_CHANNEL_ERROR: return True
            case PacketType.MESSAGING_ERROR:
                if not PacketType._containsAll(packet, ["reason"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
            case PacketType.BOTSIDE_SERVER_WARNING:
                if not PacketType._containsAll(packet, ["side", "warning"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["side"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.MEMBER_QUIT_MESSAGING_CHANNEL:
                if not PacketType._containsAll(packet, ["memberSide"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["memberSide"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.MEMBER_JOIN_MESSAGING_CHANNEL:
                if not PacketType._containsAll(packet, ["memberSide"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["memberSide"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.BOTSIDE_SERVER_ERROR:
                if not PacketType._containsAll(packet, ["side", "error"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["side"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.BOTSIDE_SERVER_STOPPED:
                if not PacketType._containsAll(packet, ["side", "reason"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["side"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
            case PacketType.BOTSIDE_2FA_NEEDED:
                if not PacketType._containsAll(packet, ["side", "nickname"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["side"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
                if len(packet["nickname"])<3 or len(packet["nickname"])>16:
                    if (isDebug): print("Incurrect nickname "+str(packet))
                    return False
            case PacketType.SITESIDE_2FA_RESPONSE:
                if not PacketType._containsAll(packet, ["side", "status", "reason"]):
                    if (isDebug): print("Incurrect packet values "+str(packet))
                    return False
                if not PacketType.validateSide(packet["side"]):
                    if (isDebug): print("Incurrect side type "+str(packet))
                    return False
                if not PacketType.validateStatus(packet["status"]):
                    if (isDebug): print("Incurrect status "+str(packet))
                    return False
                if packet["status"]==PacketType.SUCCESS and packet["reason"]!="":
                    if (isDebug): print("Incurrect reason with status SUCCESS "+str(packet))
                    return False
            case _:
                return False
            
        return True #if checks complete
    
    def isPacketSided (packet: dict) -> bool:
        return PacketType._containsAll(packet, ["side"])

    def reason (status: str, reason: str) -> str:
        if (status == PacketType.SUCCESS): return ""
        else: return reason

    def validateStatus (status: str) -> bool:
        return status==PacketType.SUCCESS or status==PacketType.DENIED

    def validateSide (sideType: str) -> bool:
        return sideType==PacketType.BOTSIDE or sideType==PacketType.SITESIDE or sideType==PacketType.MINECRAFTSIDE or sideType==PacketType.ALL

    def get_MESSAGING_CHANNEL_ERROR (error: str):
        return {
            "type": PacketType.MESSAGING_CHANNEL_ERROR,
            "error": error
        }

    def get_MEMBER_QUIT_MESSAGING_CHANNEL (side: str) -> dict:
        if (PacketType.validateSide(side)):
            return {
                "type": PacketType.MEMBER_QUIT_MESSAGING_CHANNEL,
                "memberSide": side,
            }
        print("Incorrect side, must be ALL|BOT|SITE|MINECRAFT -> "+str(side))

    def get_MEMBER_JOIN_MESSAGING_CHANNEL (side: str) -> dict:
        if (PacketType.validateSide(side)):
            return {
                "type": PacketType.MEMBER_JOIN_MESSAGING_CHANNEL,
                "memberSide": side,
            }
        print("Incorrect side, must be ALL|BOT|SITE|MINECRAFT")

    def get_MESSAGE (content: str, side: str = "ALL") -> dict:
        if (PacketType.validateSide(side)):
            return {
                "type": PacketType.MESSAGE,
                "side": side,
                "content": content
            }
        print("Incorrect side, must be ALL|BOT|SITE|MINECRAFT")

    def get_AUTH_RESPONSE(status: str, reason: str = "") -> dict:
        if (PacketType.validateStatus(status)):
            return {
                "type": PacketType.AUTH_RESPONSE,
                "status": status,
                "reason": PacketType.reason(status, reason)
            }
        print("Incorrect status, must be SUCCESS or DENIED")
    
    def get_SERVER_PING() -> dict:
        return {
            "type": PacketType.SERVER_PING
        }
    
    def get_AUTH_PACKET(sideType: str, token: str, protocol: str) -> dict:
        if (PacketType.validateSide(sideType)):
            return {
                "type": PacketType.AUTH_PACKET,
                "sideType": sideType,
                "password": token,
                "protocol": protocol
            }
        print ("Incorrect side type, must be BOT|SITE|MINECRAFT")
        return None

    def get_CONNECTION_WILL_BE_CLOSED() -> dict:
        return {
            "type": PacketType.CONNECTION_WILL_BE_CLOSED
        }
    
    def get_MESSAGING_ERROR(reason: str) -> dict:
        return {
            "type": PacketType.MESSAGING_ERROR,
            "reason": reason
        }
    
    def get_BOTSIDE_2FA_NEEDED(nickname: str) -> dict:
        if nickname=="" or len(nickname)<3 or len(nickname)>16:
            print ("Incorrect nickname, must be len 3-16 chars of nickname")
            return None
        return {
            "type": PacketType.BOTSIDE_2FA_NEEDED,
            "side": PacketType.BOTSIDE,
            "nickname": nickname
        }
    
    def get_SITESIDE_2FA_RESPONSE(nickname: str, status:str, reason: str) -> dict:
        if nickname=="" or len(nickname)<3 or len(nickname)>16:
            print ("Incorrect nickname, must be len 3-16 chars of nickname")
            return None
        if (PacketType.validateStatus(status)):
            return {
                "type": PacketType.SITESIDE_2FA_RESPONSE,
                "status": status,
                "side": PacketType.SITESIDE,
                "nickname": nickname,
                "reason": PacketType.reason(status, reason)
            }
        print ("Incorrect side type, must be BOT|SITE|MINECRAFT")
        return None