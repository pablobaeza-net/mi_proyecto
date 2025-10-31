import wx
import random

# -------------------- Capa Lógica --------------------

class Especie:
    def __init__(self, x, y, vida):
        self.posicion_x = x
        self.posicion_y = y
        self.vida = vida
        self.edad = 0
        self.viva = True
        self.salto = 5

    def mover(self):
        dx = random.choice([-1, 0, 1]) * self.salto
        dy = random.choice([-1, 0, 1]) * self.salto
        self.posicion_x = max(0, min(480, self.posicion_x + dx))
        self.posicion_y = max(0, min(380, self.posicion_y + dy))

    def envejecer(self):
        self.edad += 1
        if self.edad > 50 or self.vida <= 0:
            self.viva = False

class Planta(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=999)


class Herbivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=100)

    def comer(self, plantas):
        for planta in plantas:
            distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
            if distancia < 20:
                self.vida += 10
                planta.viva = False

class Carnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=120)

    def cazar(self, presas):
        for presa in presas:
            distancia = ((self.posicion_x - presa.posicion_x)**2 + (self.posicion_y - presa.posicion_y)**2)**0.5
            if distancia < 20:
                self.vida += 15
                presa.viva = False

class Omnivoro(Especie):
    def __init__(self, x, y, vida=200)

    def alimentarse(self, plantas, herbivoros):
        for plantas in plantas:
            distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
            if distancia < 20:
                self.vida += 8
                planta.viiva = False
                return
        for herbivoro in herbivoros:
            distancia = ((self.posicion_x - herbivoro.posicion_x)**2 + (self.posicion_y - herbivoro.posicion_y)**2)**0.5
            if distancia <20:
                self.vida +=12
                herbivoro.vida = False
                return
class Ecosistema:
    def __init__(self):
        self.entidades = []

    def agregar(self, especie):
        self.entidades.append(especie)

    def simular_turno(self):
        plantas = [e for e in self.entidades if isinstance(e, Planta) and e.viva]
        herbivoros = [e for e in self.entidades if isinstance(e, Herbivoro) and e.viva]
        carnivoros = [e for e in self.entidades if isinstance(e, Carnivoro) and e.viva]
        omnivoros = [e for e in self.entidades if isinstance(e, Omnivoro) and e.viva]
        

        for e in self.entidades:
            if e.viva:
                e.mover()
                if isinstance(e, Herbivoro):
                    e.comer(plantas)
                elif isinstance(e, Carnivoro):
                    e.cazar(herbivoros)
                elif isinstance(e, Omnivoros)
                    e.alimentarse(plantas, herbivoros)
                e.envejecer()

        self.entidades = [e for e in self.entidades if e.viva]

# -------------------- Capa Vista --------------------

class VistaEcosistema:
    def __init__(self):
        self.app = wx.App()
        self.ventana = wx.Frame(None, title="Ecosistema Virtual", size=(500, 400))
        self.panel = wx.Panel(self.ventana)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.panel.SetFocus()

        self.ecosistema = Ecosistema()
        self.inicializar_entidades()

        self.timer = wx.Timer(self.panel)
        self.panel.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(500)

        self.ventana.Centre()
        self.ventana.Show()

    def inicializar_entidades(self):
        for _ in range(5):
            self.ecosistema.agregar(Planta(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(3):
            self.ecosistema.agregar(Herbivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(2):
            self.ecosistema.agregar(Carnivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(2):
            self.ecosistema.agregar(Omnivoro(random.raditn(50,450), random.radint(50, 350)))

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)

        dc.SetBackground(wx.Brush('forest green'))
        dc.Clear()

        planta_posiciones = [(50, 50), (100, 300), (400, 100), (300, 250)]
        dc.SetBrush(wx.Brush('dark green'))
        for x, y in planta_posiciones:
            dc.DrawCircle(x, y, 8)
       
        for e in self.ecosistema.entidades:
            if isinstance(e, Planta):
                dc.SetBrush(wx.Brush('lime green'))
            elif isinstance(e, Herbivoro):
                dc.SetBrush(wx.Brush('sky blue'))
            elif isinstance(e, Carnivoro):
                dc.SetBrush(wx.Brush('firebrick'))
            elif isinstance(e, Omnivoro):
                dc.SetBrush(wx.Brush('purple'))
            dc.DrawCircle(e.posicion_x, e.posicion_y, 10)

    def on_timer(self, event):
        self.ecosistema.simular_turno()
        self.panel.Refresh()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.ventana.Close()

    def iniciar(self):
        self.app.MainLoop()
# -------------------- Main --------------------

if __name__ == "__main__":
    print("=== Simulador de Ecosistema Virtual ===")
    vista = VistaEcosistema()
    vista.iniciar()
