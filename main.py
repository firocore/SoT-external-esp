import pymemoryapi as pymem
import threading

from handlers.overlayrep import Overlay
from handlers.memory import Memory
from handlers.logic import *

process_name = "SoTGame.exe"
winwow_name = "Sea of Thieves"

debug = True


class Test():
    def __init__(self) -> None:
        if process_name in pymem.list_processes_names():
            print("Process found")
            self.overlay = Overlay(winwow_name)
            self.mem = Memory(process_name, debug)
            self.cheat()

    def cheat(self):
        while 0.000001:
            localplayer = self.mem.get_local_player_info()
            # print(localplayer)
            actors_dict = self.mem.get_actors_list()

            for actor in actors_dict:
                # print(localplayer)
                actor_cords = self.mem.get_actor_cords(actor)
                position = w2s(localplayer, actor_cords)
                distance = int(get_actor_distance(localplayer, actor_cords) / 1000)
                if type(position) != bool:
                    if 1920 > position[0] > 0 and 1080 > position[1] > 0 and distance < 3000:
                        # print(position, distance, actors_dict[actor][0])
                        if actors_dict[actor][0] == 'BP_WaterBarrel_C':
                            self.overlay.draw_text(f"* | {distance}m", ('Arial', 14), position[0], position[1], (255, 0, 255), False)
                        else:
                            if debug:
                                self.overlay.draw_text(f"{actors_dict[actor][0]} | {distance}m", ('Arial', 14), position[0], position[1], (255, 255, 255), False)
                    # print((position[0]))
                # print(actors_dict[actor][1])
                # if type(position) != bool and 1920 > position[0] > 0 and 1080 > position[1] > 0:

            self.overlay.update_overlay()


if __name__ == '__main__':
    Test()
