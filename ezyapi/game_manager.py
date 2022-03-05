import os
import sys
import shutil
import subprocess
import ezyapi.sessions as sessions
import ezyapi.mysql_connection as connect
from ezyapi.UUID import UUID


class GameError(Exception):
    def __init__(self, mess=None):
        super().__init__(str(mess) if mess else "The game has encountered an exception.")


class GameNotFound(GameError):
    def __init__(self, uuid=None):
        super().__init__(f"GameError: The game{f' with the UUID: {uuid}' if uuid else ''} doesn't exist.")


class VersionsNotFound(GameError):
    def __init__(self, uuid=None, version=None):
        super().__init__(f"GameError: The game{f' with the UUID: {uuid}' if uuid else ''} doesn't have the versions specified{f' ({version})' if version else ''}.")


class TooOldVersion(GameError):
    def __init__(self, current=None, expected=None):
        super().__init__(f"""GameError: The game version is too old.{" ({}{}{})".format(f"expected '{expected}'", " " if current and expected else "", f"got '{current}'") if current or expected else ""}""")


class InaccessibleGame(GameError):
    def __init__(self, uuid=None):
        super().__init__(f"GameError: The game{f' with the UUID: {uuid}' if uuid else ''} isn't accessible.")


class UserError(Exception):
    def __init__(self, mess=None):
        super().__init__("The LSP (Linking Session Process) has encountered an exception.")


class UserParameterExpected(UserError):
    def __init__(self):
        super().__init__("UserError: The game must be run with parameters: (--uuid <uuid> or --username <username>) and --password <pwd>")


class NoUserLinked(UserError):
    def __init__(self):
        super().__init__("UserError: There is no user session linked.")


class UserFrozen(UserError):
    def __init__(self):
        super().__init__("UserError: The user is frozen. He cannot commit games sets.")


class AlreadyCommitted(Exception):
    def __init__(self):
        super().__init__("This set is already committed.")


class FormatError(Exception):
    def __init__(self, ver=None):
        super().__init__(f"""The format of the version{f" '{ver}'" if ver is not None else ""} is not correct. (ex: 'v1', 'v1.3', 'v1.0.12')""")


class ResourceNotFound(Exception):
    def __init__(self, id=None, specification=None):
        super().__init__(f"""Couldn't find the resource{f' {id = }' if id is not None else ''}{f' {specification = }' if specification is not None else ''}.""")


