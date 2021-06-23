import pygame
import os
import math
import sys
import random
import neat
import pyautogui
from pygame.locals import *

screen_width = 1500
screen_height = 1000
generation = 0
#define colours
bg = (204, 102, 0)
red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)

#define global variable
clicked = False
counter = 0


pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Demo for both self driving and remote control Car')
clock = pygame.time.Clock()
generation_font = pygame.font.SysFont("Arial", 70)
font = pygame.font.SysFont("Arial", 30)
map = pygame.image.load('map.png')


class button():
		
	#colours for button and text
	button_col = (255, 0, 0)
	hover_col = (75, 225, 255)
	click_col = (50, 150, 255)
	text_col = black
	width = 180
	height = 70

	def __init__(self, x, y, text):
		self.x = x
		self.y = y
		self.text = text

	def draw_button(self):

		global clicked
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#create pygame Rect object for the button
		button_rect = Rect(self.x, self.y, self.width, self.height)
		
		#check mouseover and clicked conditions
		if button_rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				clicked = True
				pygame.draw.rect(screen, self.click_col, button_rect)
			elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
				clicked = False
				action = True
			else:
				pygame.draw.rect(screen, self.hover_col, button_rect)
		else:
			pygame.draw.rect(screen, self.button_col, button_rect)
		
		#add shading to button
		pygame.draw.line(screen, white, (self.x, self.y), (self.x + self.width, self.y), 2)
		pygame.draw.line(screen, white, (self.x, self.y), (self.x, self.y + self.height), 2)
		pygame.draw.line(screen, black, (self.x, self.y + self.height), (self.x + self.width, self.y + self.height), 2)
		pygame.draw.line(screen, black, (self.x + self.width, self.y), (self.x + self.width, self.y + self.height), 2)

		#add text to button
		text_img = font.render(self.text, True, self.text_col)
		text_len = text_img.get_width()
		screen.blit(text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + 25))
		return action


speed=0
class Car:
    def __init__(self):
        self.surface = pygame.image.load("car2.png")
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos = [700, 650]
        self.angle = 0
        #self.speed = 0
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)
        self.draw_radar(screen)

    def draw_radar(self, screen):
        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (0, 255, 0), pos, 5)

    def check_collision(self, map):
        self.is_alive = True
        for p in self.four_points:
            if map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not map.get_at((x, y)) == (255, 255, 255, 255) and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    # def updated(self, map,x):
    #     if x==0:
    #         self.speed=0

    #     if x==1:
    #         self.speed=15        

    def update(self, map,x):
        if x==0:
            self.speed=0
            return

        if x==1:
            self.speed=15    
        #check speed
        #self.speed = 0

        #check position
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(map)
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, map)

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)

        return ret

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.distance / 50.0

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

def run_car(genomes, config):

    # Init NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my cars
        cars.append(Car())

    # Init my game
    # pygame.init()
    # screen = pygame.display.set_mode((screen_width, screen_height))
    # pygame.display.set_caption('Self Driving Car for HCI Project')
    # clock = pygame.time.Clock()
    # generation_font = pygame.font.SysFont("Arial", 70)
    # font = pygame.font.SysFont("Arial", 30)
    # map = pygame.image.load('map.png')
    


    # #BHAJAN
    # bg = (204, 102, 0)
    # red = (255, 0, 0)
    # black = (0, 0, 0)
    # white = (255, 255, 255)
    # Start = button(75, 350, 'Start')
    quit = button(1300, 900, 'Quit?')
    Start = button(30, 900, 'Start')
    Stop = button(650, 900, 'Stop')


    # Main loop
    global generation
    generation += 1
    isstop=1
    while True:

        if quit.draw_button():
            msg = pyautogui.confirm(text='Do You Really want to Quit', title='', buttons=['Yes', 'No'])
            if(msg=='Yes'):
                pygame.quit()

           
        # if Start.draw_button():
        #     speed=15
        #     # for car in enumerate(cars):
        #     #     car.update(map,1)
        #     print("Start ->")  
        carr=Car();  
        if Stop.draw_button():
            isstop=1
            carr.update(map,0)
            print("Stopped...")

        if Start.draw_button():
            isstop=0
            #car.update(map,1)
            print("Started...")    
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)


        # Input my data and get result from network
        if isstop==0:
            for index, car in enumerate(cars):
                output = nets[index].activate(car.get_data())
                i = output.index(max(output))
                if i == 0:
                    car.angle += 10
                else:
                    car.angle -= 10

        # for index, car in enumerate(cars):
        #     output = nets[index].activate(car.get_data())
        #     i = output.index(max(output))
        #     if i == 0:
        #         car.angle += 10
        #     else:
        #         car.angle -= 10

        # Update car and fitness
        remain_cars = 0
        for i, car in enumerate(cars):
            if car.get_alive():
                remain_cars += 1
                if isstop==0:
                    car.update(map,1)
                else:
                	break
                    
                # else:
                # 	car.update(map,1)
                    
                # if Start.draw_button():	
                #     car.update(map,1)
                #car.update(map,1)
                genomes[i][1].fitness += car.get_reward()



        # for i, car in enumerate(cars):
        #     if car.get_alive():
        #         remain_cars += 1
        #         if Stop.draw_button():
        #             car.update(map,0)
        #             break
        #         else:
        #         	car.update(map,1)
                    
        #         # if Start.draw_button():	
        #         #     car.update(map,1)
        #         #car.update(map,1)
        #         genomes[i][1].fitness += car.get_reward()

        # check
        if remain_cars == 0:
            break

        # Drawing
        screen.blit(map, (0, 0))
        for car in cars:
            if car.get_alive():
                car.draw(screen)

        # text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (screen_width/2, 100)
        # screen.blit(text, text_rect)

        # text = font.render("remain cars : " + str(remain_cars), True, (0, 0, 0))
        # text_rect = text.get_rect()
        # text_rect.center = (screen_width/2, 200)
        # screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

if __name__ == "__main__":
    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_car, 1000)

