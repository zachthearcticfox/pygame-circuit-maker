import pygame, sys, time

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
                self.colour_on = (60, 60, 60)  # black
            case 'NODE':
                self.colour_on = (255, 255, 255)  # white
        self.colour_off = tuple(max(int(c * 0.6), 0) for c in self.colour_on)  # darkens colour_on by 40%
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25), self.colour_off)  # creates rect to render
        self.inputs = [] # blocks that are connected to this block

    def update_rect(self):
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25),
                     self.colour_on if self.state else self.colour_off)  # updates rendered rect to turn on and off

blocks = [] # where the blocks are stored
mode = 'build' # mode (build, wire, etc.)
block = 'NOT' # selected block
tps = 20 # ticks / second

# the blocks for the wiring system
wre_1 = None
wre_2 = None

print("""Controls:
1 through 6: Change block
Ctrl+1 through Ctrl+4: Change tool
0: Print state and next state for all blocks""")

def update_blockswires():  # updates the rect for all blocks
    for i in blocks:
        i.update_rect()

pygame.init() # initialize pygame

screen = pygame.display.set_mode((pygame.display.Info().current_w * 0.75, pygame.display.Info().current_h * 0.75)) # screen surface
pygame.display.set_caption('Pygame Circuit Maker') # changes window name
clock = pygame.time.Clock() # pygame clock

def tick():
    global blocks, tps
    time.sleep(1/tps) # tps delay

    for idx, blk in enumerate(blocks):
        inputs = [inp.state for inp in blk.inputs]
        match blk.type:
            case 'NOT':
                blk.next_state = not inputs[0] if len(inputs) >= 1 else True
            case 'AND':
                blk.next_state = all(inputs) if inputs else False
            case 'OR':
                blk.next_state = any(inputs) if inputs else False
            case 'XOR':
                blk.next_state = sum(inputs) % 2 == 1 if inputs else False
            case 'NODE':
                blk.next_state = inputs[0] if inputs else False
        
    for blk in blocks:
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
            elif mode == 'interact':
                for i in blocks:
                    if i.rect[0].collidepoint(event.pos):
                        if i.type == 'TFLIPFLOP':
                            i.next_state = not i.state
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
                if event.key == pygame.K_4:
                    mode = 'interact'
                    print(mode)
            if event.key == pygame.K_0:
                for i in blocks:
                    print(i.next_state, i.state)

    screen.fill((0, 0, 0))
    tick()
    for i in blocks:
        pygame.draw.rect(screen, i.rect[1], i.rect[0])
        i.update_rect()
        for j in i.inputs:
            pygame.draw.line(screen, (255, 255, 255), i.pos, (j.pos[0]+25, j.pos[1]))
    pygame.display.flip()
    clock.tick(60)
