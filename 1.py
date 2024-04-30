import os
import sys
import pygame
import requests
import math


COLOR_INACTIVE = pygame.Color('black')
COLOR_ACTIVE = pygame.Color('dodgerblue2')

# Класс кнопки. Большая задача по Maps API. Часть №7
class ImageButton:
    def __init__(self, x, y, width, height, image, image_hover=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.image_hover = self.image

        if image_hover:
            self.image_hover = pygame.image.load(image_hover)
            self.image_hover = pygame.transform.scale(self.image_hover, (width, height))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_hovered = False

    def draw_button(self, screen):
        current_image = self.image_hover if self.is_hovered else self.image
        screen.blit(current_image, self.rect.topleft)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.FONT = pygame.font.Font(None, 32)
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    app.find(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Карта")
        self.image_t = None
        self.image = None
        self.image_type = "map"
        self.pt_address = None
        self.pt_x = None
        self.pt_y = None
        self.pt = False
        self.pch_i = False
        self.pch_i_ad = ""
        self.text = "35.829036,55.517821"
        self.map_file = None
        self.map()
        self.screen = pygame.display.set_mode((1624, 536))
        pygame.display.flip()
        self.clock = pygame.time.Clock()
        self.x = 35.829036
        self.y = 55.517821
        self.z = 0.002

    def map(self, spn_1=0.002, coord_1=35.829036, coord_2=55.517821):
        if self.pt:
            map_request = f"http://static-maps.yandex.ru/1.x/?ll={coord_1},{coord_2}&pt={self.pt_x},{self.pt_y},pm2rdm&spn={spn_1},{spn_1}&size=650,450&l={self.image_type}"
        else:
            map_request = f"http://static-maps.yandex.ru/1.x/?ll={coord_1},{coord_2}&spn={spn_1},{spn_1}&size=650,450&l={self.image_type}"

        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.image = pygame.image.load(self.map_file)
        self.image_t = self.image

    def find(self, adr):
        self.text = adr
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={adr}&format=json"
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Почтовый индекс. Большая задача по Maps API. Часть №9 Большая задача по Maps API. Часть №10
            if self.pch_i:
                try:
                    self.pch_i_ad = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                except:
                    self.pch_i_ad = "почтового индекса нет"
            else:
                self.pch_i_ad = ""
            # Полный адрес топонима. Большая задача по Maps API. Часть №8
            self.pt_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"] + "  " + self.pch_i_ad
            toponym_coodrinates = toponym["Point"]["pos"].split(" ")
            self.x = float(toponym_coodrinates[0])
            self.y = float(toponym_coodrinates[1])
            self.pt_y = self.y
            self.pt_x = self.x
            self.pt = True
            self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def im_map(self):
        self.image_type = "map"
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def im_sput(self):
        self.image_type = "sat"
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def im_gib(self):
        self.image_type = "sat,skl"
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def reset(self):
        self.pt_x = None
        self.pt_y = None
        self.pt_address = ""
        self.pt = False
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def activ_diac(self):
        self.pch_i = not self.pch_i
        self.find(self.text)

    def z_up(self, a):
        if a:
            if self.z - 0.04 > 0:
                self.z -= 0.04
        else:
            if self.z + 0.04 != 2:
                self.z += 0.04
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def yx_up(self, a, b):
        if a and b == 1:
            if self.x - 0.0025 > 0:
                self.x -= 0.0025
        elif not a and b == 1:
            if self.x + 0.0025 < 90:
                self.x += 0.0025
        if a and b == 2:
            if self.y - 0.0009 > 0:
                self.y -= 0.0009
        elif not a and b == 2:
            if self.y + 0.0009 < 90:
                self.y += 0.0009
        self.map(spn_1=self.z, coord_1=self.x, coord_2=self.y)

    def run(self):
        self.font = pygame.font.Font(None, 34)
        self.button_play = ImageButton(660, 86, 100, 32, "button_f.png", "button_f_a.png")
        self.button_pch = ImageButton(1030, 128, 120, 32, "button_p.png", "button_p_a.png")
        self.box = InputBox(10, 10, 140, 32)
        while True:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    os.remove(self.map_file)
                    sys.exit()

                if keys[pygame.K_PAGEUP]:
                    self.z_up(False)

                if keys[pygame.K_PAGEDOWN]:
                    self.z_up(True)

                if keys[pygame.K_RIGHT]:
                    self.yx_up(False, 1)

                if keys[pygame.K_LEFT]:
                    self.yx_up(True, 1)

                if keys[pygame.K_UP]:
                    self.yx_up(True, 2)

                if keys[pygame.K_DOWN]:
                    self.yx_up(False, 2)

                if keys[pygame.K_m]:
                    self.im_map()

                if keys[pygame.K_s]:
                    self.im_sput()

                if keys[pygame.K_k]:
                    self.im_gib()

                # Нажатие кнопки. Большая задача по Maps API. Часть №7
                if event.type == pygame.USEREVENT and event.button == self.button_play:
                    self.reset()

                # Нажатие кнопки. Большая задача по Maps API. Часть №9 Большая задача по Maps API. Часть №10
                if event.type == pygame.USEREVENT and event.button == self.button_pch:
                    self.activ_diac()

                self.button_play.handle_event(event)
                self.button_pch.handle_event(event)
                self.box.handle_event(event)
                self.box.update()

            # Отрисовка фона
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.image_t, (0, 86))
            self.box.draw(self.screen)
            # Отрисовка кнопки и реакция на мышь. Большая задача по Maps API. Часть №7
            self.button_play.draw_button(self.screen)
            self.button_play.check_hover(pygame.mouse.get_pos())
            # Отрисовка кнопки и реакция на мышь. Большая задача по Maps API. Часть №9 Большая задача по Maps API. Часть №10
            self.button_pch.draw_button(self.screen)
            self.button_pch.check_hover(pygame.mouse.get_pos())
            # Полный адрес топонима. Большая задача по Maps API. Часть №8
            self.text_1 = self.font.render(self.pt_address, False, (0, 0, 0))
            self.screen.blit(self.text_1, (10, 54))
            # Отрисовка кнопки и реакция на мышь. Большая задача по Maps API. Часть №9 Большая задача по Maps API. Часть №10
            if self.pch_i:
                self.text_2 = self.font.render("Почтовый индекс: Включен", False, (0, 0, 0))
            else:
                self.text_2 = self.font.render("Почтовый индекс: Выключен", False, (0, 0, 0))
            self.screen.blit(self.text_2, (660, 132))
            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    app = App()
    app.run()
