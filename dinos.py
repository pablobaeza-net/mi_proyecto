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
        self.salto = 2.0
        self.direccion = random.uniform(0, 2 * math.pi)
        self.ya_reprodujo = False
        self.cooldown_comer = 0
        self.cooldown_repro = 0

    def puede_reproducirse_con(self, otra):
        return (
            type(self) == type(otra)
            and self.viva and otra.viva
            and not self.ya_reprodujo and not otra.ya_reprodujo
            and self != otra
            and self.cooldown_repro == 0 and otra.cooldown_repro == 0
            and ((self.posicion_x - otra.posicion_x)**2 + (self.posicion_y - otra.posicion_y)**2)**0.5 < 28
        )

    def mover(self):
        self.direccion += random.uniform(-0.06, 0.06)
        dx = math.cos(self.direccion) * self.salto
        dy = math.sin(self.direccion) * self.salto
        self.posicion_x += dx
        self.posicion_y += dy
        if self.posicion_x <= 0 or self.posicion_x >= 480:
            self.direccion = math.pi - self.direccion
        if self.posicion_y <= 0 or self.posicion_y >= 380:
            self.direccion = -self.direccion
        self.posicion_x = max(0, min(480, self.posicion_x))
        self.posicion_y = max(0, min(380, self.posicion_y))

    def envejecer(self):
        self.edad += 1
        self.vida -= 0.25
        if self.cooldown_comer > 0:
            self.cooldown_comer -= 1
        if self.cooldown_repro > 0:
            self.cooldown_repro -= 1
        if self.edad > 300000 or self.vida <= 0:  # 300k turnos
            self.viva = False

    def reproducir(self, otros=None):
        return None

# --- Plantas ---
class Planta(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=999)
        self.salto = 0

    def mover(self): pass

    def envejecer(self): self.vida = 999

    def reproducir(self, plantas=None):
        # Solo reproducir si hay menos de 39 plantas
        if plantas is not None and len(plantas) >= 39:
            return None
        if random.random() < 0.20:  # 20% por turno
            new_x = self.posicion_x + random.uniform(-25, 25)
            new_y = self.posicion_y + random.uniform(-25, 25)
            new_x = max(0, min(480, new_x))
            new_y = max(0, min(380, new_y))
            return Planta(new_x, new_y)
        return None

# --- Herbívoros ---
class Herbivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=900)

    def comer(self, plantas):
        if self.cooldown_comer > 0: return
        for planta in plantas:
            if planta.viva:
                distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
                if distancia < 20:
                    self.vida += 12
                    planta.viva = False
                    self.vida = min(self.vida, 1050)
                    self.cooldown_comer = 4
                    return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):  # dinos no superan plantas
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = True
                    otro.ya_reprodujo = True
                    self.cooldown_repro = 30
                    otro.cooldown_repro = 30
                    return Herbivoro(self.posicion_x, self.posicion_y)
        return None

# --- Carnívoros ---
class Carnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=950)

    def cazar(self, presas):
        if self.cooldown_comer > 0: return
        for presa in presas:
            if presa.viva:
                distancia = ((self.posicion_x - presa.posicion_x)**2 + (self.posicion_y - presa.posicion_y)**2)**0.5
                if distancia < 18:
                    self.vida += 14
                    presa.viva = False
                    self.vida = min(self.vida, 1150)
                    self.cooldown_comer = 6
                    return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = True
                    otro.ya_reprodujo = True
                    self.cooldown_repro = 40
                    otro.cooldown_repro = 40
                    return Carnivoro(self.posicion_x, self.posicion_y)
        return None

# --- Omnívoros ---
class Omnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=920)

    def alimentarse(self, plantas, herbivoros):
        if self.cooldown_comer > 0: return
        for planta in plantas:
            if planta.viva:
                distancia = ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
                if distancia < 20:
                    self.vida += 10
                    planta.viva = False
                    self.vida = min(self.vida, 1100)
                    self.cooldown_comer = 4
                    return
        for herbivoro in herbivoros:
            if herbivoro.viva:
                distancia = ((self.posicion_x - herbivoro.posicion_x)**2 + (self.posicion_y - herbivoro.posicion_y)**2)**0.5
                if distancia < 18:
                    self.vida += 11
                    herbivoro.viva = False
                    self.vida = min(self.vida, 1100)
                    self.cooldown_comer = 6
                    return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = True
                    otro.ya_reprodujo = True
                    self.cooldown_repro = 35
                    otro.cooldown_repro = 35
                    return Omnivoro(self.posicion_x, self.posicion_y)
        return None

# --- Ecosistema ---
class Ecosistema:
    def __init__(self):
        self.entidades = []
        self.turno = 0

    def agregar(self, especie):
        self.entidades.append(especie)

    def simular_turno(self):
        self.turno += 1
        nuevas_entidades = []
        for e in self.entidades:
            e.ya_reprodujo = False
        plantas = [e for e in self.entidades if isinstance(e, Planta) and e.viva]
        herbivoros = [e for e in self.entidades if isinstance(e, Herbivoro) and e.viva]
        carnivoros = [e for e in self.entidades if isinstance(e, Carnivoro) and e.viva]
        omnivoros = [e for e in self.entidades if isinstance(e, Omnivoro) and e.viva]

        for e in self.entidades:
            if e.viva:
                e.mover()
                nuevo = None
                if isinstance(e, Planta):
                    nuevo = e.reproducir(plantas)
                elif isinstance(e, Herbivoro):
                    e.comer(plantas)
                    nuevo = e.reproducir(herbivoros, plantas)
                elif isinstance(e, Carnivoro):
                    e.cazar(herbivoros)
                    nuevo = e.reproducir(carnivoros, plantas)
                elif isinstance(e, Carnivoro):
                    e.cazar(herbivoros)
                    nuevo = e.reproducir(carnivoros, plantas)
                elif isinstance(e, Omnivoro):
                    e.alimentarse(plantas, herbivoros)
                    nuevo = e.reproducir(omnivoros, plantas)

                e.envejecer()
                if nuevo:
                    nuevas_entidades.append(nuevo)

        self.entidades = [e for e in self.entidades if e.viva] + nuevas_entidades

