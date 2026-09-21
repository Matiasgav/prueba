"""El modelo integrado del ensayo de ajuste de cuñas (WTD), por partes.

POR QUE EXISTE ESTE MODULO

El trabajo crecio por capas -- la cuña, el hueco espectral, el palpador, la
lectura, el golpe -- y cada capa se corrigio varias veces. Leido de corrido
es dificil de sostener en la cabeza. Aca esta el mismo trabajo declarado
como UNA CADENA DE SEIS BLOQUES, cada uno con:

    * la PREGUNTA que contesta (una sola, y concreta),
    * sus ENTRADAS, que o vienen de afuera o las produjo un bloque anterior,
    * sus SALIDAS, con simbolo, valor, unidad y de donde sale el valor,
    * la ECUACION que gobierna el bloque,
    * las HIPOTESIS que asume, con su origen,
    * como se VERIFICA (ancla de pytest y/o ensayo de banco),
    * y QUE PASA SI FALLA: que parte del ensayo se cae.

La cadena es ejecutable y se valida sola: `verificar_cadena()` comprueba que
ningun bloque consume un simbolo que nadie produce, y que ningun bloque
queda sin verificacion. Los valores que se pueden recalcular se recalculan
desde `wtd.softprobe` y `wtd.backemf`, asi que el documento no puede quedar
desactualizado en silencio respecto del codigo.

LA CADENA EN UNA LINEA

    B1 la cuña se mueve  ->  B2 se mueve en DOS BANDAS distintas segun el
    ajuste  ->  B3 el palpador es un filtro que planta su corte en el medio
    ->  B4 la lectura integra esa energia y la convierte en un numero  ->
    B5 el golpe que la excita se mide a si mismo  ->  B6 los dos numeros
    deciden asentada o suelta.

DONDE ESTA EL RIESGO

El unico bloque abierto es B6 (el clasificador conjunto). El unico bloque
que puede tumbar todo lo demas es B2, y depende de un parametro estimado,
`k_hombro`, que nadie midio todavia. Todo lo demas esta cerrado y anclado.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .softprobe import (
    F0_SWEEP_FLEXURA, PEAK_SPLIT, PRELOAD_SWEEP, RESONANCE_LIFTOFF,
    ZETA_SWEEP, design,
)


# ---------------------------------------------------------------------------
# Vocabulario
# ---------------------------------------------------------------------------

#  De donde sale cada numero. Es la misma marca que usa el informe.
#   D  dato del usuario o de campo         (no se discute)
#   V  de catalogo / hoja de datos         (verificable en papel)
#   M  calculado por el modelo             (reproducible corriendo el codigo)
#   S  medido sobre la simulacion          (reproducible corriendo el estudio)
#   E  estimado                            <- el riesgo vive aca
#   X  elegido por diseño                  (es una decision, no un hallazgo)
ORIGENES = {"D", "V", "M", "S", "E", "X"}


@dataclass(frozen=True)
class Magnitud:
    """Un numero con nombre, unidad y procedencia."""

    simbolo: str
    nombre: str
    valor: float | str
    unidad: str
    origen: str
    nota: str = ""

    def __post_init__(self) -> None:
        if self.origen not in ORIGENES:
            raise ValueError(f"origen desconocido: {self.origen!r}")


@dataclass(frozen=True)
class Hipotesis:
    """Algo que el bloque da por cierto, y cuanto duele si no lo es."""

    texto: str
    origen: str
    si_es_falsa: str


@dataclass(frozen=True)
class Bloque:
    """Una parte del modelo: una pregunta, entradas, salidas y como se verifica."""

    id: str
    nombre: str
    pregunta: str
    entradas: tuple[str, ...]
    salidas: tuple[Magnitud, ...]
    ecuacion: str
    explicacion: str
    hipotesis: tuple[Hipotesis, ...] = ()
    anclas: tuple[str, ...] = ()          # tests de pytest
    banco: tuple[str, ...] = ()           # ensayos de banco (A-D)
    si_falla: str = ""
    abierto: bool = False                 # True = todavia no esta cerrado

    def simbolos(self) -> tuple[str, ...]:
        return tuple(s.simbolo for s in self.salidas)

    def valor(self, simbolo: str) -> float | str:
        for s in self.salidas:
            if s.simbolo == simbolo:
                return s.valor
        raise KeyError(f"{self.id} no produce {simbolo!r}")


# ---------------------------------------------------------------------------
# Lo que entra de afuera: no lo produce ningun bloque
# ---------------------------------------------------------------------------

EXTERNAS: tuple[Magnitud, ...] = (
    Magnitud("geom_cuña", "Cuña G11 50 x 30 x 8 mm, 22.8 g", "50x30x8", "mm", "D",
             "Dato del usuario."),
    Magnitud("apoyo", "Hombro de cola de milano + ripple precargado", "unilateral",
             "-", "D", "Dato de campo: el apoyo es DISTRIBUIDO, no en extremos."),
    Magnitud("k_hombro", "Rigidez de contacto del hombro", 2.0e10, "N/m/m", "E",
             "LA INCOGNITA N.1 DEL PROYECTO. Nadie la midio."),
    Magnitud("F_precarga", "Precarga disponible para apoyar el palpador", 1.0, "N",
             "D", "Restriccion dura del usuario: 1 N como maximo."),
    Magnitud("d_palpador", "Distancia del palpador al punto de golpe", 12.5, "mm",
             "D", "El usuario pide 10-15 mm."),
    Magnitud("LAH04", "Voice coil del modulo de impacto", "R 5.1 ohm, L 220 uH",
             "-", "V", "Hoja de datos."),
)

EXTERNAS_SIMBOLOS = tuple(m.simbolo for m in EXTERNAS)


# ---------------------------------------------------------------------------
# B1 -- LA CUÑA
# ---------------------------------------------------------------------------

_p = design()          # el palpador nominal, recalculado desde softprobe

B1 = Bloque(
    id="B1",
    nombre="La cuña y su apoyo",
    pregunta="Cuando el golpe entra, ¿como se mueve la cuña, y que cambia con el ajuste?",
    entradas=("geom_cuña", "apoyo", "k_hombro", "d_palpador"),
    salidas=(
        Magnitud("w(t)", "Movimiento de la cuña bajo el palpador", "serie", "m", "M",
                 "Viga de Timoshenko libre-libre, 20 modos, apoyos bilaterales "
                 "unilaterales, velocity-Verlet, dt = 50 ns."),
        Magnitud("escalera", "Estados de ajuste S0..S6", 7, "estados", "X",
                 "Varian precarga 1800 N -> 0, luz 0 -> 200 um y disipacion de "
                 "junta. La frontera asentada|suelta cae entre S3 (25 %) y S4 (5 %)."),
        Magnitud("x_pico", "Excursion de la cuña, S0 -> S6, a 5 mJ", "0.31 -> 6.90",
                 "um", "S", "Monotona con la soltura."),
        Magnitud("a_pico", "Aceleracion de la cuña, S0 -> S6, a 5 mJ", "830 -> 1062",
                 "g", "S", "NO monotona: pasa por 4808 g en S3, y 1545 g "
                 "corresponde tanto a S2 como a S4."),
        Magnitud("deriva", "Corrimiento permanente tras el golpe", 0.01, "um", "S",
                 "<0.2 % del pico: el ripple reasienta la cuña. No hay deriva."),
    ),
    ecuacion="M q'' + C q' + K q = f(t),  con contacto unilateral en el hombro:\n"
             "    F_hombro = k_hombro * max(0, penetracion)     (solo empuja)",
    explicacion=(
        "El golpe entra radialmente hacia adentro, o sea que DESASIENTA la cuña "
        "de los hombros. Lo que cambia entre una cuña ajustada y una suelta no es "
        "la cuña -- es su condicion de borde: con el ripple precargado los hombros "
        "estan cerrados y la cuña esta acoplada al nucleo en toda su longitud; sin "
        "precarga los hombros se abren y la cuña queda colgada del ripple.\n\n"
        "El resultado que ordena todo B2 sale de aca: la ESCALERA no es un cambio "
        "gradual de rigidez, es un cambio de condicion de borde. Y el resultado que "
        "mata la idea ingenua sale tambien de aca: el pico de ACELERACION de la cuña "
        "no es monotono con la soltura (4808 g en S3, 1062 g en S6), asi que un mismo "
        "numero corresponde a dos estados opuestos. El de DESPLAZAMIENTO si es "
        "monotono. Medir la aceleracion cruda de la cuña no sirve, y eso es "
        "independiente de cuanta precarga haya."
    ),
    hipotesis=(
        Hipotesis("El apoyo es distribuido a lo largo del hombro, no en los extremos.",
                  "D", "Cambia todas las frecuencias modales. La rev. A usaba "
                       "'ends' y de ahi salia el falso 6.1 kHz."),
        Hipotesis("k_hombro = 2e10 N/m por metro de contacto.", "E",
                  "Es la hipotesis mas cara del proyecto. Ver B2."),
        Hipotesis("La disipacion de junta crece al aflojarse (zeta 0.012 -> 0.055).",
                  "E", "De los cinco parametros estimados de la cuña es el unico "
                       "que mueve el resultado (barrido de la rev. B)."),
    ),
    anclas=("test_anclas.py :: la escalera de estados", "test_softprobe.py :: "
            "test_frecuencia_sube_con_el_apriete"),
    banco=("A",),
    si_falla="Si la cuña real no cambia de condicion de borde al aflojarse -- si "
             "el aflojamiento fuera gradual y no un cambio de apoyo -- no hay "
             "hueco espectral y el metodo entero se cae. Es lo que mide el "
             "ensayo A, y por eso el ensayo A va primero.",
)


# ---------------------------------------------------------------------------
# B2 -- EL HUECO ESPECTRAL  (el fundamento del metodo)
# ---------------------------------------------------------------------------

#  Sensibilidad a k_hombro: el diseño esta sentado en la rodilla de esta curva.
#  k_hombro relativo, 1er modo asentada [Hz], separacion asentada|suelta
K_HOMBRO_SENS = [
    (1 / 100, 3530, 0.08), (1 / 10, 10487, 0.34), (1 / 3.3, 18067, 8.3),
    (1.0, 32874, 150.2), (3.0, 55493, 176.0),
]

B2 = Bloque(
    id="B2",
    nombre="El hueco espectral",
    pregunta="¿En que se distingue, medible, una cuña asentada de una suelta?",
    entradas=("w(t)", "escalera", "k_hombro"),
    salidas=(
        Magnitud("f_asentada", "Pico espectral del desplazamiento, S0", 33350, "Hz",
                 "S", "El 90 % de la energia cae en 33 325 - 33 375 Hz."),
        Magnitud("f_suelta", "Techo de la banda del desplazamiento de S6", 175, "Hz", "S",
                 "S6 NO tiene pico espectral: no oscila. Hace una sola excursion "
                 "de 6.9 um que cruza su media dos veces en 5 ms. Su espectro es "
                 "el de UN TRANSITORIO, no el de un modo."),
        Magnitud("hueco", "Decadas vacias entre las dos bandas", 2.3, "-", "S",
                 "No se cita un 'factor entre picos': S6 no tiene pico, asi que "
                 "ese cociente dependia de la ventana. Lo robusto es el reparto."),
        Magnitud("banda_baja_S0", "Energia de S0 por debajo de 1273 Hz", 0.0, "%", "S"),
        Magnitud("banda_baja_S6", "Energia de S6 por debajo de 1273 Hz", 100.0, "%", "S"),
    ),
    ecuacion="hombro CERRADO -> modos 32.9 / 33.4 / 33.6 / 40.0 kHz\n"
             "hombro ABIERTO -> 1.28 / 1.29 kHz (cuerpo rigido sobre el ripple)\n"
             "                  y recien despues 10.6 / 24.9 kHz de flexion",
    explicacion=(
        "LA FRECUENCIA SUBE CON EL APRIETE, y sube muchisimo. Una version anterior "
        "de este trabajo afirmaba lo contrario, apoyada en un 6.1 kHz que venia del "
        "modelo de apoyo viejo; estaba mal.\n\n"
        "El mecanismo es simple una vez visto: la cuña asentada esta pegada al "
        "nucleo, que es una masa practicamente infinita, asi que responde con sus "
        "modos de flexion contra un apoyo rigidisimo -- 33 kHz. La cuña suelta "
        "queda montada sobre el ripple, que es blando, y responde con sus dos modos "
        "de CUERPO RIGIDO sobre ese resorte -- decenas de Hz. No son el mismo modo "
        "corrido: son familias de modos distintas.\n\n"
        "Y el reparto de energia es total, no parcial: contra un corte a 1273 Hz, "
        "la asentada pone el 0.0 % de su energia por debajo y la suelta el 100.0 %. "
        "El filtro no las atenua distinto -- las separa enteras. ESTE es el "
        "fundamento del metodo; todo B3 y B4 son consecuencia.\n\n"
        "Ojo con dos trampas ya pisadas: (1) el espectro que importa es el del "
        "DESPLAZAMIENTO, porque es lo que excita al palpador; el de la aceleracion "
        "pesa las altas por omega^4 y da otra cosa. (2) La ventana tiene que ser "
        "larga: con 8 ms el bin vale 125 Hz y el pico de la cuña suelta 'aparece' "
        "en 125 Hz por puro artefacto. Con 40 ms (25 Hz) el numero correcto es 50 Hz."
    ),
    hipotesis=(
        Hipotesis("k_hombro = 2e10 N/m/m, heredada de B1.", "E",
                  "AQUI ES DONDE DUELE. Con el hombro 10 veces mas blando el "
                  "primer modo asentado baja a 10.5 kHz, entra en la banda del "
                  "palpador y la separacion se INVIERTE (x0.34). Ningun diseño "
                  "de palpador sobrevive a eso: no es un problema de palpador, "
                  "es que el hueco deja de existir."),
        Hipotesis("La cuña suelta hace UNA excursion; el ripple la reasienta y "
                  "no queda sonando sobre el.", "E",
                  "El sistema linealizado con el hombro abierto tiene dos modos "
                  "de cuerpo rigido en 1.28 y 1.29 kHz, y la simulacion no "
                  "lineal no los excita de forma sostenida. Si en el fierro si "
                  "sonaran, caerian encima de la f0 del palpador (ver B3) y el "
                  "palpador despegaria."),
    ),
    anclas=("test_softprobe.py :: test_el_filtro_separa_las_dos_bandas_enteras",
            "test_softprobe.py :: test_frecuencia_sube_con_el_apriete"),
    banco=("A",),
    si_falla="Es el bloque critico. Si el hueco no existe en el banco, ningun "
             "palpador lo arregla y hay que cambiar de metodo. Por eso el ensayo "
             "A no necesita palpador: se hace con un acelerometro de choque "
             "pegado a la cuña y puede invalidar el enfoque en un dia.",
)


# ---------------------------------------------------------------------------
# B3 -- EL PALPADOR COMO FILTRO
# ---------------------------------------------------------------------------

B3 = Bloque(
    id="B3",
    nombre="El palpador: un pasa-bajos plantado en el hueco",
    pregunta="¿Como se mide eso con 1 N de precarga y a 12.5 mm del golpe?",
    entradas=("f_asentada", "f_suelta", "hueco", "F_precarga", "d_palpador"),
    salidas=(
        Magnitud("m_movil", "Masa movil (carro + acelerometro)", _p.mass * 1e3, "g", "X",
                 "Sale naturalmente en 0.33 g: hay que LASTRARLA con 0.35 g."),
        Magnitud("k_medicion", "Rigidez del acople blando (flexura)",
                 _p.k_series() / 1e3, "N/mm", "M", "En serie con Hertz."),
        Magnitud("f0", "Corte del filtro", _p.f0(), "Hz", "M",
                 "Optimo con zeta real; la banda util (>x100) va de 700 a 1700 Hz."),
        Magnitud("zeta", "Amortiguamiento del acople", 0.02, "-", "X",
                 "Tiene PISO y TECHO. Ver explicacion."),
        Magnitud("a_despegue", "Fondo de escala util", _p.a_liftoff() / 9.80665, "g", "M",
                 "= F/m, y NO depende del resorte. Es el invariante del diseño."),
        Magnitud("m_punta", "Techo de masa del lado punta", 20.0, "mg", "M",
                 "= F / a_cuña_max. Es una cota de SIMULTANEIDAD y por eso es "
                 "conservadora: en la simulacion el despegue llega a 120 mg."),
        Magnitud("k_precarga", "Rigidez del resorte de precarga", 0.30, "N/mm", "X",
                 "La fija el POSICIONAMIENTO (rango de 3 mm), no la medicion."),
    ),
    ecuacion="m x'' + c (x' - w') + k (x - w) = 0            (en contacto)\n"
             "F_contacto = F_precarga - k(x-w) - c(x'-w') + m_punta * w''\n"
             "despegue  <=>  F_contacto <= 0  <=>  a_leida = F / m",
    explicacion=(
        "La topologia es la unica que funciona, y es la que la pregunta del usuario "
        "corrigio: el resorte va ENTRE LA PUNTA Y LA MASA, no entre la masa y el "
        "cuerpo.\n\n"
        "    cuña -- punta --[ resorte k ]-- carro --[ precarga F ]-- cuerpo\n\n"
        "La compliancia tiene que estar EN EL CAMINO DE CARGA, entre lo que toca y "
        "lo que mide. Con un vastago rigido punta->carro y la flexura carro->cuerpo "
        "se obtiene el palpador RIGIDO con pasos de mas: el carro sigue a la cuña y "
        "el acelerometro lee los miles de g.\n\n"
        "TRES RESULTADOS QUE ORDENAN EL DISEÑO:\n\n"
        "1. El fondo de escala de CUALQUIER palpador apoyado vale F/m, y no depende "
        "   del resorte. Ablandar el acople no cuesta rango: cambia QUE PARTE del "
        "   movimiento de la cuña cae adentro de ese fondo de escala. Con acople "
        "   rigido se gasta en los picos de alta frecuencia, que no llevan "
        "   informacion; con acople blando se gasta en el desplazamiento, que si.\n"
        "   El limite es de UN SOLO LADO: acota la semionda que DESCARGA el "
        "   contacto. Por eso el margen se calcula contra el pico de descarga "
        "   (73.5 g) y no contra el de compresion (85.9 g), que es el que "
        "   dimensiona el acelerometro.\n\n"
        "2. f0 elige la CALIDAD y la masa elige si SOBREVIVIS, y son independientes: "
        "   la separacion y el pico leido resultaron funcion de f0 (y zeta) sola. "
        "   Por eso el diseño se hace en dos pasos, no resolviendo un compromiso.\n\n"
        "3. zeta es el parametro mas sensible de todo el trabajo, y tiene piso Y "
        "   techo. Techo: con elastomero (zeta ~ 0.15) el rechazo de alta "
        "   frecuencia cae de 1/r^2 a 1/r y la separacion se desploma de x150 a x3. "
        "   Piso: con zeta muy bajo, Q es alto y una excitacion SOSTENIDA a f0 "
        "   (maquina girando, motores del crawler, ring-down del tiro anterior) "
        "   despega el palpador con apenas 0.23 um. Lo que protege es el tiempo de "
        "   crecimiento -- llegar a Q pide ~Q ciclos y el impacto dura ~1.3 -- pero "
        "   el margen es de 16 ms. Por eso zeta = 0.02: cuesta x150 -> x112 de "
        "   separacion y compra 4x de inmunidad, ademas de bajar el ring-down de "
        "   115 a 29 ms, que es lo que fija el ritmo maximo de disparo."
    ),
    hipotesis=(
        Hipotesis("La cuña suelta no queda sonando a ~1.29 kHz sobre el ripple.",
                  "E",
                  "LO MAS FRAGIL DEL DISEÑO DESPUES DE k_hombro. f_ripple = "
                  "sqrt(k_ripple*L/m)/2pi = 1291 Hz, contra f0 = 1273 Hz: "
                  "coinciden dentro del 1.4 %, y son dos calculos "
                  "independientes. Con zeta = 0.02 una excitacion SOSTENIDA a "
                  "f0 despega el palpador con 0.92 um, y la excursion de la "
                  "cuña suelta es 6.9 um. Protege que la cuña no oscila: hace "
                  "una excursion y listo. Lo responde el ensayo A."),
        Hipotesis("La flexura metalica da zeta ~ 0.005-0.02.", "E",
                  "Con elastomero el ensayo es inservible. Es LA decision de "
                  "construccion, y se mide en un ping (ensayo B)."),
        Hipotesis("La resonancia parasita del lado punta (~7.4 kHz) no molesta.", "E",
                  "Cae entre las dos bandas de la cuña, asi que en principio no "
                  "interfiere, pero NO esta en el modelo: la punta se trata como "
                  "masa pura sin grado de libertad propio. Pendiente."),
        Hipotesis("El cuerpo del palpador pesa >= 7 g (10x la masa movil).", "X",
                  "Con 3x el efecto de masa reducida corre f0 un 15 %."),
    ),
    anclas=("test_softprobe.py :: test_fondo_de_escala_es_F_sobre_m_y_no_depende_del_resorte",
            "test_softprobe.py :: test_el_amortiguamiento_es_el_parametro_dominante",
            "test_softprobe.py :: test_el_amortiguamiento_tiene_piso_no_solo_techo",
            "test_softprobe.py :: test_la_masa_de_punta_no_cambia_la_lectura_pero_adelanta_el_despegue"),
    banco=("B", "C", "D"),
    si_falla="Si zeta construido supera 0.05 hay que rehacer la flexura (mas "
             "delgada, sin adhesivo en el camino de carga, sin elastomero). "
             "Si la punta pesa mas de ~30 mg el palpador despega en los golpes "
             "fuertes y se reconoce por el recorte plano en F/m.",
)


# ---------------------------------------------------------------------------
# B4 -- LA LECTURA
# ---------------------------------------------------------------------------

B4 = Bloque(
    id="B4",
    nombre="La lectura: de la señal a un numero",
    pregunta="¿Que numero se saca del registro, y cuanto separa?",
    entradas=("f0", "zeta", "a_despegue", "m_movil"),
    salidas=(
        Magnitud("rasgo", "Rasgo de decision", "int a^2 dt", "g^2 ms", "X",
                 "Energia de la señal, banda-limitada a 5 kHz, ventana de 3 ms."),
        Magnitud("separacion", "Separacion asentada | suelta", 112.2, "-", "S",
                 "Con zeta = 0.02. Con zeta = 0.005 seria x150."),
        Magnitud("ventaja_rasgo", "int a^2 dt contra el pico", "14 a 58", "x", "S",
                 "El rango 'x3 a x9' salia con zeta = 0.08. Con el diseño "
                 "vigente (zeta = 0.02) el rasgo separa x112 a x579 y el pico "
                 "x3.2 a x19.2."),
        Magnitud("despegue_detect", "Deteccion de despegue", "riel plano en -F/m",
                 "-", "S", "0 muestras en contacto limpio, 110 (3.67 %) al despegar."),
        Magnitud("a_leida", "Rango de lectura sobre 126 casos", "0.9 a 109", "g", "S",
                 "Cero despegues en los 126 casos."),
        Magnitud("acelerometro", "Sensor", "ADXL1005 +-100 g", "-", "X",
                 "0.1 g de masa, 44 dB de SNR en el peor caso."),
    ),
    ecuacion="rasgo = integral de a(t)^2 dt sobre 3 ms, SIN filtrar\n\n"
             "(los 5 kHz son una especificacion de la cadena de adquisicion y\n"
             " entran en el presupuesto de ruido, pero NO se aplicaron al\n"
             " calculo: aplicarlos mejora la separacion x1.9 a x8)",
    explicacion=(
        "Lo que el palpador mide NO es desplazamiento ni velocidad limpios. Por "
        "regresion sobre los 126 casos simulados, omega^2 x da R^2 = 0.92 con 40 % "
        "de error mediano y omega v da R^2 = 0.84 con 26 %. La cuña no lo excita "
        "con un impulso sino con una rafaga, asi que la lectura es un valor de "
        "ESPECTRO DE RESPUESTA AL CHOQUE a f0. Hay que calibrarla; no se invierte "
        "con formula cerrada. Eso no es un problema para este ensayo, que clasifica "
        "y no mide una magnitud fisica.\n\n"
        "La energia de la señal le gana al pico por 3 a 9 veces porque promedia "
        "sobre toda la rafaga en vez de quedarse con un instante -- y el instante "
        "del pico esta dominado por el transitorio rapido del impacto, que es "
        "justamente la parte que NO sigue al estado de ajuste.\n\n"
        "LA DETECCION DE DESPEGUE SALE GRATIS Y ES BINARIA. En vuelo la unica "
        "fuerza sobre el carro es la precarga, asi que la lectura se clava "
        "EXACTAMENTE en -F/m. Se cuentan las muestras con |a + F/m| < 1 % de F/m: "
        "son 0 en contacto limpio y 110 al despegar. No hace falta calibrar nada "
        "para usarlo y no tiene falsos positivos.\n\n"
        "LIMITE HONESTO DEL ENSAYO: resuelve bien la TRANSICION asentada/suelta "
        "(entre S3 y S4), no el grado de apriete. Dentro del grupo asentado la "
        "lectura no es monotona, y S4/S5/S6 saturan todos en el mismo valor. Es un "
        "ensayo de dos clases, no un medidor de precarga."
    ),
    hipotesis=(
        Hipotesis("El ancho de banda de adquisicion es 5 kHz.", "X",
                  "Entra en el presupuesto de ruido, pero NO se aplico al "
                  "calculo del rasgo. Los numeros reportados son sin filtrar, "
                  "y con el filtro MEJORAN: x579 -> x4608 a 5 mJ, x112 -> x210 "
                  "en la peor energia."),
        Hipotesis("La ventana de 3 ms es adecuada.", "E",
                  "Es una eleccion heredada, no un optimo. La separacion en la "
                  "peor energia va de x45 (0.5 ms) a x127 (5 ms). Alargarla es "
                  "gratis: el ritmo de disparo es de 125 ms."),
        Hipotesis("La respuesta propia del acelerometro no importa.", "E",
                  "No esta en el modelo. Un ADXL1005 rueda a ~20 kHz y "
                  "atenuaria parte del rizado de 33 kHz de S0: conservador."),
    ),
    anclas=("test_softprobe.py :: test_el_despegue_se_detecta_por_el_riel_plano",
            "test_softprobe.py :: la energia de la señal le gana al pico"),
    banco=("C", "D"),
    si_falla="Si la separacion medida en banco queda por debajo de x100, revisar "
             "primero zeta (ensayo B) y despues el hueco (ensayo A). El rasgo no "
             "es el sospechoso: es el mejor de los probados.",
)


# ---------------------------------------------------------------------------
# B5 -- EL GOLPE QUE EXCITA
# ---------------------------------------------------------------------------

B5 = Bloque(
    id="B5",
    nombre="El golpe, y como se mide a si mismo",
    pregunta="¿Con cuanta energia hay que golpear, y como se sabe cuanta fue?",
    entradas=("escalera", "rasgo", "LAH04"),
    salidas=(
        Magnitud("E_golpe", "Energia de golpe recomendada", "3 a 5", "mJ", "S",
                 "TIENE OPTIMO, y no es el minimo."),
        Magnitud("ritmo", "Ritmo maximo de disparo", 8, "tiros/s", "M",
                 "Lo fija el ring-down del palpador (29 ms al 1 % con zeta = 0.02)."),
        Magnitud("v_maza", "Velocidad de la maza por back-EMF", "u = R i + L di/dt + K_F v",
                 "m/s", "M", "Con el drive abierto, u = K_F(x) v directamente."),
        Magnitud("err_cociente", "Error del cociente de velocidades", 0.145, "%", "M",
                 "Back-EMF. El sensor inductivo da 0.291 %: el back-EMF es 2x mejor."),
        Magnitud("err_absoluto", "Error de la energia absoluta", 4.0, "%", "M",
                 "Sistematico y calibrable; la repetibilidad es 0.17 %."),
        Magnitud("tau_e", "Constante electrica de la bobina", 43.1, "us", "M",
                 "Comparable al contacto (60 us): hay que abrir el drive ~5 tau "
                 "= 215 us antes del impacto, que a 1.48 m/s son 318 um de "
                 "carrera. Una nota anterior decia 265 um: son 4.15 tau."),
    ),
    ecuacion="e = v_rebote / v_incidente = (K v_r) / (K v_i)   -> K se cancela EXACTO\n"
             "eta = 1 - e^2      (fraccion de energia entregada a la cuña)",
    explicacion=(
        "LA ENERGIA DEL GOLPE TIENE OPTIMO. El limite de arriba ya se conocia: con "
        "el golpe fuerte hasta la cuña ajustada despega del hombro y la escalera se "
        "aplana. El de abajo es menos obvio: a 1 mJ la cuña ajustada S0 devuelve mas "
        "señal que S1 y S2, o sea que la escalera deja de ordenar en el extremo "
        "apretado. El maximo es ancho, 3-5 mJ.\n\n"
        "MEDIR LA VELOCIDAD CON LA PROPIA BOBINA. El actuador es un voice coil: la "
        "fuerza contraelectromotriz que aparece en sus bornes es proporcional a la "
        "velocidad. Midiendo u e i se despeja v sin agregar ningun sensor. El "
        "problema es que la escala K_F(x) varia 31 % a lo largo de la carrera, lo "
        "que da 4 % de error en la energia absoluta.\n\n"
        "PERO SI SE MIDEN LAS DOS VELOCIDADES, EL ERROR DE ESCALA SE CANCELA "
        "EXACTO. El discriminante es un cociente (indice tipo Leeb, o eta = 1-e^2), "
        "y en un cociente K se va: e = (K v_r)/(K v_i) = v_r/v_i. Lo que NO se "
        "cancela es la VARIACION de K entre los dos instantes, o sea dK/dx -- y ahi "
        "hay un regalo geometrico: la curva del LAH04 tiene su maximo en el centro "
        "de carrera, donde dK/dx = 0. Haciendo caer el impacto en el centro el "
        "residuo es 0.04 % contra 0.41 % a 1.5 mm del centro.\n\n"
        "CUIDADO CON LA ARQUITECTURA: si el lanzador SEPARA la maza (resorte, vuelo "
        "libre), la bobina solo ve la velocidad de separacion y no el rebote. Con "
        "palanca no se separa, y ahi el back-EMF ve las dos -- pero entonces el 49 % "
        "de la masa equivalente ES el actuador, cosa que hay que tener en cuenta."
    ),
    hipotesis=(
        Hipotesis("R de la bobina conocida al 5 % y K_F al 2 %.", "V",
                  "Afecta la energia absoluta (4 %), no el cociente."),
        Hipotesis("El impacto cae en el centro de carrera.", "X",
                  "Es gratis de conseguir y vale 10x en el residuo de dK/dx."),
    ),
    anclas=("test_backemf.py :: test_el_error_de_escala_cancela_exacto_en_el_cociente",
            "test_backemf.py :: test_conviene_que_el_impacto_caiga_en_el_centro_de_la_carrera",
            "test_backemf.py :: test_en_el_cociente_el_backemf_le_gana_al_inductivo"),
    banco=("D",),
    si_falla="Si el back-EMF no llega, queda el sensor inductivo del proyectil, "
             "que da 0.291 % en el cociente: peor, pero suficiente. Ningun "
             "resultado de B1-B4 depende de esta eleccion.",
)


# ---------------------------------------------------------------------------
# B6 -- LA DECISION  (el bloque abierto)
# ---------------------------------------------------------------------------

B6 = Bloque(
    id="B6",
    nombre="La decision: asentada o suelta",
    pregunta="¿Como se combinan el rasgo y la energia del golpe en un veredicto?",
    entradas=("rasgo", "separacion", "E_golpe", "err_cociente", "despegue_detect"),
    salidas=(
        Magnitud("veredicto", "Clase", "asentada | suelta", "-", "X",
                 "Dos clases, no un grado de apriete."),
        Magnitud("descarte", "Tiros descartados", "los que despegan", "-", "X",
                 "El detector de B4 es binario y se aplica antes de clasificar."),
        Magnitud("clasificador", "Clasificador conjunto", "PENDIENTE", "-", "E",
                 "Falta: usar la energia del golpe como covariable del rasgo."),
    ),
    ecuacion="veredicto = f(rasgo normalizado por E_golpe)      <- falta calibrar f",
    explicacion=(
        "ESTE ES EL UNICO BLOQUE QUE NO ESTA CERRADO. El rasgo de B4 separa x112, "
        "pero depende tambien de con cuanta energia se golpeo, y esa energia varia "
        "tiro a tiro. B5 la mide con 0.145 % de error en el cociente, que es mas "
        "que suficiente para usarla como covariable -- pero la funcion que combina "
        "las dos cosas todavia no esta ajustada, porque ajustarla pide datos de "
        "banco, no de simulacion.\n\n"
        "Lo que SI esta definido es el orden de operaciones: primero el detector de "
        "despegue descarta el tiro (binario, sin calibracion); despues se normaliza "
        "el rasgo por la energia entregada; recien ahi se compara contra el umbral. "
        "Y el umbral se calibra contra cuñas de estado conocido, no se deriva del "
        "modelo.\n\n"
        "Tambien queda afuera del modelo el montaje del palpador en el brazo del "
        "crawler y su dinamica propia."
    ),
    hipotesis=(
        Hipotesis("El umbral se calibra en banco contra cuñas de estado conocido.",
                  "X", "Derivarlo del modelo seria confiar en k_hombro."),
    ),
    anclas=(),
    banco=("C", "D"),
    si_falla="Es trabajo pendiente, no un riesgo: la separacion de x112 deja "
             "muchisimo margen para cualquier clasificador razonable.",
    abierto=True,
)


MODELO: tuple[Bloque, ...] = (B1, B2, B3, B4, B5, B6)


# ---------------------------------------------------------------------------
# Los ensayos de banco, atados a lo que matan
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Ensayo:
    id: str
    nombre: str
    mata: str
    instrumentos: str
    criterio: str
    bloques: tuple[str, ...]


BANCO: tuple[Ensayo, ...] = (
    Ensayo("A", "¿Existe el hueco espectral?",
           "La hipotesis k_hombro, que es la unica que puede tumbar el metodo.",
           "Acelerometro de choque pegado a la cuña, >=50 kHz, +-5000 g, 200 kS/s. "
           "NO necesita palpador.",
           "La cuña asentada responde arriba de 20 kHz y la suelta abajo de 1 kHz.",
           ("B1", "B2")),
    Ensayo("B", "Ping test del palpador construido",
           "La hipotesis zeta, que es el parametro mas sensible del diseño.",
           "Un golpecito y el registro del decaimiento. Da zeta y f0 de una sola "
           "medicion.",
           "zeta <= 0.02 y f0 entre 700 y 1700 Hz.",
           ("B3",)),
    Ensayo("C", "Palpador contra referencia, barriendo precarga",
           "Que la separacion simulada exista en fierro.",
           "Palpador + acelerometro de referencia sobre la ranura de prueba.",
           "Separacion > x100 entre 25 % y 5 % de precarga.",
           ("B3", "B4", "B6")),
    Ensayo("D", "Robustez: precarga, despegue, repetibilidad, orientacion",
           "Los supuestos de operacion del crawler.",
           "El mismo banco de C, variando precarga, energia y orientacion.",
           "Ganancia insensible a la precarga (+-20 % -> <1 %), umbral de despegue "
           "donde lo predice F/m, repetibilidad dentro del presupuesto de ruido.",
           ("B3", "B4", "B5", "B6")),
)


# ---------------------------------------------------------------------------
# Validacion de la cadena
# ---------------------------------------------------------------------------

def verificar_cadena(modelo: tuple[Bloque, ...] = MODELO) -> dict:
    """Comprueba que el modelo cierra: nada consume lo que nadie produce.

    Devuelve un informe con los simbolos huerfanos, los bloques sin
    verificacion y los bloques abiertos. Un modelo sano tiene las dos
    primeras listas vacias.
    """
    disponibles = set(EXTERNAS_SIMBOLOS)
    huerfanos: list[tuple[str, str]] = []
    sin_verificar: list[str] = []
    orden: list[str] = []

    for b in modelo:
        for e in b.entradas:
            if e not in disponibles:
                huerfanos.append((b.id, e))
        if not b.anclas and not b.banco:
            sin_verificar.append(b.id)
        disponibles |= set(b.simbolos())
        orden.append(b.id)

    #  Todo ensayo de banco tiene que servirle a algun bloque, y todo bloque
    #  que declara un ensayo tiene que existir en BANCO.
    ids_banco = {e.id for e in BANCO}
    banco_inexistente = sorted(
        {x for b in modelo for x in b.banco} - ids_banco)

    return {
        "orden": orden,
        "huerfanos": huerfanos,
        "sin_verificar": sin_verificar,
        "banco_inexistente": banco_inexistente,
        "abiertos": [b.id for b in modelo if b.abierto],
        "n_salidas": sum(len(b.salidas) for b in modelo),
        "cierra": not huerfanos and not sin_verificar and not banco_inexistente,
    }


def resumen() -> str:
    """El modelo entero en una pantalla, para leer antes de entrar al detalle."""
    lineas = ["CADENA DEL ENSAYO WTD", ""]
    for b in MODELO:
        marca = "  [ABIERTO]" if b.abierto else ""
        lineas.append(f"{b.id}  {b.nombre}{marca}")
        lineas.append(f"      {b.pregunta}")
        lineas.append(f"      entra:  {', '.join(b.entradas)}")
        lineas.append(f"      sale:   {', '.join(b.simbolos())}")
        lineas.append(f"      banco:  {', '.join(b.banco) or '-'}")
        lineas.append("")
    inf = verificar_cadena()
    lineas.append(f"cadena cierra: {inf['cierra']}   "
                  f"({inf['n_salidas']} magnitudes, "
                  f"{len(inf['abiertos'])} bloque(s) abierto(s))")
    return "\n".join(lineas)


def riesgos() -> list[dict]:
    """Las hipotesis estimadas [E], ordenadas por cuanto se lleva si fallan."""
    out = []
    for b in MODELO:
        for h in b.hipotesis:
            if h.origen == "E":
                out.append({"bloque": b.id, "hipotesis": h.texto,
                            "consecuencia": h.si_es_falsa,
                            "ensayo": ", ".join(b.banco) or "-"})
    return out


if __name__ == "__main__":       # pragma: no cover
    print(resumen())
    print()
    for r in riesgos():
        print(f"[{r['bloque']}] {r['hipotesis']}  -> ensayo {r['ensayo']}")
