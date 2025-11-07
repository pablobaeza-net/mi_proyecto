import random
import math
import wx

# --- Configuración del lago ovalado ---
LAKE_X_START = 140
LAKE_X_END = 340
LAKE_Y_START = 90
LAKE_Y_END = 290
MAX_TURNS = 9000

# --- NUEVOS LÍMITES DE POBLACIÓN ---
MAX_HERBIVOROS = 40  # Límite estricto para Herbívoros (Objetivo del usuario)
MAX_CARNIVOROS = 15  # Límite para evitar el colapso por depredadores

def is_in_lake(x, y):
    """Verifica si las coordenadas están dentro del área del lago ovalado."""
    cx = (LAKE_X_START + LAKE_X_END) / 2
    cy = (LAKE_Y_START + LAKE_Y_END) / 2
    rx = (LAKE_X_END - LAKE_X_START) / 2
    ry = (LAKE_Y_END - LAKE_Y_START) / 2
    return ((x - cx)**2 / rx**2 + (y - cy)**2 / ry**2) <= 1

def get_random_lake_position():
    """Genera una posición aleatoria garantizada dentro del lago."""
    cx = (LAKE_X_START + LAKE_X_END) / 2
    cy = (LAKE_Y_START + LAKE_Y_END) / 2
    rx = (LAKE_X_END - LAKE_X_START) / 2
    ry = (LAKE_Y_END - LAKE_Y_START) / 2
    
    while True:
        x = random.uniform(LAKE_X_START, LAKE_X_END)
        y = random.uniform(LAKE_Y_START, LAKE_Y_END)
        if is_in_lake(x, y):
            return x, y

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
        """Verifica si dos entidades pueden reproducirse."""
        return (
            type(self) == type(otra)
            and self.viva and otra.viva
            and not self.ya_reprodujo and not otra.ya_reprodujo
            and self != otra
            and self.cooldown_repro == 0 and otra.cooldown_repro == 0
            and ((self.posicion_x - otra.posicion_x)**2 + (self.posicion_y - otra.posicion_y)**2)**0.5 < 28 
        )

    def mover(self):
        """Mueve la especie y la hace rebotar en límites."""
        self.direccion += random.uniform(-0.06, 0.06)
        dx = math.cos(self.direccion) * self.salto
        dy = math.sin(self.direccion) * self.salto
        tentative_x = self.posicion_x + dx
        tentative_y = self.posicion_y + dy

        # Rebotar si el movimiento tentativo choca contra el lago (desde fuera), excepto los peces
        if is_in_lake(tentative_x, tentative_y) and not isinstance(self, Pez):
            self.direccion += math.pi + random.uniform(-0.1, 0.1) 
        else:
            self.posicion_x = max(0, min(480, tentative_x))
            self.posicion_y = max(0, min(380, tentative_y))
            
            if self.posicion_x <= 0 or self.posicion_x >= 480:
                self.direccion = math.pi - self.direccion
            if self.posicion_y <= 0 or self.posicion_y >= 380:
                self.direccion = -self.direccion

    def envejecer(self):
        """Aumenta la edad y disminuye lentamente la vida."""
        self.edad += 1
        self.vida -= 0.15
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
        if plantas is not None and len(plantas) >= 10000: # Límite para evitar sobrecarga
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
        # VIDA INICIAL AUMENTADA (de 1000 a 1200) para resistir mejor
        super().__init__(x, y, vida=1200) 

    def comer(self, plantas):
        if self.cooldown_comer > 0: return
        for planta in plantas:
            distancia= ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5
            if planta.viva and distancia < 30:
                # VIDA GANADA AUMENTADA (de 12 a 20) para combatir el hambre
                self.vida = min(self.vida + 20, 10000) 
                planta.viva = False
                self.cooldown_comer = 4
                return

    def reproducir(self, otros, plantas):
        # AUMENTO DEL COSTE Y COOLDOWN PARA CONTROLAR LA POBLACIÓN
        REPRO_COST = 500  # Aumentado de 400
        REPRO_COOLDOWN = 25 # Aumentado de 20
        
        if self.cooldown_repro > 0 or self.ya_reprodujo:
            return None

        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.vida -= REPRO_COST
                otro.vida -= REPRO_COST
                if self.vida <= 0: self.viva = False
                if otro.vida <= 0: otro.viva = False
                if not self.viva or not otro.viva:
                    return None
                
                if random.random() < 0.25:  
                    self.ya_reprodujo = otro.ya_reprodujo = True
                self.cooldown_repro = otro.cooldown_repro = REPRO_COOLDOWN

                for _ in range(5): 
                    offset_x = random.uniform(-20, 20)
                    offset_y = random.uniform(-20, 20)
            
                    nuevo_x = max(0, min(480, self.posicion_x + offset_x))
                    nuevo_y = max(0, min(380, self.posicion_y + offset_y))
                    if not is_in_lake(nuevo_x, nuevo_y):
                        return Herbivoro(nuevo_x, nuevo_y)
           
                break 
        return None

class Carnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=950)

    def cazar(self, presas):
        if self.cooldown_comer > 0: 
            return
        for presa in presas:
            distancia = ((self.posicion_x - presa.posicion_x)**2 + (self.posicion_y - presa.posicion_y)**2)**0.5 
          
            if presa.viva and distancia < 18:
                if random.random () < 0.7:
                    # VIDA GANADA REDUCIDA (de 14 a 10)
                    self.vida = min(self.vida + 10, 1150)
                    presa.viva = False
                    # COOLDOWN AUMENTADO (de 12 a 15) para espaciar ataques
                    self.cooldown_comer = 15 
    
                    return

    def reproducir(self, otros, plantas):
        # AUMENTO DEL COSTE Y COOLDOWN PARA CONTROLAR LA POBLACIÓN
        REPRO_COST = 400  # Aumentado de 300
        REPRO_COOLDOWN = 40 # Aumentado de 30
        
        if self.cooldown_repro > 0 or self.ya_reprodujo:
            return None

        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.vida -= REPRO_COST
                otro.vida -= REPRO_COST
                if self.vida <= 0: self.viva = False
                if otro.vida <= 0: otro.viva = False
                if not self.viva or not otro.viva:
                    return None

                if random.random() < 0.25:  
                    self.ya_reprodujo = otro.ya_reprodujo = True
                self.cooldown_repro = otro.cooldown_repro = REPRO_COOLDOWN

                for _ in range(5):  
                    offset_x = random.uniform(-20, 20)
                    offset_y = random.uniform(-20, 20) 
                    nuevo_x = max(0, min(480, self.posicion_x + offset_x))
                    nuevo_y = max(0, min(380, self.posicion_y + offset_y))
                    if not is_in_lake(nuevo_x, nuevo_y):
                        return Carnivoro(nuevo_x, nuevo_y)
                break
        return None


class Omnivoro(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=920)

    def alimentarse(self, plantas, herbivoros):
        if self.cooldown_comer > 0:
            return
        
        # 1. Intentar comer plantas
        for planta in plantas:
            if planta.viva and ((self.posicion_x - planta.posicion_x)**2 + (self.posicion_y - planta.posicion_y)**2)**0.5 < 20:
                self.vida = min(self.vida + 8, 1100)
                planta.viva = False
                self.cooldown_comer = 4
                return
        
        # 2. Intentar cazar herbívoros
        for herbivoro in herbivoros:
            if herbivoro.viva and ((self.posicion_x - herbivoro.posicion_x)**2 + (self.posicion_y - herbivoro.posicion_y)**2)**0.5 < 18:
                if random.random() < 0.6:
                    # VIDA GANADA REDUCIDA (de 10 a 8)
                    self.vida = min(self.vida + 8, 1100) 
                herbivoro.viva = False
                # COOLDOWN AUMENTADO (de 6 a 8) para espaciar ataques
                self.cooldown_comer = 8 
                return

    def reproducir(self, otros, plantas):
        # AUMENTO DEL COSTE Y COOLDOWN PARA CONTROLAR LA POBLACIÓN
        REPRO_COST = 350 # Aumentado de 250
        REPRO_COOLDOWN = 40 # Aumentado de 30
        
        if self.cooldown_repro > 0 or self.ya_reprodujo:
            return None

        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.vida -= REPRO_COST
                otro.vida -= REPRO_COST
                if self.vida <= 0: self.viva = False
                if otro.vida <= 0: otro.viva = False
                if not self.viva or not otro.viva:
                    return None
                
                if random.random() < 0.25:  
                    self.ya_reprodujo = otro.ya_reprodujo = True
                self.cooldown_repro = otro.cooldown_repro = REPRO_COOLDOWN

                for _ in range(5):  
                    offset_x = random.uniform(-20, 20)
                    offset_y = random.uniform(-20, 20) 
                    nuevo_x = max(0, min(480, self.posicion_x + offset_x))
                    nuevo_y = max(0, min(380, self.posicion_y + offset_y))
                    if not is_in_lake(nuevo_x, nuevo_y):
                        return Omnivoro(nuevo_x, nuevo_y)
                break
        return None

