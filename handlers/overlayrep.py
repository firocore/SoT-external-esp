import pygame
import win32api
import win32gui
import win32con
import win32process
import os
import time


class Overlay():
    def __init__(self, link_window: str) -> None:
        self.__link_window = link_window
        self.__entity_list = []

        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(win32api.GetSystemMetrics(0)) + "," + str(win32api.GetSystemMetrics(1))

        self.__search_window_hwnd = win32gui.FindWindow(None, self.__link_window)

        if not self.__search_window_hwnd:
            print(f'Could not find window with {link_window} title')
            raise Exception(f'Could not find window with {link_window} title')
        else:
            print(f"Find window with {link_window} title")

        th = win32process.GetWindowThreadProcessId(self.__search_window_hwnd)
        win32process.AttachThreadInput(win32api.GetCurrentThreadId(), int(th[0]), True)
        win32gui.ShowWindow(self.__search_window_hwnd, 5)
        win32gui.SetForegroundWindow(self.__search_window_hwnd)
        win32gui.SetFocus(self.__search_window_hwnd)

        self.__monitor_size = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
        self.__window_rect = win32gui.GetWindowRect(self.__search_window_hwnd)
        self.__window_size = self.__window_rect[2] - self.__window_rect[0], self.__window_rect[3] - self.__window_rect[1]

        self.__overlay_screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
        self.__overlay_hwnd = pygame.display.get_wm_info()['window']
        # win32gui.SetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        # 0x000000 is transparent color
        win32gui.GetWindowLong(self.__overlay_hwnd, 0)
        win32gui.SetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(self.__overlay_hwnd, win32api.RGB(1, 1, 1), 255, win32con.LWA_COLORKEY | win32con.LWA_ALPHA)
        win32gui.BringWindowToTop(self.__overlay_hwnd)
        win32gui.SetWindowPos(self.__overlay_hwnd, win32con.HWND_TOPMOST, 1, 1, 0, 0, 0 | 1)
        win32gui.ShowWindow(self.__overlay_hwnd, win32con.SW_SHOW)

        # if self.__monitor_size != self.__window_size:
        #    win32gui.SetWindowPos(self.__overlay_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 0 | 2)
        # else:
        #    win32gui.SetWindowPos(self.__overlay_hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 0 | 2)

    def draw_rect(self, x: int, y: int, width: int, height, color: tuple, thickness: int) -> None:
        self.__entity_list.append({'type': 'rectangle', 'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'thickness': thickness})

    def draw_circle(self, x: int, y: int, radius: int, color: tuple, thickness: int) -> None:
        self.__entity_list.append({'type': 'circle', 'x': x, 'y': y, 'radius': radius, 'color': color, 'thickness': thickness})

    def draw_ellipse(self, x: int, y: int, width: int, height, color: tuple, thickness: int) -> None:
        self.__entity_list.append({'type': 'ellipse', 'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'thickness': thickness})

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: tuple, thickness: int) -> None:
        self.__entity_list.append({'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2, 'color': color, 'thickness': thickness})

    def draw_text(self, text: str, font: tuple, x: int, y: int, color: tuple, antialiasing: bool = True):
        self.__entity_list.append({'type': 'text', 'text': text, 'font': font, 'x': x, 'y': y, 'color': color, 'antialiasing': antialiasing})

    def draw_custom_text(self, text: str, font: tuple, x: int, y: int, color: tuple, antialiasing: bool = True):
        self.__entity_list.append({'type': 'custom_text', 'text': text, 'font': font, 'x': x, 'y': y, 'color': color, 'antialiasing': antialiasing})

    def draw_image(self, x: int, y: int, image: object):
        self.__entity_list.append({'type': 'image', 'x': x, 'y': y, 'image': image})

    def update_overlay(self) -> None:
        pygame.event.get()
        self.__overlay_screen.fill((1, 1, 1))

        self.__window_rect = win32gui.GetWindowRect(self.__search_window_hwnd)
        self.__window_size = self.__window_rect[2] - self.__window_rect[0], self.__window_rect[3] - self.__window_rect[1]
        win32gui.MoveWindow(self.__overlay_hwnd, self.__window_rect[0], self.__window_rect[1], self.__window_size[0], self.__window_size[1], True)
        # print(win32gui.GetWindowRect(self.__overlay_hwnd))
        # print(self.__window_rect)
        # print(self.__monitor_size)
        if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.__link_window:
            for shape in self.__entity_list:
                if shape['type'] == 'rectangle':
                    pygame.draw.rect(self.__overlay_screen, shape['color'], (shape['x'], shape['y'], shape['width'], shape['height']), shape['thickness'])
                if shape['type'] == 'ellipse':
                    pygame.draw.ellipse(self.__overlay_screen, shape['color'], (shape['x'], shape['y'], shape['width'], shape['height']), shape['thickness'])
                if shape['type'] == 'circle':
                    pygame.draw.circle(self.__overlay_screen, shape['color'], (shape['x'], shape['y']), shape['radius'], shape['thickness'])
                if shape['type'] == 'line':
                    pygame.draw.line(self.__overlay_screen, shape['color'], [shape['x1'], shape['y1']], [shape['x2'], shape['y2']], shape['thickness'])
                if shape['type'] == 'text':
                    self.__text_font = pygame.font.SysFont(*shape['font'])
                    self.__text_surface = self.__text_font.render(shape['text'], shape['antialiasing'], shape['color'])
                    self.__overlay_screen.blit(self.__text_surface, dest=(shape['x'], shape['y']))
                if shape['type'] == 'custom_text':
                    self.__text_font = pygame.font.Font(*shape['font'])
                    self.__text_surface = self.__text_font.render(shape['text'], shape['antialiasing'], shape['color'])
                    self.__overlay_screen.blit(self.__text_surface, dest=(shape['x'], shape['y']))
                if shape['type'] == 'image':
                    self.__overlay_screen.blit(shape['image'].image, (shape['x'], shape['y']))

        pygame.display.update()
        win32gui.ShowWindow(self.__overlay_hwnd, win32con.SW_SHOW)
        win32gui.SetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(self.__overlay_hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TOOLWINDOW)
        self.__entity_list = []
