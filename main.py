from pygame import *
import random
import numpy as np
from typing import Literal

#https://flappybird-ai.netlify.app/

display.init()
font.init()

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 375
win = display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
display.set_caption('AI tries to learn Flappy Bird')
win.fill((0, 192, 255))
clock = time.Clock()


class FlappyBirdGame():
    def __init__(self) -> None:
        self.gaming = True
        self.tracker = Tracker(parent=self)

        self.COLUMN_MOVESPEED = 10
        self.SPAWN_COLUMN_COOLDOWN = 45
        self.AUTO_RESTART_COOLDOWN = 15
        self.columnSegmentsGroup = sprite.Group()

        self.birds:list[FlappyBird] = list()

    def startGame(self):
        self.finish = False
        self.columns:list[Column] = list()
        self.autoRestartTimer = self.AUTO_RESTART_COOLDOWN
        self.toNextColumn = 0
        self.columnSegmentsGroup.empty()

        for _ in range(50):
            self.birds.append(FlappyBird('imgs/flappy.png', 75, 100))

        #self.birds.append(FlappyBird('imgs/flappy_manual.png', 75, 100, isAi=False))


class Tracker:
    def __init__(self, parent:FlappyBirdGame) -> None:
        self.parent = parent
        self.generations = 0
        self.bestScore = 0
        self.bestW1 = None
        self.bestW2 = None

    def updateWeights(self, w1, w2):
        self.bestW1:np.ndarray = w1
        self.bestW2:np.ndarray = w2


class GameSprite(sprite.Sprite):
    def __init__(self, img_path, x, y, w, h):
       super().__init__()

       self.image = transform.scale(image.load(img_path), (w, h))

       self.rect = self.image.get_rect()
       self.rect.x = x
       self.rect.y = y
    def renderSprite(self):
       win.blit(self.image, (self.rect.x, self.rect.y))

class Column():
    def __init__(self):
        SEGMENT_HEIGHT = 46
        SEGMENT_ALT_HEIGHT = 24
        SEGMENT_WIDTH = 72
        bottomSegments = random.randint(1, 4)
        topSegments = 5 - bottomSegments

        self.gap = [topSegments * SEGMENT_HEIGHT + SEGMENT_ALT_HEIGHT, DISPLAY_HEIGHT - bottomSegments * SEGMENT_HEIGHT - SEGMENT_ALT_HEIGHT]
        self.x = DISPLAY_WIDTH - SEGMENT_WIDTH

        self.segments:list[GameSprite] = list()
        for i in range(topSegments):
            self.segments.append(GameSprite(
                'imgs/column_base_segment.png', DISPLAY_WIDTH - SEGMENT_WIDTH, i * SEGMENT_HEIGHT, SEGMENT_WIDTH, SEGMENT_HEIGHT
                ))
        self.segments.append(GameSprite(
            'imgs/column_top.png', DISPLAY_WIDTH - SEGMENT_WIDTH, topSegments * SEGMENT_HEIGHT, SEGMENT_WIDTH, SEGMENT_ALT_HEIGHT
            ))
        for j in range(bottomSegments):
            self.segments.append(GameSprite(
                'imgs/column_base_segment.png', DISPLAY_WIDTH - SEGMENT_WIDTH, DISPLAY_HEIGHT - (j + 1) * SEGMENT_HEIGHT, SEGMENT_WIDTH, SEGMENT_HEIGHT
                ))
        self.segments.append(GameSprite(
            'imgs/column_bottom.png', DISPLAY_WIDTH - SEGMENT_WIDTH, DISPLAY_HEIGHT - bottomSegments * SEGMENT_HEIGHT - SEGMENT_ALT_HEIGHT, SEGMENT_WIDTH, SEGMENT_ALT_HEIGHT
            ))
        
        for s in self.segments:
            game.columnSegmentsGroup.add(s)

    def move(self):
        for s in self.segments:
            s.rect.x -= game.COLUMN_MOVESPEED
            if s.rect.x < 0:
                s.kill()
        self.x -= game.COLUMN_MOVESPEED

    def renderColumn(self):
        for s in self.segments:
            s.renderSprite()


