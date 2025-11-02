import random
import math
import wx
# --- Configuración del lago ovalado ---
LAKE_X_START = 140
LAKE_X_END = 340
LAKE_Y_START = 90
LAKE_Y_END = 290
MAX_TURNS = 600

def is_in_lake(x, y):
    cx = (LAKE_X_START + LAKE_X_END) / 2
    cy = (LAKE_Y_START + LAKE_Y_END) / 2
    rx = (LAKE_X_END - LAKE_X_START) / 2
    ry = (LAKE_Y_END - LAKE_Y_START) / 2
    return ((x - cx)**2 / rx**2 + (y - cy)**2 / ry**2) <= 1

# --- Clases de entidades ---
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
        tentative_x = self.posicion_x + dx
        tentative_y = self.posicion_y + dy

        if is_in_lake(tentative_x, tentative_y):
            self.direccion += math.pi + random.uniform(-0.1, 0.1)
        else:
            self.posicion_x = max(0, min(480, tentative_x))
            self.posicion_y = max(0, min(380, tentative_y))
            if self.posicion_x <= 0 or self.posicion_x >= 480:
                self.direccion = math.pi - self.direccion
            if self.posicion_y <= 0 or self.posicion_y >= 380:
                self.direccion = -self.direccion

    def envejecer(self):
        self.edad += 1
        self.vida -= 0.25
        if self.cooldown_comer > 0:
            self.cooldown_comer -= 1
        if self.cooldown_repro > 0:
            self.cooldown_repro -= 1
        if self.edad > 300000 or self.vida <= 0:
            self.viva = False

    def reproducir(self, otros=None):
        return None

class Planta(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=999)
        self.salto = 0

    def mover(self): pass
    def envejecer(self): self.vida = 999

    def reproducir(self, plantas=None):
        if plantas is not None and len(plantas) >= 39:
            return None
        if random.random() < 0.20:
            attempt_x = self.posicion_x + random.uniform(-25, 25)
            attempt_y = self.posicion_y + random.uniform(-25, 25)
            attempt_x = max(0, min(480, attempt_x))
            attempt_y = max(0, min(380, attempt_y))
            if not is_in_lake(attempt_x, attempt_y):
                return Planta(attempt_x, attempt_y)
        return None

class Herbivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=900)

    def comer(self, plantas):
        if self.cooldown_comer > 0: return
        for planta in plantas:
            if planta.viva and ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5 < 20:
                self.vida = min(self.vida + 12, 1050)
                planta.viva = False
                self.cooldown_comer = 4
                return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = otro.ya_reprodujo = True
                    self.cooldown_repro = otro.cooldown_repro = 30
                    if not is_in_lake(self.posicion_x, self.posicion_y):
                        return Herbivoro(self.posicion_x, self.posicion_y)
        return None

class Carnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=950)

    def cazar(self, presas):
        if self.cooldown_comer > 0: return
        for presa in presas:
            if presa.viva and ((self.posicion_x - presa.posicion_x)**2 + (self.posicion_y - presa.posicion_y)**2)**0.5 < 18:
                self.vida = min(self.vida + 14, 1150)
                presa.viva = False
                self.cooldown_comer = 6
                return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = otro.ya_reprodujo = True
                    self.cooldown_repro = otro.cooldown_repro = 40
                    if not is_in_lake(self.posicion_x, self.posicion_y):
                        return Carnivoro(self.posicion_x, self.posicion_y)
        return None

class Omnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=920)

    def alimentarse(self, plantas, herbivoros):
        if self.cooldown_comer > 0: return
        for planta in plantas:
            if planta.viva and ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5 < 20:
                self.vida = min(self.vida + 10, 1100)
                planta.viva = False
                self.cooldown_comer = 4
                return
        for herbivoro in herbivoros:
            if herbivoro.viva and ((self.posicion_x - herbivoro.posicion_x)**2 + (self.posicion_y - herbivoro.posicion_y)**2)**0.5 < 18:
                self.vida = min(self.vida + 11, 1100)
                herbivoro.viva = False
                self.cooldown_comer = 6
                return

    def reproducir(self, otros, plantas):
        if len(otros) + len(plantas) <= len(plantas):
            for otro in otros:
                if self.puede_reproducirse_con(otro):
                    self.ya_reprodujo = otro.ya_reprodujo = True
                    self.cooldown_repro = otro.cooldown_repro = 35
                    if not is_in_lake(self.posicion_x, self.posicion_y):
                        return Omnivoro(self.posicion_x, self.posicion_y)
        return None

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
                e.envejecer()
                nuevo = None
                if isinstance(e, Planta):
            
                    nuevo = e.reproducir(plantas)
                elif isinstance(e, Herbivoro):
                    e.comer(plantas)
                    nuevo = e.reproducir(herbivoros, plantas)
                elif isinstance(e, Carnivoro):
                    e.cazar(herbivoros)
                    nuevo = e.reproducir(carnivoros, plantas)
                elif isinstance(e, Omnivoro):
                    e.alimentarse(plantas, herbivoros)
                    nuevo = e.reproducir(omnivoros, plantas)

                if nuevo:
                    nuevas_entidades.append(nuevo)

        self.entidades = [e for e in self.entidades if e.viva] + nuevas_entidades

