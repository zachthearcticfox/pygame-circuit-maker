import pygame, sys, time

class Block:
    def __init__(self, type_, pos):
        self.type = type_
        self.pos = pos
        self.state = False
        self.next_state = False
        match self.type:
            case 'NOT':
                self.colour_on = (255, 0, 0)
            case 'AND':
                self.colour_on = (0, 0, 255)
            case 'XOR':
                self.colour_on = (127, 0, 255)
            case 'OR':
                self.colour_on = (0, 255, 0)
            case 'TFLIPFLOP':
                self.colour_on = (60, 60, 60)
            case 'NODE':
                self.colour_on = (255, 255, 255)
            case 'SOUND':
                self.colour_on = (234, 182, 118)
        self.colour_off = tuple(max(int(c * 0.6), 0) for c in self.colour_on)
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25), self.colour_off)
        self.inputs = []

    def update_rect(self):
        self.rect = (pygame.Rect(self.pos[0], self.pos[1], 25, 25),
                     self.colour_on if self.state else self.colour_off)

blocks = []
mode = 'build'
block = 'NOT'
tps = 20
wre_1 = None
wre_2 = None
selecting = False
select_start = None
select_end = None
selected_blocks = []
right_dragging = False
last_mouse_pos = (0, 0)

print("""Controls:
1 through 6: Change block
Ctrl+1 through Ctrl+5: Change tool
0: Print state and next state for all blocks
Del: Delete selection
Right Click + Drag: Move selection""")

def update_blockswires():
    for i in blocks:
        i.update_rect()

idxconv = ['NOT', 'AND', 'XOR', 'OR', 'TFLIPFLOP', 'NODE', 'SOUND']

def import_from_file(fp):
    global blocks
    blocks = []
    with open(fp, 'r') as fr:
        contents = fr.read().split('?')
        if contents == ['', ''] or contents == ['']:
            return
    blocks_i = contents[0].split(';')
    wires_i = contents[1].split('+')
    for i in range(len(blocks_i)):
        blocks_i[i] = tuple(map(int, blocks_i[i].split(',')))
    for i in range(len(wires_i)):
        wires_i[i] = tuple(map(int, wires_i[i].split(',')))
    for idx, blk in enumerate(blocks_i):
        blocks.append(Block(idxconv[blk[0]-1], (blk[2], blk[3])))
    for i in wires_i:
        blocks[i[1]].inputs.append(blocks[i[0]])
    return blocks_i, wires_i

def export_to_file(fp):
    global blocks
    output_blks = []
    output_wres = []
    for i in blocks:
        output_blks.append(f'{idxconv.index(i.type)+1},{int(i.state)},{i.pos[0]},{i.pos[1]}')
        for j in i.inputs:
            output_wres.append(f'{blocks.index(j)},{blocks.index(i)}')
    output_blks = ';'.join(output_blks)
    output_wres = '+'.join(output_wres)
    output = f'{output_blks}?{output_wres}'
    with open(fp, 'w') as fw:
        fw.write(output)
    return output

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((pygame.display.Info().current_w * 0.75, pygame.display.Info().current_h * 0.75))
pygame.display.set_caption('Pygame Circuit Maker v0.3')
clock = pygame.time.Clock()
pygame.mixer.music.load('soundblock.mp3')

import_from_file('main.save')

def tick():
    global blocks, tps
    time.sleep(1 / tps)
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
            case 'SOUND':
                blk.next_state = inputs[0] if inputs else False
                if blk.state == True:
                    pygame.mixer.music.play(1)
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
            elif mode == 'select':
                selecting = True
                select_start = event.pos
                select_end = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if selecting and mode == 'select':
                selecting = False
                select_end = event.pos
                selected_blocks.clear()
                x1, y1 = select_start
                x2, y2 = select_end
                selection_rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                for blk in blocks:
                    if selection_rect.colliderect(blk.rect[0]):
                        selected_blocks.append(blk)
                print(f"selected {len(selected_blocks)} blocks.")

        elif event.type == pygame.MOUSEMOTION and selecting and mode == 'select':
            select_end = event.pos

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            right_dragging = True
            last_mouse_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            right_dragging = False

        elif event.type == pygame.MOUSEMOTION and right_dragging:
            current_mouse_pos = event.pos
            dx = current_mouse_pos[0] - last_mouse_pos[0]
            dy = current_mouse_pos[1] - last_mouse_pos[1]
            for blk in selected_blocks:
                blk.pos = (blk.pos[0] + dx, blk.pos[1] + dy)
                blk.update_rect()
            last_mouse_pos = current_mouse_pos

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
            if event.key == pygame.K_7:
                block = 'SOUND'
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
                if event.key == pygame.K_5:
                    mode = 'select'
                    print(mode)
            if event.key == pygame.K_0:
                for i in blocks:
                    print(i.next_state, i.state)
            if event.key == pygame.K_DELETE:
                for i in selected_blocks:
                    blocks.remove(i)

    screen.fill((0, 0, 0))
    tick()
    export_to_file('main.save')

    for i in blocks:
        pygame.draw.rect(screen, i.rect[1], i.rect[0])
        if i in selected_blocks:
            pygame.draw.rect(screen, (255, 255, 0), i.rect[0], 2)
        i.update_rect()
        for j in i.inputs:
            pygame.draw.line(screen, (255, 255, 255), i.pos, (j.pos[0] + 25, j.pos[1]))

    if selecting and select_start and select_end and mode == 'select':
        x1, y1 = select_start
        x2, y2 = select_end
        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
        pygame.draw.rect(screen, (0, 255, 0), rect, 1)

    pygame.display.flip()
    clock.tick(60)
