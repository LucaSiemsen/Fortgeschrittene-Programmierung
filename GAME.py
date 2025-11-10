import pygame
import sys
pygame.init()
#bildschirm wird auf vollbild festgelegt, die clock ist für die fps damit das spiel auf jedem bildschirm gleich schnell läuft.

screen= pygame.display.set_mode((0,0), pygame.FULLSCREEN)
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
clock= pygame.time.Clock()




#Konstanten
wide_ratio=0.07
height_ratio=0.15
wide_ratio_block=0.08
height_ratio_block=0.16
b_list_test=[1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
b_zeilen=10
b_spalten=10




pygame.display.set_caption("Dig or Exma")
#ZEILE 18 bis 23 ki generiert
#nützliche hilfsklassen (falls noch jemand welche schreibt gerne hier rein)


#pictureloader einfach bei allem als elternklasse rein wo bilder benötigt werden.
class PictureLoader:
    def __init__(self,bildpfad,wide_ratio=None,height_ratio=None, ):
        info = pygame.display.Info()
        self.wide = int(info.current_w * wide_ratio) if wide_ratio else info.current_w
        self.height = int(info.current_h * height_ratio) if height_ratio else info.current_h
        self.bild = pygame.image.load(bildpfad).convert_alpha()
        self.bild = pygame.transform.scale(self.bild, (self.wide, self.height))
    def draw (self, screen,x,y,):
        self.x=x
        self.y=y
        self.screen=screen
        screen.blit(self.bild, (x,y))
    
        


#hier die klassen für alle objekte rein:
class Student (PictureLoader):
    def __init__(self,x,y,speed, bildpfad,wide_ratio,height_ratio):
        super().__init__(bildpfad, wide_ratio, height_ratio)
        self.x=x
        self.y=y
        self.speed= speed
    def studentmovement(self,gedrueckt,WIDTH,HEIGHT): 
        #bewegung des spielercharakters die kollisionserkennung also der teil nach and ist ki generiert
        "gedrueckt= pygame.key.get_pressed()"
        if gedrueckt[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if gedrueckt[pygame.K_DOWN] and self.y + self.height < HEIGHT:
            self.y += self.speed
        if gedrueckt[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if gedrueckt[pygame.K_RIGHT] and self.x + self.wide < WIDTH:
            self.x += self.speed

#ist ne klasse um noch die kollisionsmethode hinzuzufügen sowohl für den spieler als auch alle sprites
class Block(PictureLoader): 
    def __init__ (self,bildpfad,):
        self.block_widht= WIDTH/b_spalten
        self.block_height= HEIGHT/b_zeilen
        self.bild = pygame.image.load(bildpfad).convert_alpha()
        self.bild= pygame.transform.scale(self.bild, (self.block_widht, self.block_height))
        self.x=0
        self.y=0
    def Block_draw(self,screen,x,y):
        screen.blit (self.bild,(x,y)) 
  

class leerer_Block (PictureLoader):
    def __init__ (self,bildpfad):
        self.block_widht= WIDTH/b_spalten
        self.block_height= HEIGHT/b_zeilen
        self.bild = pygame.image.load(bildpfad).convert_alpha()
        self.bild= pygame.transform.scale(self.bild, (self.block_widht, self.block_height))
        self.x=0
        self.y=0
    def leerer_Block_draw(self,screen,x,y):
        screen.blit (self.bild,(x,y)) 
    def leerer_Block_move_right(self,):
        self.x += self.block_widht
    def leerer_Block_move_down (self):
        self.x +=self.block_height

        



    

#hier einfach alle bilder mit hilfe von name=pictureloader("pfad zum bild",wide_ratio,height_ratio) rein bei sprites spielfigur diese zahlen noch eintragen sorgt für die skalierung
hintergrund=PictureLoader("parallax-forest-back-trees.png")
student= Student(600,0,3,"student.png",wide_ratio,height_ratio)


#die spielschleife. fenster skaliert sich immer auf Vollbild und kann mit einmaligem drücken von esc geschlossen werden. 
go= True
while go:
    for event in pygame.event.get():
        if event.type== pygame.KEYDOWN and event.key == pygame.K_ESCAPE: #ki generiert die schleife sorgt eigentlich nur dafür das das spiel dauerhaft wartet bis esc gedrückt wird
            pygame.quit()
            sys.exit()
    gedrueckt=pygame.key.get_pressed()
    student.studentmovement(gedrueckt,WIDTH,HEIGHT)
    
    
    
    #hier alle Objekte rein die gezeichnet werden nutzt .draw gehört zum pictureloader und spart code.
    hintergrund.draw(screen,0,0)
    student.draw(screen,student.x,student.y)

   
    x=0
    y=0
    block_widht= WIDTH/b_spalten
    block_height= HEIGHT/b_zeilen
    index=0# ki generiert
    

    for zeile in range (b_zeilen):# ki generiert
        for spalte in range (b_spalten):# ki generiert
            if index< len(b_list_test):
                    zahl=b_list_test[index]
                    if zahl==1:
                        block=Block("Buchblock-1.png.png")
                        block.draw(screen,x,y)
                        
                
                    else:
                        leererblock=leerer_Block("leerer block.png")
                        leererblock.draw(screen,x,y)
                        

                    x+=  block_widht# ki generiert
                    index+=1# ki generiert
        x=0# ki generiert
        y+=block_height# ki generiert
                


                
           
    
   
    
            


    pygame.display.update()


    clock.tick(60)

   