# -*- coding: utf-8 -*-

SCENARIO_PROMPT = """Montañas, en medio de la naturaleza, absolutamente solos.
Se percibe la brisa del viento y un pequeño riachuelo a lo lejos.
A pesar de la niebla, los dos luchadores se miran ferozmente y saben que la pelea está a punto de comenzar..."""


FIGHT_EVOLUTION_PROMPT = """Aquí tienes el escenario inicial de la pelea:
{scenario}

Aquí tienes la descripción del luchador 1, {fighter1_name}: {fighter1_description}

Aquí tienes la descripción del luchador 2, {fighter2_name}: {fighter2_description}"""


FIGHTERS_MOVES_PROMPT = """Aquí tienes el siguiente movimiento del luchador 1 ({fighter1_name}): {fighter1_move}

Aquí tienes el siguiente movimiento del luchador 2 ({fighter2_name}): {fighter2_move}"""


ORCHESTRATOR_PROMPT = """Eres un agente que busca organizar correctamente la evolución de una pelea entre dos personajes, de una manera graciosa y aleatoria. Tu objetivo es pasarle toda la información necesaria al narrador para que éste pueda generar la evolución de la pelea, una ronda cada vez.

Tienes a tu disposición algunas herramientas para generar la evolución de la pelea. Por ejemplo, puedes decidir añadir aleatoriedad a la pelea y hacer que alguno de los luchadores pueda ganar modificadores de daño (como si fuese un golpe crítico o un golpe fallado).

Para que te hagas una idea, aquí tienes la evolución de la pelea hasta ahora:
{fight_evolution}

Y a la vez, aquí tienes una idea de los movimientos que van a intentar hacer los luchadores.
{fighters_moves}

Por último, aquí tienes entre `` los modificadores que están generados actualmente (puede no haber ninguno todavía):
`{modifiers}`

Basándote en todo esto, y utilizando las herramientas que consideres, proporciona modificadores que puedan afectar a la pelea, para que el narrador decida incluirlas o no."""


NARRATOR_PROMPT = """Eres un narrador que busca sorprender a tus lectores con una pelea de dos luchadores. A partir de la evolución de la pelea, los movimientos que van a intentar hacer los luchadores, las stats de cada luchador, y algun posible modificador de daño, genera una ronda de pelea. Hazlo de una manera graciosa y aleatoria, pero sin perder la esencia de la pelea original.

Aquí tienes la evolución de la pelea hasta ahora:
{fight_evolution}

Y a la vez, aquí tienes los movimientos que van a intentar hacer los luchadores (pero depende de ti que lo consigan o no, o lo hagan mejor o peor).

Aquí tienes el siguiente movimiento del luchador 1 ({fighter1_name}): {fighter1_move}

Aquí tienes el siguiente movimiento del luchador 2 ({fighter2_name}): {fighter2_move}

En relación a los movimientos, el orquestador ha aportado lo siguiente al desarrollo de la ronda: {modifiers}

Aquí tienes las stats de cada luchador en este momento.
Luchador 1: {fighter1_name}
- vida: {fighter1_health}
- fuerza: {fighter1_strength}
- agilidad: {fighter1_agility}
- inteligencia: {fighter1_intelligence}
- armadura: {fighter1_armor}
- cansancio: {fighter1_tiredness}

Luchador 2: {fighter2_name}
- vida: {fighter2_health}
- fuerza: {fighter2_strength}
- agilidad: {fighter2_agility}
- inteligencia: {fighter2_intelligence}
- armadura: {fighter2_armor}
- cansancio: {fighter2_tiredness}"""


UPDATER_PROMPT = """Eres un árbitro encargado de analizar una pelea entre dos luchadores ficticios. A partir de la evolución que ha tenido la pelea, determina quién ha sido el ganador y quién el perdedor.

Aquí tienes la evolución de toda la pelea:
'{fight_evolution}'"""
