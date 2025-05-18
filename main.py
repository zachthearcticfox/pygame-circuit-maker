import pygame, sys

class Block:
    def __init__(self, type_, pos):
        self.type = type_  # block type
        self.pos = pos  # block position
        self.state = False  # block state
        self.next_state = False  # next block state
        match self.type:
            case 'NOT':
                self.colour_on = (255, 0, 0)  # red
            case 'AND':
                self.colour_on = (0, 0, 255)  # blue
            case 'XOR':
                self.colour_on = (127, 0, 255)  # purple
            case 'OR':
                self.colour_on = (0, 255, 0)  # green
            case 'TFLIPFLOP':
                self.colour_on = (45, 45, 45)  # black
            case 'NODE':
                self.colour_on = (255, 255, 255)  # white
        self.colour_off = tuple(max(int(c * 0.8), 0) for c in self.colour_on)  # darkens colour_on by 20%
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25), self.colour_off)  # creates rect to render
        self.inputs = []

    def update_rect(self):
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25),
                     self.colour_on if self.state else self.colour_off)  # updates rendered rect to turn on and off

blocks = []
mode = 'build'
block = 'NOT'
tps = 20

wre_1 = None
wre_2 = None

def update_blockswires():  # updates the rect for all blocks
    for i in blocks:
        i.update_rect()

pygame.init()

screen = pygame.display.set_mode((pygame.display.Info().current_w * 0.75, pygame.display.Info().current_h * 0.75))
pygame.display.set_caption('Pygame Circuit Maker')
clock = pygame.time.Clock()

def tick():
    global blocks
    for idx, blk in enumerate(blocks):
        blk.state = blk.next_state

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            print(f'click at: {mx}, {my}')
            if mode == 'build':
                blocks.append(Block(block, (mx, my)))
            elif mode == 'delete':
                for idx, i in enumerate(blocks):
                    rect, color = i.rect
                    if rect.collidepoint(event.pos):
                        blocks.remove(i)
            elif mode == 'wire':
                if wre_1 is None:
                    for i in blocks:
                        if i.rect[0].collidepoint(event.pos):
                            wre_1 = i
                            break
                elif wre_2 is None:
                    for i in blocks:
                        if i.rect[0].collidepoint(event.pos):
                            wre_2 = i
                            if wre_2 != wre_1:
                                wre_2.inputs.append(wre_1)
                            wre_1 = None
                            wre_2 = None
                            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                block = 'NOT'
            if event.key == pygame.K_2:
                block = 'AND'
            if event.key == pygame.K_3:
                block = 'XOR'
            if event.key == pygame.K_4:
                block = 'OR'
            if event.key == pygame.K_5:
                block = 'TFLIPFLOP'
            if event.key == pygame.K_6:
                block = 'NODE'
            if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
                if event.key == pygame.K_1:
                    mode = 'build'
                    print(mode)
                if event.key == pygame.K_2:
                    mode = 'delete'
                    print(mode)
                if event.key == pygame.K_3:
                    mode = 'wire'
                    print(mode)

    screen.fill((0, 0, 0))
    for i in blocks:
        pygame.draw.rect(screen, i.rect[1], i.rect[0])
        for j in i.inputs:
            pygame.draw.line(screen, (255, 255, 255), (i.pos[0], i.pos[1]+12), (j.pos[0]+25, j.pos[1]+12))
    pygame.display.flip()
    clock.tick(60)