class Pez(Especie):
    def __init__(self, x, y):
        super().__init__(x, y, vida=1000)
        self.salto = 1.2

    def mover(self):
        """Mueve el pez asegurándose de que permanezca DENTRO del lago."""
        self.direccion += random.uniform(-0.15, 0.15)
        dx = math.cos(self.direccion) * self.salto
        dy = math.sin(self.direccion) * self.salto
        tentative_x = self.posicion_x + dx
        tentative_y = self.posicion_y + dy

        if is_in_lake(tentative_x, tentative_y):
            self.posicion_x = tentative_x
            self.posicion_y = tentative_y
        else:
            self.direccion += math.pi + random.uniform(-0.5, 0.5)
            self.posicion_x -= math.cos(self.direccion) * (self.salto * 0.1)
            self.posicion_y -= math.sin(self.direccion) * (self.salto * 0.1)
            
    def envejecer(self):
        """Envejecimiento más lento para peces."""
        self.edad += 1
        self.vida -= 0.05
        if self.cooldown_repro > 0:
            self.cooldown_repro -= 1
        if self.edad > 50000 or self.vida <= 0: 
            self.viva = False

    def reproducir(self, otros, poblacion_actual):
        """Permite la reproducción si la población actual es menor al límite máximo (10)."""
        if self.cooldown_repro > 0 or self.ya_reprodujo or poblacion_actual >= 10:
            return None

        for otro in otros:
            if self.puede_reproducirse_con(otro):
                self.vida -= 50 
                otro.vida -= 50
                if not self.viva or not otro.viva:
                    return None
                
                if poblacion_actual < 10 and random.random() < 0.35:  
                    self.ya_reprodujo = otro.ya_reprodujo = True
                    self.cooldown_repro = otro.cooldown_repro = 50 

                    offset_x = random.uniform(-10, 10)
                    offset_y = random.uniform(-10, 10)
                    
                    nuevo_x = self.posicion_x + offset_x
                    nuevo_y = self.posicion_y + offset_y
                    
                    if not is_in_lake(nuevo_x, nuevo_y):
                        nuevo_x, nuevo_y = get_random_lake_position() 
                        
                    return Pez(nuevo_x, nuevo_y)
                
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

        # Recolectar poblaciones actuales antes de la simulación
        plantas = [e for e in self.entidades if isinstance(e, Planta) and e.viva]
        herbivoros = [e for e in self.entidades if isinstance(e, Herbivoro) and e.viva]
        carnivoros = [e for e in self.entidades if isinstance(e, Carnivoro) and e.viva]
        omnivoros = [e for e in self.entidades if isinstance(e, Omnivoro) and e.viva]
        peces = [e for e in self.entidades if isinstance(e, Pez) and e.viva]

        # 1. Ejecutar acciones y generar nuevas crías
        for e in self.entidades: 
            if not e.viva:
                continue

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
            elif isinstance(e, Pez):
                nuevo = e.reproducir(peces, len(peces))

            if nuevo:
                nuevas_entidades.append(nuevo)

        # 2. Filtrar entidades muertas
        self.entidades = [e for e in self.entidades if e.viva]
        
        # 3. Aplicar límites de población a las nuevas crías ANTES de añadirlas
        current_herb_count = len([e for e in self.entidades if isinstance(e, Herbivoro)])
        current_omni_count = len([e for e in self.entidades if isinstance(e, Omnivoro)])
        current_carn_count = len([e for e in self.entidades if isinstance(e, Carnivoro)])
        current_fish_count = len([e for e in self.entidades if isinstance(e, Pez)])

        for nuevo in nuevas_entidades:
            if isinstance(nuevo, Herbivoro):
                if current_herb_count < MAX_HERBIVOROS:
                    self.entidades.append(nuevo)
                    current_herb_count += 1
            
            elif isinstance(nuevo, Omnivoro):
                # OMNIVOROS: No más que herbívoros Y menor que el límite global (40)
                if current_omni_count < current_herb_count and current_omni_count < MAX_HERBIVOROS:
                    self.entidades.append(nuevo)
                    current_omni_count += 1
            
            elif isinstance(nuevo, Carnivoro):
                if current_carn_count < MAX_CARNIVOROS:
                    self.entidades.append(nuevo)
                    current_carn_count += 1
                    
            elif isinstance(nuevo, Pez):
                # Peces: Límite 10
                if current_fish_count < 10:
                    self.entidades.append(nuevo)
                    current_fish_count += 1
                    
        # 4. Control Estricto de Población de Peces (2 <= Pez <= 10) (FINAL)
        pez_actual = [e for e in self.entidades if isinstance(e, Pez)]
        pez_count = len(pez_actual)

        # Mínimo (Añadir si es < 2)
        if pez_count < 2:
            for _ in range(2 - pez_count):
                x, y = get_random_lake_position()
                self.entidades.append(Pez(x, y))

        # Máximo (Eliminar si es > 10)
        pez_actual = [e for e in self.entidades if isinstance(e, Pez)]
        pez_count = len(pez_actual)
        
        if pez_count > 10:
            excess = pez_count - 10
            # Priorizar la eliminación de los peces más viejos y con menos vida
            pez_actual.sort(key=lambda f: (f.vida, f.edad)) 
            pez_to_remove = set(pez_actual[:excess])
            
            self.entidades = [e for e in self.entidades if not isinstance(e, Pez) or e not in pez_to_remove]


