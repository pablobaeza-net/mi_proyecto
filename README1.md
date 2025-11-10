SIMULADOR DE ECOSISTEMA DINAMICO 
(PYTHON & WXPYTHON)
Este proyecto implementa un simulador de ecosistema que aplica los principios de la Programación Orientada a Objetos (POO)
para modelar las interacciones biológicas de diferentes especies. La simulación utiliza Python para la lógica y wxPython 
(incluida en el entorno de ejecución) para una representación gráfica simple y dinámica.

1. ESTRUCTURA Y PRINCIPIOS DE POO:
El proyecto está rigurosamente dividido en dos capas principales y organizadas en módulos, cumpliendo con los requisitos de la evaluación:
|-----------------------------------------------------------------------------------------------------|
|Capa       |     modulo    |    responsabilidad           |   principio POO clave                    |
|-----------------------------------------------------------------------------------------------------|
|Logica     |     logic.py  |    modelado de especies      |   Abstraccion, Herencia,                 |
|           |               |    (Especie, Planta,         |   Polimorfismo, Composicion.             | 
|           |               |    Hervivoro, Carnivoro      |                                          |
|           |               |    Omnivoro, Pez) y gestion  |                                          |
|           |               |    de iteacciones globales   |                                          |
|           |               |    (Ecosistema)              |                                          |
|           |               |                              |                                          |
|-----------------------------------------------------------------------------------------------------|
|Vista      |    view.py    |   Representacion visual del  |  Encapsulamiento, separacion             |
|           |               |   estado del ecosistema      |  separacion de preocupaciones            |
|           |               |   (VistaEcosistema), control |                                          |
|           |               |   de la interfaz grafica     |                                          |  
|           |               |                              |                                          |
|-----------------------------------------------------------------------------------------------------|

