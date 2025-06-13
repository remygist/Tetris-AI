from settings import *

class Preview:
    def __init__(self, next_shapes, topleft=(PADDING, PADDING)):

        self.surface = pygame.Surface((SIDEBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION))
        self.rect = self.surface.get_rect(topleft=topleft)
        self.display_surface = pygame.display.get_surface()

        # list of upcoming shapes
        self.next_shapes = next_shapes

    def draw_preview(self):
        self.surface.fill(GRAY)

        slot_height = 4 * CELL_SIZE
        slot_padding = 20

        # draw upcoming shape
        for i, shape_key in enumerate(self.next_shapes):
            shape_data = TETROMINOS[shape_key]['shape']
            color = TETROMINOS[shape_key]['color']

            # get bounding box of the shape
            xs = [x for x, y in shape_data]
            ys = [y for x, y in shape_data]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            shape_height = (max_y - min_y + 1) * CELL_SIZE
            shape_width = (max_x - min_x + 1) * CELL_SIZE

            # center shape in slot
            x_offset = (SIDEBAR_WIDTH - shape_width) // 2
            y_base = i * (slot_height + slot_padding)
            y_offset = y_base + (slot_height - shape_height) // 2

            # draw shape
            for x, y in shape_data:
                nx = x - min_x
                ny = y - min_y
                block_rect = pygame.Rect(
                    x_offset + nx * CELL_SIZE,
                    y_offset + ny * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.surface, color, block_rect)
                pygame.draw.rect(self.surface, 'black', block_rect, width=2)

    def run(self):
        self.display_surface.blit(self.surface, self.rect)
        self.draw_preview()
        pygame.draw.rect(self.display_surface, 'white', self.rect, width=2, border_radius=4)
