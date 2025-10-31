import wx
import random
import math

# -------------------- Capa Lógica --------------------

class Especie:
    def __init__(self, x, y, vida):
        self.posicion_x = x
        self.posicion_y = y
        self.vida = vida
        self.edad = 0
        self.viva = True
        self.salto = 4.5  # velocidad ajustada para fluidez
        self.direccion = random.uniform(0, 2 * math.pi)
        self.ya_reprodujo = False

    def puede_reproducirse_con(self, otra):
        return (
            type(self) == type(otra) and
            self.viva and otra.viva and
            not self.ya_reprodujo and
            not otra.ya_reprodujo and
            self != otra and
            ((self.posicion_x - otra.posicion_x)**2 + (self.posicion_y - otra.posicion_y)**2)**0.5 < 20
        )

    def mover(self):
        self.direccion += random.uniform(-0.05, 0.05)  # variación suave
        dx = math.cos(self.direccion) * self.salto
        dy = math.sin(self.direccion) * self.salto
        self.posicion_x += dx
        self.posicion_y += dy

        # rebote en bordes
        if self.posicion_x <= 0 or self.posicion_x >= 480:
            self.direccion = math.pi - self.direccion
        if self.posicion_y <= 0 or self.posicion_y >= 380:
            self.direccion = -self.direccion

        self.posicion_x = max(0, min(480, self.posicion_x))
        self.posicion_y = max(0, min(380, self.posicion_y))

    def envejecer(self):
        self.edad += 1
        if self.edad > 500 or self.vida <= 0:
            self.viva = False

    def reproducir(self, otros):
        return None


class Planta(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=999)

    def mover(self):
        pass


class Herbivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=100)

    def comer(self, plantas):
        for planta in plantas:
            distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
            if distancia < 30:
                self.vida += 10
                planta.viva = False

    def reproducir(self, otros):
        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.ya_reprodujo = True
                otro.ya_reprodujo = True
                return Herbivoro(self.posicion_x, self.posicion_y)
        return None


class Carnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=120)

    def cazar(self, presas):
        for presa in presas:
            distancia = ((self.posicion_x - presa.posicion_x)**2 + (self.posicion_y - presa.posicion_y)**2)**0.5
            if distancia < 30:
                self.vida += 15
                presa.viva = False

    def reproducir(self, otros):
        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.ya_reprodujo = True
                otro.ya_reprodujo = True
                return Carnivoro(self.posicion_x, self.posicion_y)
        return None


class Omnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=110)

    def alimentarse(self, plantas, herbivoros):
        for planta in plantas:
            distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
            if distancia < 30:
                self.vida += 8
                planta.viva = False
                return
        for herbivoro in herbivoros:
            distancia = ((self.posicion_x - herbivoro.posicion_x)**2 + (self.posicion_y - herbivoro.posicion_y)**2)**0.5
            if distancia < 30:
                self.vida += 12
                herbivoro.viva = False
                return

    def reproducir(self, otros):
        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.ya_reprodujo = True
                otro.ya_reprodujo = True
                return Omnivoro(self.posicion_x, self.posicion_y)
        return None


class Ecosistema:
    def __init__(self):
        self.entidades = []

    def agregar(self, especie):
        self.entidades.append(especie)

    def simular_turno(self):
        nuevas_entidades = []

        plantas = [e for e in self.entidades if isinstance(e, Planta) and e.viva]
        herbivoros = [e for e in self.entidades if isinstance(e, Herbivoro) and e.viva]
        carnivoros = [e for e in self.entidades if isinstance(e, Carnivoro) and e.viva]
        omnivoros = [e for e in self.entidades if isinstance(e, Omnivoro) and e.viva]

        for e in self.entidades:
            if e.viva:
                e.mover()
                nuevo = None
                if isinstance(e, Herbivoro):
                    e.comer(plantas)
                    nuevo = e.reproducir(herbivoros)
                elif isinstance(e, Carnivoro):
                    e.cazar(herbivoros)
                    nuevo = e.reproducir(carnivoros)
                elif isinstance(e, Omnivoro):
                    e.alimentarse(plantas, herbivoros)
                    nuevo = e.reproducir(omnivoros)
                e.envejecer()
                if nuevo:
                    nuevas_entidades.append(nuevo)

        self.entidades = [e for e in self.entidades if e.viva] + nuevas_entidades

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
        self.timer.Start(16)  # ✅ 60 FPS

        self.ventana.Centre()
        self.ventana.Show()

    def inicializar_entidades(self):
        for _ in range(999):
            self.ecosistema.agregar(Planta(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(99):
            self.ecosistema.agregar(Herbivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(24):
            self.ecosistema.agregar(Carnivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(12):
            self.ecosistema.agregar(Omnivoro(random.randint(50, 450), random.randint(50, 350)))

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBackground(wx.Brush('forest green'))
        dc.Clear()

        for e in self.ecosistema.entidades:
            if isinstance(e, Planta):
                dc.SetBrush(wx.Brush('yellow'))
            elif isinstance(e, Herbivoro):
                dc.SetBrush(wx.Brush('sky blue'))
            elif isinstance(e, Carnivoro):
                dc.SetBrush(wx.Brush('red'))
            elif isinstance(e, Omnivoro):
                dc.SetBrush(wx.Brush('purple'))
            dc.DrawCircle(int(e.posicion_x), int(e.posicion_y), 10)

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