class GameVersion:
    def __init__(self, version_to_parse: str | int | float | list = None, reduce_indicator: bool = False):
        self.indicator: list[str or int] = []
        self.set_version(version_to_parse, reduce_indicator)

    @staticmethod
    def parse_version(version_to_parse: str | int | float, reduce_indicator: bool = False, raw: bool = False):
        version = str(version_to_parse).lower() if version_to_parse else "v0.0"
        version = version.replace(" ", "").replace("\n", "").replace("+", "").replace(",", ".").replace("'", ".") \
            .replace("/", ".").replace("*", ".").replace("_", ".")
        letter = "a" if version.startswith("a") or version.startswith("alpha")\
            else "b" if version.startswith("b") or version.startswith("beta")\
            else "d" if version.startswith("d") or version.startswith("delta")\
            else "v"
        if version.startswith("version"):
            version = version[7:]
        elif version.startswith("alpha") or version.startswith("delta"):
            version = version[5:]
        elif version.startswith("beta"):
            version = version[4:]
        elif version.startswith("ver"):
            version = version[3:]
        elif version.startswith("v") or version.startswith("a") or version.startswith("b") or version.startswith("d"):
            version = version[1:]
        if not version.replace(".", "").replace("-", ""):
            version += "0.0"
        if not version.replace(".", "").replace("-", "").isnumeric():
            raise FormatError(version)
        indicator: list[str or int] = [0 if i == "" else int(i) for i in version.split(".")]
        indicator.insert(0, letter)
        if reduce_indicator:
            GameVersion.reduce_indicator(indicator=indicator)
        return indicator if raw else GameVersion(indicator)

    def reduce_indicator(self=None, indicator: list = None):
        if indicator is not None:
            ind = indicator
        elif self is not None:
            ind = self.indicator
        else:
            return
        for i in range(len(ind) - 1, -1, -1):
            if ind[i]: break
            del ind[i]

    def set_precision(self=None, indicator: list = None, precision: int = -1):
        if precision < 0:
            return
        if indicator is not None:
            ind = indicator
        elif self is not None:
            ind = self.indicator
        else:
            return
        ind_origin = ind[:]
        ind.clear()
        for i in range(precision):
            ind.append(ind_origin[i] if len(ind_origin) > i else 0)

    def set_version(self, version_to_parse: str | int | float | list = None, reduce_indicator: bool = False):
        self.indicator = version_to_parse if isinstance(version_to_parse, list) \
            else self.parse_version(version_to_parse, reduce_indicator, True)

    def get_precision(self):
        return self.__len__()

    def get_indicator(self):
        return self.indicator

    def get_version(self, precision: int = -1, reduce_version: bool = False):
        ind = []
        if precision >= 0:
            for i in range(precision):
                ind.append(self.indicator[i] if len(self.indicator) > i else 0)
        else:
            ind = self.indicator[:]
        if reduce_version:
            for i in range(len(ind) - 1, -1, -1):
                if ind[i]: break
                del ind[i]
        fin = ".".join(str(i) for i in ind)
        return fin.replace(".", "", 1) if len(ind) > 1 else fin

    def compare(self, other):
        if not isinstance(other, GameVersion):
            raise TypeError(f"Operators aren't supported between instances of 'GameVersion' and '{type(other)}'")
        p = max(self.get_precision(), other.get_precision())
        for foo, bar in zip(GameVersion(self.get_version(p)).get_indicator(), GameVersion(other.get_version(p)).get_indicator()):
            if str(foo).isalpha():
                f = 1 if str(foo).lower() == "a" else 2 if str(foo).lower() == "b" else 3
                b = 1 if str(bar).lower() == "a" else 2 if str(bar).lower() == "b" else 3
                if f > b: return 1
                elif f < b: return -1
            if foo > bar: return 1
            elif foo < bar: return -1
        return 0

    def __repr__(self):
        return "<ver version='{}' indicator='{}'>".format(self.get_version(), str(self.indicator).replace("'", '"'))

    def __str__(self):
        return self.get_version()

    def __len__(self):
        return len(self.indicator)

    def __contains__(self, item):
        return item in self.indicator

    def __getitem__(self, index):
        return self.indicator[index]

    def __setitem__(self, index, value):
        self.indicator[index] = value

    def __delitem__(self, index):
        self.indicator[index] = 0

    def __lt__(self, other):
        return self.compare(other) == -1

    def __le__(self, other):
        return self.compare(other) != 1

    def __eq__(self, other):
        return self.compare(other) == 0

    def __ne__(self, other):
        return self.compare(other) != 0

    def __ge__(self, other):
        return self.compare(other) != -1


class GameInfo:
    def __init__(self, fetched: tuple | list):
        if not (fetched and (isinstance(fetched, tuple) or isinstance(fetched, list)) and len(fetched) >= 10):
            fetched = [None for _ in range(10)]
        self.uuid: UUID = None if fetched[0] is None else UUID(fetched[0])
        self.name: str = fetched[1]
        self.accessible: bool = fetched[2]
        self.creation = fetched[3]
        self.creator: UUID = None if fetched[4] is None else UUID(fetched[4])
        self.exp_earnable: str = fetched[5]
        self.gp_earnable: str = fetched[6]
        self.other: str = fetched[7]
        self.catchphrase: str = fetched[8]
        self.description: str = fetched[9]
        if self.uuid is None:
            self.version: GameVersion = GameVersion()
        else:
            try:
                connect.execute(f"""SELECT id, specification, resource_version FROM resources WHERE specification = "game" AND id = '{self.uuid}'""")
                v = GameVersion()
                for id, s, f in connect.fetch():
                    try:
                        if GameVersion(f) > v:
                            v = GameVersion(f)
                    except FormatError:
                        continue
                self.version: GameVersion = v
            except Exception:
                self.version: GameVersion = GameVersion()

    def exists(self):
        return self.uuid is not None