Modelado de Clases y Comportamientos:

  1.Clase Abstracta/Base (Especie): Define el estado base (vida, posicion, edad) y los comportamientos basicos
                                    y polimorfismos (mover(), envejecer(), reproducir()).

  2.Especies Modeladas(Herencia y Polimorfismo):
                                                2.1: Planta: Recurso base(no se mueve, se reproduce por despersion
                                                2.2: Herbivoro: se alimenta de las Plantas
                                                2.3: Carnivoro: se alimenta del Herbivoro(caza)
                                                2.4: Omnivoro: implementa un metodo de alimentacion mas complejo, consumiendo
                                                     tanto Planta como Herbivoro (polimorfismo de alimentacion)
                                                2.5: Pez: Especie especializada confunada al area del lago

  3.Composicion(Ecosistema): La clase Ecosistema utiliza Composición al contener y gestionar una lista de objetos Especie (self.entidades).


Comportamientos Implementados:

|-----------------------------|-------------------------------|
|Comportamiento               | Logica de Simulacion          |
|-----------------------------|-------------------------------|
| Movimiento                  |Implementado en Especie.mover()|
|                             |, con logica de rebote en los  |
|                             |limites del mapa sobreescrito  |
|                             |en Pez para confinarse al ovalo|
|                             |del lago                       |                                        
|-----------------------------|-------------------------------|
| alimentacion                |Implementado polimórficamente: | 
|                             | Herbivoro.comer(),            | 
|                             | Carnivoro.cazar(),            |
|                             | Omnivoro.alimentarse().       |
|                             | La alimentación exitosa       |
|                             | regenera vida y elimina el    |
|                             | recurso/presa.                |
|-----------------------------|-------------------------------|
|Reproducción                 |Se basa en la proximidad y un  |
|                             |costo de vida. Las poblaciones |
|                             |están controladas por límites  |
|                             |estrictos (MAX_HERBIVOROS,     |
|                             |MAX_CARNIVOROS, Pez: 2-10)     |
|                             |para evitar la extinción o     |
|                             |sobrepoblación.                |
|                             |                               |
|-----------------------------|-------------------------------|
|Ciclo de Vida                |Especie.envejecer()            |
|                             |decrementa vida por            |
|                             |cada turno.                    | 
|                             |La entidad muere si la vida es |
|                             |$0$ o si su edad supera el     |
|                             |límite máximo.                 |
|                             |                               |
|                             |                               |
|-----------------------------|-------------------------------|

2. Colaboración y Control de Versiones:
El desarrollo del proyecto se realizó mediante un flujo de trabajo basado en ramas en Git
y GitHub, con la participación de tres integrantes del equipo:

|----------------------------------------------------------|------------------------------------------|
|Rol        |    Integrante |    Contribucion Principal    |   Commits asociados                      |
|-----------|---------------|------------------------------|------------------------------------------|
|Líder de   | Pablo Baeza V.|Estructura de base de datos   |#6,#7.#9 (refinamiento final)             |
|Proyecto   |               |del ecosistema,               |                                          |
|/ Backend  |               |implementacion de reproduccion|                                          |
|Core       |               |balanceo de poblacion final y |                                          |
|           |               |refinamiento de la simulacion.|                                          | 
|-----------|---------------|------------------------------|------------------------------------------|
|Modelado de| Pablo Baeza V.|implementacion de clases      |#3,#4,#5                                  |
|Terrestres |               |Herbivoro, Carnivoro, omnivoro|                                          |
|           |               |y su logica de alimentacion   |                                          |
|           |               |implementacion inicial de     |                                          |  
|           |               |plantas y fondo.              |                                          |
|-----------|---------------|------------------------------|------------------------------------------|
|Diseño de  |Pablo Baeza V. |Implementacion del Objeto lago|#8, #9 (Pez/Lago)                         |
|Entorno/   |               |, logica de movimiento, dentro|                                          |
|Acuatico   |               |de la elipse, y el desarrollo |                                          |
|           |               |completo de la clase Pez y su |                                          |
|           |               |control de poblacion.         |                                          |
|-----------|---------------|------------------------------|------------------------------------------|

  Historial de Commits Detallado:
    A continuación, se presenta un resumen del historial de commits que refleja el desarrollo iterativo del proyecto:
      Commit nº9 (07-11-2025): al fin hay peces 😁
      Contribución: Pablo Baeza
      Detalle: Integración de la clase Pez con movimiento restringido al lago. Implementación de límites de población y ajustes de balanceo
      para asegurar la sostenibilidad del ecosistema.
      
      Commit nº8 (02-11-2025): agüita
      Contribución: Pablo Baeza
      Detalle: Implementación del área del lago (óvalo) como un componente del entorno que afecta el movimiento de las especies terrestres.


      Commit nº7 (01-11-2025): rawr
      Contribución: Pablo Baeza
      Detalle: Implementación funcional de la reproducción de Planta y ajustes en la estética de las entidades.

      Commit nº6 (30-10-2025): Update dinos.py
      Contribución: Pablo Baeaza.
      Detalle: Mejora en la fluidez (FPS) de la vista y la introducción de la lógica base de reproducción en las especies animales.

      Commit nº5 (30-10-2025): Update dinos.py
      Contribución: Pablo Baeza.
      Detalle: Refinamiento del comportamiento del Omnivoro para cazar Herbivoro.

      Commit nº4 (30-10-2025): Update dinos.py
      Contribución: Pablo Baeza.
      Detalle: Introducción de la clase Omnivoro.

      Commit nº3 (29-10-2025): Update dinos.py
      Contribución: Pablo Baeza
      Detalle: Implementación del fondo y la clase Planta (aún sin funcionalidad de alimentación completa).

3. Instrucciones de Ejecución:
  Prerrequisitos:
    Este simulador requiere la librería wxPython.
    # Instalación de wxPython (si no está disponible)
    pip install wxPython


  Ejecución:
    Asegúrese de que los archivos logic.py y view.py estén en la misma carpeta.
    Ejecute el módulo de la vista:
    python view.py


    El simulador se iniciará automáticamente en una ventana gráfica.