# -------------------- Capa Vista --------------------

class VistaEcosistema:
    def __init__(self):
        self.app = wx.App()
        self.ventana = wx.Frame(None, title="Ecosistema Virtual (Estable y Largo - 60 FPS)", size=(500, 420))
        self.panel = wx.Panel(self.ventana)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.panel.SetFocus()

        self.ecosistema = Ecosistema()
        self.inicializar_entidades()

        # Timer de simulación: 200 ms por turno
        self.sim_timer = wx.Timer(self.panel)
        self.panel.Bind(wx.EVT_TIMER, self.on_sim_timer, self.sim_timer)
        self.sim_timer.Start(200)

        # Timer de dibujo: 60 FPS (16 ms)
        self.draw_timer = wx.Timer(self.panel)
        self.panel.Bind(wx.EVT_TIMER, self.on_draw_timer, self.draw_timer)
        self.draw_timer.Start(16)

        self.ventana.Centre()
        self.ventana.Show()

    def inicializar_entidades(self):
        # Más plantas para base sólida
        for _ in range(70):
            self.ecosistema.agregar(Planta(random.randint(50, 450), random.randint(50, 350)))
        # Balance inicial de dinos
        for _ in range(45):
            self.ecosistema.agregar(Herbivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(12):
            self.ecosistema.agregar(Carnivoro(random.randint(50, 450), random.randint(50, 350)))
        for _ in range(18):
            self.ecosistema.agregar(Omnivoro(random.randint(50, 450), random.randint(50, 350)))

    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBackground(wx.Brush('forest green'))
        dc.Clear()

        plantas = herbivoros = carnivoros = omnivoros = 0

        for e in self.ecosistema.entidades:
            x = int(e.posicion_x)
            y = int(e.posicion_y)
            max_life = 0

            if isinstance(e, Planta):
                plantas += 1
                dc.SetPen(wx.Pen('green', 2))
                dc.DrawLine(x, y+5, x, y-5)
                dc.SetBrush(wx.Brush('yellow'))
                dc.DrawCircle(x, y-5, 4)
                dc.SetBrush(wx.Brush('green'))
                dc.DrawEllipse(x-6, y-2, 12, 6)
                continue

            elif isinstance(e, Herbivoro):
                herbivoros += 1
                max_life = 1050
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 180), 3))       
                dc.SetBrush(wx.Brush(wx.Colour(100, 180, 255)))   
                dc.DrawRectangle(x-12, y-6, 24, 12)
                dc.DrawLine(x-12, y, x-20, y-10)
                dc.DrawCircle(x-20, y-10, 5)
                dc.DrawLine(x-6, y+6, x-6, y+15)
                dc.DrawLine(x+6, y+6, x+6, y+15)

            elif isinstance(e, Carnivoro):
                carnivoros += 1
                max_life = 1150
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 3))         
                dc.SetBrush(wx.Brush(wx.Colour(220, 0, 0)))       
                dc.DrawRectangle(x-15, y-7, 30, 14)
                dc.SetPen(wx.Pen('red', 1))
                dc.DrawLine(x-9, y+2, x-12, y+6)
                dc.DrawLine(x+9, y+2, x+12, y+6)
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 3))
                dc.DrawLine(x-4, y+7, x-4, y+18)
                dc.DrawLine(x+4, y+7, x+4, y+18)

            elif isinstance(e, Omnivoro):
                omnivoros += 1
                max_life = 1100
                dc.SetPen(wx.Pen(wx.Colour(120, 0, 120), 3))      
                dc.SetBrush(wx.Brush(wx.Colour(180, 0, 220)))     
                dc.DrawEllipse(x-12, y-7, 24, 14)
                dc.SetBrush(wx.Brush('orange'))
                dc.DrawPolygon([(x-3, y-7), (x, y-12), (x+3, y-7)])
                dc.DrawLine(x+12, y, x+18, y)

            # Barra de vida
            if max_life > 0:
                current_life = max(0, min(e.vida, max_life))
                health_ratio = current_life / max_life
                bar_full_width = 24
                bar_height = 5
                bar_x = x - (bar_full_width // 2)
                bar_y = y - 25
                dc.SetPen(wx.Pen('black', 1))
                dc.SetBrush(wx.Brush('grey'))
                dc.DrawRectangle(bar_x, bar_y, bar_full_width, bar_height)
                health_color = 'green'
                if health_ratio < 0.3:
                    health_color = 'red'
                elif health_ratio < 0.6:
                    health_color = 'yellow'
                dc.SetBrush(wx.Brush(health_color))
                dc.DrawRectangle(bar_x, bar_y, int(bar_full_width * health_ratio), bar_height)

        # Estado
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(wx.Colour(255, 255, 255))
        status_text = (
            f"Turno: {self.ecosistema.turno} | "
            f"Plantas: {plantas} | "
            f"Herbív.: {herbivoros} | "
            f"Carnív.: {carnivoros} | "
            f"Omnív.: {omnivoros}"
        )
        dc.DrawText(status_text, 5, 390)

    def on_sim_timer(self, event):
        self.ecosistema.simular_turno()

    def on_draw_timer(self, event):
        self.panel.Refresh()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.ventana.Close()

    def iniciar(self):
        self.app.MainLoop()

# -------------------- Main --------------------

if __name__ == "__main__":
    vista = VistaEcosistema()
    vista.iniciar()

