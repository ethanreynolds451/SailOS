import tkinter as tk
import pygame
from pygame.locals import *

class PygameWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.init_pygame()
        self.init_ui()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption('Pygame Window')

    def init_ui(self):
        self.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        self.after(50, self.update_pygame)

    def on_canvas_resize(self, event):
        size = (event.width, event.height)
        self.screen = pygame.display.set_mode(size)

    def update_pygame(self):
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            # Handle other Pygame events here

        # Update Pygame display
        pygame.draw.circle(self.screen, (255, 0, 0), (200, 150), 50)
        pygame.display.flip()

        # Call this function again after a short delay
        self.after(30, self.update_pygame)

if __name__ == '__main__':
    root = tk.Tk()
    app = PygameWindow(master=root)
    app.mainloop()
