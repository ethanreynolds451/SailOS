import tkinter as tk
import pygame
from pygame.locals import *
from PIL import Image, ImageTk

class PygameTkinterIntegration(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.init_pygame()
        self.init_ui()

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.Surface((400, 300))
        pygame.display.set_caption('Pygame in Tkinter')

    def init_ui(self):
        self.pack(fill=tk.BOTH, expand=True)

        # Create a label to display the Pygame content
        self.pygame_label = tk.Label(self)
        self.pygame_label.pack(fill=tk.BOTH, expand=True)

        # Create other tkinter widgets
        self.button = tk.Button(self, text="Click Me", command=self.button_clicked)
        self.button.pack()

        # Update Pygame display in Tkinter window
        self.update_pygame()

    def button_clicked(self):
        print("Button clicked!")

    def update_pygame(self):
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            # Handle other Pygame events here

        # Update Pygame display
        self.screen.fill((255, 255, 255))
        pygame.draw.circle(self.screen, (255, 0, 0), (200, 150), 50)

        # Convert Pygame surface to a Tkinter-compatible format
        img = Image.frombytes('RGB', self.screen.get_size(), pygame.image.tostring(self.screen, 'RGB'))
        img_tk = ImageTk.PhotoImage(image=img)

        # Update the label with the new image
        self.pygame_label.configure(image=img_tk)
        self.pygame_label.image = img_tk

        # Call this function again after a short delay
        self.after(30, self.update_pygame)

if __name__ == '__main__':
    root = tk.Tk()
    app = PygameTkinterIntegration(master=root)
    app.mainloop()