class Resource:
    def __init__(self, n: int, id: str, name: str, type: str, bin: bytes, specification: str, info: str = None,
                 resource_version: GameVersion = GameVersion("v1.0"), creator: str = None, creation=None):
        self.n: int = n
        self.id: str = id
        self.name: str = name
        self.type: str = type.lower()
        self.bin: bytes = bin
        self.specification: str = specification
        self.info: str = info
        self.resource_version: GameVersion = resource_version
        self.creator: str = creator
        self.creation = creation

    def save_if_doesnt_exists(self, dir_path: str = "", name: str = None, type: str = None):
        t = self.type if type is None else type
        try:
            if f"{self.name if name is None else name}{'.' if str(t) else ''}{t}" in os.listdir(str(dir_path).replace("\\", "/").replace("//", "/")):
                return
        except FileNotFoundError:
            pass
        self.save_by_erasing(dir_path, name, type)

    def save_by_erasing(self, dir_path: str = "", name: str = None, type: str = None):
        t = self.type if type is None else type
        path = str(dir_path).replace("\\", "/").replace("//", "/")
        if path:
            for i, p in enumerate(path.split("/")):
                try:
                    os.mkdir("/".join(path.split("/")[:i + 1]))
                except FileExistsError:
                    pass
        with open(f"{path}{'/' if str(path) else ''}{self.name if name is None else name}{'.' if str(t) else ''}{t}".replace("//", "/"), "wb") as f:
            f.write(self.bin)


__API_VERSION: GameVersion = GameVersion("v2.4")
__current_version: GameVersion = None
__game_info: GameInfo = None
__user: sessions.User = None
__committed: bool = True
__can_be_commit: bool = True


def linked():
    return __user and isinstance(__user, sessions.User) and __user.connected()


def verification():
    """
    :raise: ezyapi.game_manager.NoUserLinked
    """
    if not __game_info or not __game_info.exists():
        raise GameNotFound()
    if not __game_info.accessible:
        raise InaccessibleGame()
    if not linked():
        raise NoUserLinked()
    if __user.is_frozen():
        raise UserFrozen()
    if __current_version < __game_info.version:
        raise TooOldVersion(__current_version, __game_info.version)


def start_new_game():
    verification()
    global __committed
    __committed = False


def client_initialization():
    """
    :raise: ezyapi.mysql_connection.DatabaseConnexionError
    :raise: ezyapi.game_manager.UserParameterExpected
    :raise: ezyapi.sessions.UserNotFoundException
    """
    global __user
    args = list(sys.argv[1:])
    if len(args) >= 4 and "--password" in args and args.index("--password") != len(args) - 1:
        password = args[args.index("--password") + 1]
        args.pop(args.index("--password") + 1)
        args.pop(args.index("--password"))

        if "--uuid" in args and args.index("--uuid") != len(args) - 1:
            id = args[args.index("--uuid") + 1]
            args.pop(args.index("--uuid") + 1)
            args.pop(args.index("--uuid"))
        elif "--username" in args and args.index("--username") != len(args) - 1:
            id = args[args.index("--username") + 1]
            args.pop(args.index("--username") + 1)
            args.pop(args.index("--username"))
        else:
            raise UserParameterExpected()

        __user = sessions.User(id, password)
        if not __user.connected():
            raise sessions.UserNotFoundException()
    else:
        raise UserParameterExpected()


def export_resource(id: str, name: str, type: str, bin: bytes, specification: str, info: str = None,
                    creator: str = None, resource_version: GameVersion = GameVersion("v1.0")) -> int:
    connect.execute(f"""INSERT resources(id, name, type, bin, specification, info, resource_version, creator) VALUES ('{id}',
                '{name}', '{type}', 0x{bin.hex()}, {"NULL" if specification is None else f"'{specification}'"},
                {"NULL" if info is None else f"'{info}'"}, {resource_version},
                {"NULL" if creator is None else f"'{creator}'"})""")
    connect.commit()
    connect.execute(f"""SELECT max(n) FROM resources""")
    return int(connect.fetch(1)[0])


def import_resource(id: str | UUID, specification: str) -> Resource:
    connect.execute(f"""SELECT * FROM resources WHERE id = '{id}' AND specification = '{specification}'""")
    cont = connect.fetch()
    if not len(cont):
        raise ResourceNotFound(id, specification)
    fin = cont[-1]
    v = GameVersion()
    for f in cont:
        try:
            if GameVersion(f[7]) > v:
                v = GameVersion(f[7])
                fin = f
        except FormatError:
            continue
    return Resource(*fin)


