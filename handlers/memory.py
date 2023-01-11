import json
import libs.pymemoryapi as pymem

from handlers.loger import Loger


class Memory():
    # Запуск модуля памяти
    def __init__(self, process, debug) -> None:
        # Режим
        self.debug = debug

        # Логер
        self.loger = Loger()

        # Подключение к процессу
        self.process = pymem.Process(process)

        # Получение начального и конечного адреса процесса на UE4
        module = self.process.get_module_info(process)
        self.base = module.BaseAddress
        self.base_end = self.base + module.SizeOfImage

        # Лог debug информации
        if debug:
            self.loger.debug('Base address - ' + hex(self.base))
            self.loger.debug('Base end address - ' + hex(self.base_end))

        # Получаем офсеты
        self.get_offsets()

    # Получение адреса по потерну
    def get_addreses(self, pattern: str, return_first: bool = False):
        if return_first:
            # Возвращает int адресс
            address = self.process.pattern_scan(self.base, self.base_end, pattern, True)    
        else:
            # Возвращает лист с адресами
            address = self.process.pattern_scan(self.base, self.base_end, pattern, False)

        return address

    # Функция получения офсетов
    def get_offsets(self):
        try:
            # Открываем и читам файлы конфига | патарны и офсеты
            with open('cfg/patterns.json', 'r') as patterns_file:
                patternts = json.load(patterns_file)
                patterns_file.close()

            with open('cfg/offsets.json', 'r') as offsets_file:
                self.offsets = json.load(offsets_file)

            # Получаем промежуточные адреса основных адресов
            base_UWORLD = self.get_addreses(patternts['Main']['UWORLD'], True)
            base_GOBJECT = self.get_addreses(patternts['Main']['GOBJECT'], True)
            base_GNAME = self.get_addreses(patternts['Main']['GNAME'], True)

            # Лог debug информации
            if self.debug:
                print('[DEBUG] Base UWORLD - ' + hex(base_UWORLD))
                print('[DEBUG] Base GOBJECT - ' + hex(base_GOBJECT))
                print('[DEBUG] Base GNAME - ' + hex(base_GNAME))

            if base_UWORLD and base_GOBJECT and base_GNAME:
                # Получаем адрес UWORLD из промежуточного
                offset_UWORLD = self.process.read_ulong(base_UWORLD + 3)
                address_UWORLD = base_UWORLD + offset_UWORLD + 7
                self.address_UWORLD = self.process.read_ulonglong(address_UWORLD)
                print('[INFO] UWORLD address - ' + hex(self.address_UWORLD))

                # Получаем адрес GOBJECT из промежуточного
                offset_GOBJECT = self.process.read_ulong(base_GOBJECT + 2)
                address_GOBJECT = base_GOBJECT + offset_GOBJECT + 22
                self.address_GOBJECT = self.process.read_ulonglong(address_GOBJECT)
                print('[INFO] GOBJECT address - ' + hex(self.address_GOBJECT))

                # Получаем адрес GNAME из промежуточного
                offset_GNAME = self.process.read_ulong(base_GNAME + 3)
                address_GNAME = base_GNAME + offset_GNAME + 7
                self.address_GNAME = self.process.read_ulonglong(address_GNAME)
                print('[INFO] GNAME address - ' + hex(self.address_GNAME))

                # Получаем адрес уровня(Мира) ULevel
                self.address_U_level = self.process.read_ulonglong(self.address_UWORLD + self.offsets['World.PersistentLevel'])

                # Получаем локал игрока ULocalPlayer
                game_instance = self.process.read_ulonglong(self.address_UWORLD + self.offsets['World.OwningGameInstance'])
                local_player = self.process.read_ulonglong(game_instance + self.offsets['GameInstance.LocalPlayers'])
                self.local_player = self.process.read_ulonglong(local_player)
                print('[INFO] LocalPlayer address - ' + hex(self.local_player))

                # Полученеи контоллера игрока APlayerController
                self.player_controller = self.process.read_ulonglong(self.local_player + self.offsets['LocalPlayer.PlayerController'])
                print('[INFO] APlayerController address - ' + hex(self.player_controller))

                # Поличение информацию о камере игрока CameraCacheEntry.MinimalViewInfo
                camera_manager = self.process.read_ulonglong(self.player_controller + self.offsets['PlayerController.CameraManager'])
                self.camera_view_info = camera_manager + self.offsets['PlayerCameraManager.CameraCache'] + self.offsets['CameraCacheEntry.MinimalViewInfo']
                print('[INFO] MinimalViewInfo address - ' + hex(self.camera_view_info))

                # Подгружаем офстевы для Actor(Entity)
                self.offset_actorId = self.offsets['Actor.actorId']
                self.rootComponent = self.offsets['Actor.rootComponent']
                self.relative_location = self.offsets['SceneComponent.RelativeLocation']
                print('[INFO] Actor.actorId address - ' + hex(self.offset_actorId))
                print('[INFO] Actor.rootComponent address - ' + hex(self.rootComponent))
                print('[INFO] SceneComponent.ActorCoordinates address - ' + hex(self.ActorCoordinates))

            # Нужно сделать лог вывода промежуточного отсутвия адреса
            print("Need log (memory 111)")

        except Exception as _error:
            print("[ERROR] " + _error)

    def get_actors_list(self):
        actors_dict = {}
        # Нужно дабавить офсет AActor
        address_AActor = self.process.read_ulonglong(self.address_U_level + 0xA0)
        amount_AActor = self.process.read_int(self.address_U_level + 0xA0 + 0x8)

        for i in range(0, amount_AActor):
            actor_address = self.process.read_ulonglong(address_AActor + i * 8)
            actor_id = self.process.read_int(actor_address + self.offset_actorId)

            if actor_id != 0:
                actors_dict[actor_address] = self.get_actor_name(actor_id), actor_id

        return actors_dict

    def get_actor_cords(self, actor_address: int):
        u_scene_component = self.process.read_ulonglong(actor_address + self.rootComponent)
        relative_location = u_scene_component + self.relative_location

        cords_dict = {}

        # Получаем и записываем коодинаты entity в dict | Cмещение по адресу int 0, 4, 8

        # Не могу проверить скорее всего коодинаты сломались после обновления старый оффтест hex 12С или int 300
        cords_dict["cordinate_x"] = self.process.read_float(relative_location + 0x0)
        cords_dict["cordinate_y"] = self.process.read_float(relative_location + 0x4)
        cords_dict["cordinate_z"] = self.process.read_float(relative_location + 0x8)

        return cords_dict

    def get_actor_name(self, actor_id: int):
        name = self.process.read_ulonglong(self.address_GNAME + int(actor_id / 0x4000) * 8)
        name = self.process.read_ulonglong(name + 8 * (actor_id % 0x4000))
        name = self.process.read_string(name + 0x10, 32)
        
        return name

    def get_local_player_info(self):
        cordinate_dict = {}

        # Получение координат локал игрока
        cordinate_dict["localPlayer_x"] = self.process.read_float(self.camera_view_info + 0x0)
        cordinate_dict["localPlayer_y"] = self.process.read_float(self.camera_view_info + 0x4)
        cordinate_dict["localPlayer_z"] = self.process.read_float(self.camera_view_info + 0x8)
        # Получение направления камеры локал игрока
        cordinate_dict["camera_x"] = self.process.read_float(self.camera_view_info + 0x0C)
        cordinate_dict["camera_y"] = self.process.read_float(self.camera_view_info + 0x10)
        cordinate_dict["camera_z"] = self.process.read_float(self.camera_view_info + 0x14)

        # Получение фова игрока !!! НАДО СДЕЛАТЬ
        cordinate_dict["fov"] = 90

        '''if debug:
            print('[DEBUG] LocalPlayer X - ' + str(localPlayer_x))
            print('[DEBUG] LocalPlayer Y - ' + str(localPlayer_y))
            print('[DEBUG] LocalPlayer Z - ' + str(localPlayer_z))
            print('[DEBUG] Camera X - ' + str(camera_x))
            print('[DEBUG] Camera Y - ' + str(camera_y))
            print('[DEBUG] Camera Z - ' + str(camera_z))'''

        return cordinate_dict