class VistaEcosistema:
    def __init__(self):
        self.app = wx.App()
        self.ventana = wx.Frame(None, title="Ecosistema Virtual (Con Lago Ovalado)", size=(500, 420))
        self.panel = wx.Panel(self.ventana, style=wx.WANTS_CHARS)
        self.panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.panel.SetFocus()

        self.ecosistema = Ecosistema()
        self.inicializar_entidades()

        self.sim_timer = wx.Timer(self.panel)
        self.panel.Bind(wx.EVT_TIMER, self.on_sim_timer, self.sim_timer)
        self.sim_timer.Start(50)

        self.draw_timer = wx.Timer(self.panel)
        self.panel.Bind(wx.EVT_TIMER, self.on_draw_timer, self.draw_timer)
        self.draw_timer.Start(16)

        self.ventana.Centre()
        self.ventana.Show()

    def _get_valid_position(self):
        while True:
            x = random.randint(50, 450)
            y = random.randint(50, 350)
            if not is_in_lake(x, y):
                return x, y

    def inicializar_entidades(self):
        for _ in range(100): 
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Planta(x, y))
        for _ in range(30): 
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Herbivoro(x, y))
        for _ in range(10): 
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Carnivoro(x, y))
        for _ in range(15): 
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Omnivoro(x, y))
    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBackground(wx.Brush(wx.Colour(34, 139, 34)))  # forest green
        dc.Clear()

        # Lago ovalado
        dc.SetBrush(wx.Brush(wx.Colour(135, 206, 250)))     # celeste
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 255), 1))          # azul
        dc.DrawEllipse(LAKE_X_START, LAKE_Y_START, LAKE_X_END - LAKE_X_START, LAKE_Y_END - LAKE_Y_START)

        plantas = herbivoros = carnivoros = omnivoros = 0

        for e in self.ecosistema.entidades:
            x = int(e.posicion_x)
            y = int(e.posicion_y)
            max_life = 0

            if isinstance(e, Planta):
                plantas += 1
                dc.SetPen(wx.Pen(wx.Colour(0, 128, 0), 2))           # green
                dc.DrawLine(x, y+5, x, y-5)
                dc.SetBrush(wx.Brush(wx.Colour(255, 255, 0)))        # yellow
                dc.DrawCircle(x, y-5, 4)
                dc.SetBrush(wx.Brush(wx.Colour(0, 128, 0)))          # green
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
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 3))              # black
                dc.SetBrush(wx.Brush(wx.Colour(220, 0, 0)))           # red
                dc.DrawRectangle(x-15, y-7, 30, 14)
                dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 1))            # red
                dc.DrawLine(x-9, y+2, x-12, y+6)
                dc.DrawLine(x+9, y+2, x+12, y+6)
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 3))              # black
                dc.DrawLine(x-4, y+7, x-4, y+18)
                dc.DrawLine(x+4, y+7, x+4, y+18)

            elif isinstance(e, Omnivoro):
                omnivoros += 1
                max_life = 1100
                dc.SetPen(wx.Pen(wx.Colour(120, 0, 120), 3))          # purple
                dc.SetBrush(wx.Brush(wx.Colour(180, 0, 220)))         # violet
                dc.DrawEllipse(x-12, y-7, 24, 14)
                dc.SetBrush(wx.Brush(wx.Colour(255, 165, 0)))         # orange
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
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))              # black
                dc.SetBrush(wx.Brush(wx.Colour(128, 128, 128)))       # grey
                dc.DrawRectangle(bar_x, bar_y, bar_full_width, bar_height)
                health_color = wx.Colour(0, 255, 0)                   # green
                if health_ratio < 0.3:
                    health_color = wx.Colour(255, 0, 0)               # red
                elif health_ratio < 0.6:
                    health_color = wx.Colour(255, 255, 0)             # yellow
                dc.SetBrush(wx.Brush(health_color))
                dc.DrawRectangle(bar_x, bar_y, int(bar_full_width * health_ratio), bar_height)

        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(wx.Colour(255, 255, 255))                # white
        status_text = (
            f"Turno: {self.ecosistema.turno} / {MAX_TURNS} | "
            f"Plantas: {plantas} | "
            f"Herbív.: {herbivoros} | "
            f"Carnív.: {carnivoros} | "
            f"Omnív.: {omnivoros}"
        )
        dc.DrawText(status_text, 5, 390)
    def on_sim_timer(self, event):
        self.ecosistema.simular_turno()
        if self.ecosistema.turno >= MAX_TURNS:
            self.sim_timer.Stop()
            print(f"Simulación detenida después de {MAX_TURNS} turnos.")

    def on_draw_timer(self, event):
        self.panel.Refresh()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.ventana.Close()

    def iniciar(self):
        self.app.MainLoop()
if __name__ == "__main__":
    vista = VistaEcosistema()
    vista.iniciar()
