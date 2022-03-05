import random
import hashlib


class UUID:
    def __init__(self, uuid: str = None, raw=True):
        self.__uuid = None
        if uuid is None or len(str(uuid)) == 0:
            seed = ""
            for _ in range(0, 16):
                seed += random.choice("abcdefghijklmnopqrstuvwxyz0123456789&/*,;:!?./§ù*^<>$%µ¨£&é\"'(-è_çà)+°=~#{[|`\^@]}€ ")
            self.__uuid = UUID(seed).getUUID()
        elif not raw:
            self.__uuid = UUID(UUID.hash(uuid)).getUUID()
        else:
            legal = True
            if len(uuid) == 32:
                for u in uuid:
                    if u.lower() not in "0123456789abcdef":
                        legal = False
                        break
                if legal:
                    self.__uuid = uuid.lower()[0:8] + "-" + uuid.lower()[8:12] + "-" + uuid.lower()[12:16] + "-" + uuid.lower()[16:20] + "-" + uuid.lower()[20:]
            elif len(uuid) == 36:
                for u in uuid.replace("-", ""):
                    if u.lower() not in "0123456789abcdef":
                        legal = False
                        break
                if legal:
                    if uuid[8] + uuid[13] + uuid[18] + uuid[23] == "----":
                        self.__uuid = uuid.lower()
            if not self.__uuid:
                self.__uuid = UUID(UUID.hash(uuid))

    def getUUID(self):
        return str(self.__uuid)

    def __str__(self):
        return self.getUUID()

    def __repr__(self):
        return self.getUUID()

    def __eq__(self, other):
        return self.getUUID() == (other.getUUID() if isinstance(other, UUID) else UUID.parseUUID(other).getUUID())

    @staticmethod
    def hash(something):
        """ :type = HASH MD5 128bits
        :return = 32 HEX CHARS """
        return str(hashlib.md5(str(something).encode("UTF-8")).hexdigest())

    @staticmethod
    def parseUUID(uuid: str, raw=True):
        return UUID(str(uuid), raw)

    @staticmethod
    def randomUUID():
        return UUID()
