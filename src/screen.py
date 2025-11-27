class Button:
    def __init__(self,x,y,width,height,text,font,buttoncolor,textcolor):
        self.rect=pygame.Rect(x,y,width,height)

        self.text=text
        self.font=font
        self.buttoncolor=buttoncolor
        self.textcolor=textcolor

    def draw(self, screen):
        pygame.draw.rect(screen, self.buttoncolor,self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        def isclicked(self, mouse_pos, mousepressed):
            return(self.rect.colidepoint(mouse_pos)
                   and mousepressed[0])