class VistaEcosistema:
    def __init__(self):
        self.app = wx.App()
        self.ventana = wx.Frame(None, title="Ecosistema Virtual Equilibrado", size=(500, 420))
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
        """Obtiene una posición válida FUERA del lago (para especies terrestres)."""
        while True:
            x = random.randint(50, 450)
            y = random.randint(50, 350)
            if not is_in_lake(x, y):
                return x, y
            
    def _get_lake_position(self):
        """Obtiene una posición válida DENTRO del lago (para peces)."""
        return get_random_lake_position()

    def inicializar_entidades(self):
        """Inicializa todas las entidades, con poblaciones iniciales más bajas para el equilibrio."""
        for _ in range(500): # Menos plantas
            x, y = self._get_valid_position() 
            self.ecosistema.agregar(Planta(x, y))
        for _ in range(9): # Empezar con 20 Herbívoros (para evitar el estancamiento)
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Herbivoro(x, y))
        for _ in range(4): # 4 Carnívoros
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Carnivoro(x, y)) 
        for _ in range(4): # 4 Omnívoros
            x, y = self._get_valid_position()
            self.ecosistema.agregar(Omnivoro(x, y))
            
        # 5 Peces DENTRO del lago
        for _ in range(5):
            x, y = self._get_lake_position()
            self.ecosistema.agregar(Pez(x, y))
            
    def on_paint(self, event):
        dc = wx.PaintDC(self.panel)
        dc.SetBackground(wx.Brush(wx.Colour(34, 139, 34)))  # forest green (Bosque)
        dc.Clear()

        # 1. Dibujar el Lago ovalado
        dc.SetBrush(wx.Brush(wx.Colour(135, 206, 250))) # Azul claro
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 255), 1))      # Borde azul
        dc.DrawEllipse(LAKE_X_START, LAKE_Y_START, LAKE_X_END - LAKE_X_START, LAKE_Y_END - LAKE_Y_START)

        plantas = herbivoros = carnivoros = omnivoros = peces = 0

        for e in self.ecosistema.entidades:
            x = int(e.posicion_x)
            y = int(e.posicion_y)
            max_life = 0

            if isinstance(e, Planta):
                plantas += 1
                dc.SetPen(wx.Pen(wx.Colour(0, 128, 0), 2))
                dc.DrawLine(x, y+5, x, y-5)
                dc.SetBrush(wx.Brush(wx.Colour(255, 255, 0))) 
                dc.DrawCircle(x, y-5, 4)
                dc.SetBrush(wx.Brush(wx.Colour(0, 128, 0))) 
                dc.DrawEllipse(x-6, y-2, 12, 6)
                continue

            elif isinstance(e, Pez):
                peces += 1
                max_life = 1000
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 128), 1))              
                dc.SetBrush(wx.Brush(wx.Colour(255, 105, 180)))         
                dc.DrawEllipse(x-10, y-5, 20, 10)
                dc.SetBrush(wx.Brush(wx.Colour(139, 0, 0)))            
                dc.DrawPolygon([(x+10, y), (x+18, y-5), (x+18, y+5)]) 
                dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0)))
                dc.DrawCircle(x-6, y, 1)


            elif isinstance(e, Herbivoro):
                herbivoros += 1
                max_life = 1250 # Cambiado a 1250 para reflejar el aumento de vida
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
                dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 1))           
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
                dc.SetBrush(wx.Brush(wx.Colour(255, 165, 0)))         
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
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))              
                dc.SetBrush(wx.Brush(wx.Colour(128, 128, 128)))       
                dc.DrawRectangle(bar_x, bar_y, bar_full_width, bar_height)
                health_color = wx.Colour(0, 255, 0)                  
                if health_ratio < 0.3:
                    health_color = wx.Colour(255, 0, 0)              
                elif health_ratio < 0.6:
                    health_color = wx.Colour(255, 255, 0)            
                dc.SetBrush(wx.Brush(health_color))
                dc.DrawRectangle(bar_x, bar_y, int(bar_full_width * health_ratio), bar_height)

        # Mostrar estado
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground(wx.Colour(255, 255, 255))      
        status_text = (
            f"Turno: {self.ecosistema.turno} / {MAX_TURNS} | " 
            f"Plantas: {plantas} | " 
            f"Herbív.: {herbivoros} (Max {MAX_HERBIVOROS}) | " # Mostrar límite
            f"Carnív.: {carnivoros} (Max {MAX_CARNIVOROS}) | " # Mostrar límite
            f"Omnív.: {omnivoros} (Max <= Herbív.) | " # Mostrar límite
            f"Peces: {peces} (2-10)"
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