def import_resources(id: str | UUID) -> list[Resource]:
    connect.execute(f"""SELECT id, specification FROM resources WHERE id = '{id}'""")
    return [import_resource(id, sp) for id, sp in connect.fetch()]


def updated():
    return __current_version >= __game_info.version


def update():
    if GameVersion("v0.0") < __current_version < __game_info.version:
        if ".dev" in os.listdir():
            return
        for file in os.listdir():
            if not (str(file).lower() in ["main", "main.py", "main.exe", "main.bat", "main.msi", ".persists"]
                    or str(file).lower().endswith(".persists") or str(file).lower().endswith(".temp")):
                try:
                    os.remove(file)
                except OSError:
                    shutil.rmtree(file)
        try:
            os.renames("main.py", "main.py.temp")
        except FileNotFoundError:
            os.rename("main.exe", "main.exe.temp")
        for r in import_resources(__game_info.uuid):
            if r.specification != "game":
                r.save_by_erasing()
        try:
            import_resource("icon", "icon").save_by_erasing()
        except Exception:
            pass
        subprocess.call(["main", *sys.argv[1:]])
        sys.exit()


def import_missing_resources():
    if ".dev" in os.listdir():
        return
    for r in import_resources(__game_info.uuid):
        if r.specification != "game":
            r.save_if_doesnt_exists()
    try:
        import_resource("icon", "icon").save_if_doesnt_exists()
    except Exception:
        pass


def clear_temp_files():
    if ".dev" in os.listdir():
        return
    for file in os.listdir():
        if file.lower().endswith(".temp"):
            try:
                os.remove(file)
            except OSError:
                pass


def get_user():
    return __user


def is_committed():
    return bool(__committed)


def set_user(user: sessions.User):
    """
    :raise: ezyapi.sessions.UserNotFoundException
    """
    if not user.connected():
        raise sessions.UserNotFoundException()
    global __user
    __user = user


def setup(game_uuid: UUID, version: GameVersion, __update: bool = True,  __client_initialization: bool = True,
          __clear_temp_files: bool = True, __import_missing_resources: bool = True):
    global __current_version, __game_info
    __current_version = version

    if connect.connection is None:
        connect.connexion()  # can raise ezyapi.mysql_connection.DatabaseConnexionError

    connect.execute(f"SELECT * FROM games WHERE id='{game_uuid}'")
    __game_info = GameInfo(connect.fetch(1))
    if not __game_info.exists():
        raise GameNotFound(game_uuid)

    if __clear_temp_files:
        clear_temp_files()

    if __update:
        update()

    if __import_missing_resources:
        import_missing_resources()

    if __client_initialization:
        client_initialization()


def commit_new_set(won: bool, exp_earned: int = 0, gp_earned: int = 0, other: str = None, query: str = None):
    """
    :raise: ezyapi.mysql_connection.DatabaseConnexionError
    :raise: ezyapi.game_manager.AlreadyCommitted
    :raise: ezyapi.game_manager.NoUserLinked
    """
    global __user, __committed
    if __committed:
        raise AlreadyCommitted()
    verification()
    exp = int(exp_earned) if int(exp_earned) >= 0 else 0
    gp = int(gp_earned) if int(gp_earned) >= 0 else 0
    connect.execute(f"""INSERT sets(player, game, won, exp, gp, other) VALUES ("{__user.get_uuid()}",
                        "{__game_info.uuid}", {1 if won else 0}, {exp}, {gp},
                        {"null" if other is None else ('"' + str(other) + '"')})""")
    connect.commit()
    connect.execute(f"""UPDATE `users` SET `exp`=(SELECT `exp` WHERE `uuid`="{__user.get_uuid()}") + {exp}
                        WHERE `uuid`="{__user.get_uuid()}\"""")
    connect.commit()
    connect.execute(f"""UPDATE `users` SET `gp`=(SELECT `gp` WHERE `uuid`="{__user.get_uuid()}") + {gp}
                        WHERE `uuid`="{__user.get_uuid()}\"""")
    connect.commit()
    if query:
        connect.execute(str(query))
        connect.commit()
    __committed = True