class FlappyBird(GameSprite):
    def __init__(self, img_path, x, y, w=64, h=41, vel=1, accel=0.33, isAi=True):
        super().__init__(img_path, x, y, w, h)

        self.velocity = vel
        self.acceleration = accel
        self.score = 0

        if isAi:
            self.ai = FlappyBirdAi(self, noise_order='invscale')

    def renderScore(self):
        self.scoreText = font.Font(None, 24).render(
            'score: ' + str(self.score),
            True,
            (0, 0, 0)
        )
        win.blit(self.scoreText, (0, 0))

    def gravityMoment(self):
        self.rect.y += self.velocity
        self.velocity += self.acceleration

    def jump(self):
        try:
            nextColumn = None
            for c in game.columns:
                if c.x > 0:
                    nextColumn = c
                    break

            j = self.ai.calculateJumpOutput(
                y=self.rect.y,
                vlc=self.velocity,
                dist=nextColumn.x - self.rect.x,
                y_gap=nextColumn.gap,
                )
            if j:
                self.velocity = -2.5
        except AttributeError:  # non-ai bird
            if key.get_pressed()[K_SPACE]:
                self.velocity = -2.5

class FlappyBirdAi():
    def __init__(self, parent:FlappyBird, noise_order:float|Literal['invscale']=0.05) -> None:
        '''
        Noise amplitude can be either fixed or inversely scaled from the previous generation's best score.

        The higher the score, the smaller the amplitude (25% amplitude for best score of 100, 12.5% for 200 etc.).'''
        self.parent = parent

        try:
            if noise_order == 'invscale':
                noise_order = 25 / game.tracker.bestScore
            
            # generate noise
            noise1 = 1 + noise_order * (np.random.rand(4, 7) * 2 - 1)
            noise2 = 1 + noise_order * (np.random.rand(7, 2) * 2 - 1)

            self.w1 = game.tracker.bestW1 * noise1
            self.w2 = game.tracker.bestW2 * noise2
        except:
            self.w1 = np.random.rand(4, 7)
            self.w2 = np.random.rand(7, 2)

    def calculateJumpOutput(self, y:int, vlc:int, dist:float, y_gap:list[int, int]) -> bool:
        '''
        Inputs:
            `y` - current y coordinate of the Bird;\n
            `vlc` - current vertical velocity of the Bird;\n
            `dist` - distance (along the x axis) to the next column;\n
            `y_gap : list[y_gap_top, y_gap_bottom]` - gap's y coordinates at the next column.\n
        Output:
            If the Bird jumps or not.
        '''

        # normalize the values to 0-1 range
        inputs = np.array([
            y / DISPLAY_HEIGHT,
            vlc / 10,
            dist / DISPLAY_WIDTH,
            sum(y_gap) / (2 * DISPLAY_HEIGHT)
            ]).reshape((1, 4))
        
        hidden = inputs @ self.w1

        outputs = hidden @ self.w2

        if outputs[0][0] > outputs[0][1]:
            return True
        
        return False

game = FlappyBirdGame()
game.startGame()

while game.gaming:
    for e in event.get():
        if e.type == QUIT:
            game.gaming = False

    if not game.finish:
        win.fill((0, 192, 255))

        if game.toNextColumn > 0:
            game.toNextColumn -= 1
        else:
            game.toNextColumn = game.SPAWN_COLUMN_COOLDOWN
            cm = Column()
            game.columns.append(cm)

        for cm in game.columns:
            cm.move()
            cm.renderColumn()
        
        for bird in game.birds:
            bird.renderSprite()
            bird.gravityMoment()
            bird.jump()

            bird.score += 1

            if not 0 < bird.rect.y < DISPLAY_HEIGHT - bird.rect.height or sprite.spritecollide(
                bird,
                game.columnSegmentsGroup,
                False
            ):
                game.birds.remove(bird)
                if bird.score >= game.tracker.bestScore:
                    game.tracker.updateWeights(bird.ai.w1, bird.ai.w2)
                    game.tracker.bestScore = bird.score

        win.blit(font.Font(None, 24).render(
            'generation: ' + str(game.tracker.generations),
            True,
            (0, 0, 0)
            ),
            (0, 0)
        )

        win.blit(font.Font(None, 24).render(
            'alive: ' + str(len(game.birds)),
            True,
            (0, 0, 0)
            ),
            (0, 20)
        )

        win.blit(font.Font(None, 24).render(
            'best score: ' + str(game.tracker.bestScore),
            True,
            (0, 0, 0)
            ),
            (0, 40)
        )

        if len(game.birds) == 0:
            print(f'************* GENERATION {game.tracker.generations} *************')
            print("Generation's best score:", game.tracker.bestScore)
            print("Next generation starts with weights noisified by " + str(round(2500 / game.tracker.bestScore, 2)) + '%:')
            print("Generation's best weights:\n", game.tracker.bestW1.reshape((1, 28)), '\n', game.tracker.bestW2.reshape((1, 14)), '\n')
            game.tracker.generations += 1
            
            game.startGame()
            game.tracker.bestScore = 0

    display.update()
    clock.tick(30)
