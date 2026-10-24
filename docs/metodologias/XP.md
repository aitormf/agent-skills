# XP (Extreme Programming)

> Notas de estudio. Ejemplos basados en una app de carpooling.

## Qué es

**XP** es una metodología ágil centrada en la **calidad técnica** y en el **feedback continuo**. La creó **Kent Beck** en 1996, en el proyecto de nóminas **C3 de Chrysler**, junto a **Ward Cunningham** y **Ron Jeffries**. La difundió con el libro *Extreme Programming Explained: Embrace Change*:

- **1ª edición (1999):** más rígida, con 12 prácticas que había que aplicar todas juntas.
- **2ª edición (2004, con Cynthia Andres):** más flexible. Añade el valor del respeto, explicita los principios y separa las prácticas en primarias y derivadas.

El subtítulo resume la idea: **"Embrace Change"** (abraza el cambio).

## La idea central

> Los requisitos **van a cambiar**. En lugar de intentar evitarlo con más planificación, XP organiza el trabajo para que **el cambio sea barato**.

En el desarrollo clásico, el coste de un cambio crece exponencialmente con el tiempo: un cambio en producción cuesta 100 veces más que en requisitos. Beck sostiene que, con las prácticas adecuadas (tests automáticos, diseño simple, refactorización continua, integración frecuente), **esa curva se aplana**. Si cambiar es barato, no hace falta acertarlo todo al principio.

El nombre "extremo" viene de **llevar al límite** las prácticas que ya se sabía que funcionaban:

| Si esto es bueno... | ...hazlo siempre |
|---|---|
| Revisar código | Revisión continua: **pair programming** |
| Probar | Tests constantes: **TDD** |
| Diseñar | Diseño continuo: **refactorización** diaria |
| La simplicidad | El **diseño más simple** que funcione |
| Integrar | Integración **varias veces al día** |
| Ciclos cortos | Iteraciones de **una semana**, con feedback en minutos |

---

## Los tres niveles: valores → principios → prácticas

XP se construye en capas:

- **Valores:** lo que nos importa. Son universales.
- **Prácticas:** lo que hacemos cada día. Son concretas.
- **Principios:** el puente entre ambos. Explican por qué una práctica sirve a un valor.

Beck insiste en que **las prácticas sin valores son ritual vacío**. Es la misma lección que con SDD, DDD y BDD.

### Los 5 valores

1. **Comunicación.** La mayoría de los problemas de un proyecto vienen de que alguien no sabía algo que otro sí sabía. Se prefiere hablar cara a cara antes que documentar.
2. **Simplicidad.** *"¿Qué es lo más simple que podría funcionar?"* Se resuelve el problema de hoy, no el imaginado del mes que viene. De aquí sale **YAGNI** (*You Aren't Gonna Need It*).
3. **Feedback.** Saber lo antes posible si vas bien. Llega en varias escalas:
   - Segundos: el test pasa o falla.
   - Minutos: la integración continua.
   - Días: el cliente prueba la iteración.
   - Semanas: usuarios reales en producción.
4. **Coraje.** Atreverse a refactorizar código que funciona, a tirar código malo, a decir "esto no llega" o "me equivoqué". Los tests son los que lo hacen posible: sin red de seguridad, no hay coraje.
5. **Respeto** (añadido en la 2ª edición). Hacia los compañeros, el cliente y el propio trabajo. Sin respeto, los otros cuatro no funcionan.

### Algunos principios clave (2ª edición)

| Principio | Significado |
|---|---|
| **Baby steps** | Pasos pequeños. Un paso pequeño mal dado cuesta poco de deshacer |
| **Feedback rápido** (flow) | Entregar en flujo continuo, no en grandes lotes |
| **Mejora continua** | No buscar la perfección a la primera: hacer, aprender, mejorar |
| **Economía** | El software tiene que aportar valor de negocio pronto |
| **Beneficio mutuo** | Cada práctica debe beneficiar a todos, ahora y en el futuro |
| **Calidad** | Bajar la calidad no acelera; la alta calidad permite ir más rápido |
| **Redundancia** | Los problemas críticos se atacan desde varios frentes (tests + pairing + CI) |
| **Fallo como información** | Si no sabes qué opción es mejor, prueba las dos rápidamente |
| **Responsabilidad aceptada** | La responsabilidad no se impone: se acepta. Quien estima es quien hace el trabajo |

---

## Las prácticas

### Prácticas de programación

#### 1. TDD (Test-Driven Development)

El ciclo **rojo → verde → refactor**, en minutos:

1. **Rojo:** escribes un test pequeño que falla.
2. **Verde:** escribes el código **mínimo** para que pase, aunque sea feo.
3. **Refactor:** mejoras el diseño sin cambiar el comportamiento, con los tests en verde.

```ts
// 1. ROJO
it('no permite reservar si no quedan plazas', () => {
  const trip = new Trip(tripId(), 1);
  trip.book(passenger('ana'));
  expect(() => trip.book(passenger('luis'))).toThrow(NoSeatsAvailable);
});

// 2. VERDE: lo mínimo
book(p: PassengerId) {
  if (this.bookings.length >= this.seats) throw new NoSeatsAvailable(this.id);
  this.bookings.push(Booking.create(p));
}

// 3. REFACTOR: por ejemplo, extraer `hasFreeSeats()` si mejora la lectura
```

**Por qué importa:**

- Los tests documentan el comportamiento.
- Te obligan a diseñar código testeable, lo que lleva a bajo acoplamiento.
- Te dan el coraje para refactorizar.

#### 2. Pair programming

Dos personas en un ordenador, con dos roles que se intercambian a menudo:

- **Driver:** escribe y piensa en la línea actual.
- **Navigator:** revisa, piensa en el conjunto, anticipa problemas y casos límite.

**Por qué importa:**

- Revisión de código continua.
- Transmisión de conocimiento: nadie es el único que sabe algo.
- Menos bugs y más foco: es difícil distraerse con alguien al lado.

Variantes: **mob programming** o **ensemble** (todo el equipo en un ordenador) y **ping-pong pairing** (uno escribe el test y el otro lo hace pasar).

#### 3. Refactorización continua

Mejorar el diseño en pasos pequeños **sin cambiar el comportamiento**, todos los días y como parte normal del trabajo, no como "un sprint de refactor".

- Referencia: Martin Fowler, *Refactoring* (1999, 2ª ed. 2018).
- Beck lo reformuló después como **"Tidy First?"** (2023): ordenar un poco el código *antes* de cambiarlo, para que el cambio sea fácil.

> *"Make the change easy (warning: this may be hard), then make the easy change."* (Kent Beck)
> Primero haz que el cambio sea fácil (aviso: eso puede ser difícil); luego haz el cambio fácil.

#### 4. Diseño simple: las 4 reglas de Beck

Un diseño es simple si, por orden de prioridad:

1. **Pasa todos los tests.**
2. **Revela su intención:** se entiende qué hace.
3. **No tiene duplicación** (DRY).
4. **Tiene el menor número de elementos posible:** sin clases, capas ni abstracciones innecesarias.

**Por qué importa:** evita tanto el código sucio como la **sobreingeniería**. Conecta con DDD: no meter repositorios, factories y CQRS si no hacen falta.

#### 5. Integración continua

Integrar en la rama principal **varias veces al día**, con build y tests automáticos en cada integración.

- **Ten-minute build:** el build completo con tests debe tardar **10 minutos o menos**. Si tarda más, la gente deja de ejecutarlo.

**Por qué importa:** los conflictos y errores de integración se detectan cuando son pequeños. Es el origen de lo que hoy llamamos CI/CD.

#### 6. Propiedad colectiva del código

Cualquiera puede cambiar cualquier parte del código. No existe "el módulo de Juan".

**Por qué importa:** evita cuellos de botella y silos de conocimiento. Requiere tests y estándares para que sea seguro.

#### 7. Estándares de código

Un estilo común para que el código parezca escrito por una sola persona. Hoy esto lo resuelven linters y formateadores automáticos.

### Prácticas de planificación

#### 8. Historias de usuario

Los requisitos se escriben como historias cortas, en lenguaje de negocio, que caben en una tarjeta:

> *Como pasajero, quiero cancelar una reserva para no pagar un viaje que no voy a hacer.*

La tarjeta **no es la especificación**: es un **recordatorio para una conversación**. Ron Jeffries lo resumió en las **3 C**:

- **Card** (la tarjeta).
- **Conversation** (la conversación).
- **Confirmation** (los tests de aceptación).

De aquí salen BDD y las historias de usuario de Scrum.

#### 9. Planning Game

- **Negocio decide:** qué se hace, en qué orden y cuándo se publica.
- **Desarrollo decide:** cuánto cuesta (estimación) y cómo se hace.

Nadie invade el terreno del otro.

#### 10. Ciclos

| Ciclo | Duración | Qué se hace |
|---|---|---|
| **Ciclo semanal** | 1 semana | Elegir historias, dividirlas en tareas, implementarlas con tests y demostrarlas |
| **Ciclo trimestral** | 3 meses | Revisar objetivos, temas grandes y cuellos de botella |
| **Slack** | Dentro de cada ciclo | Reservar tareas menores que se pueden descartar si vas tarde. Así se cumple lo prometido |

#### 11. Entregas pequeñas

Poner software en producción con mucha frecuencia. Cuanto más pequeño el cambio, menor el riesgo y antes llega el feedback real.

#### 12. Spikes

Un experimento corto y **desechable** para resolver una duda técnica o estimar algo desconocido. El código del spike se tira.

### Prácticas de equipo

#### 13. Equipo completo (antes "cliente in situ")

Alguien de negocio **forma parte del equipo** y está disponible para resolver dudas al momento, en vez de un documento de requisitos de 200 páginas.

#### 14. Ritmo sostenible (antes "semana de 40 horas")

No se trabajan horas extra de forma continuada. La gente cansada mete bugs y toma malas decisiones. Si un equipo necesita horas extra dos semanas seguidas, el problema es el plan, no las personas.

#### 15. Espacio de trabajo informativo

El estado del proyecto está a la vista de todos: tableros, gráficos, el build en verde o en rojo.

#### 16. Retrospectivas y reflexión

Revisar con regularidad qué funciona y qué no, y ajustar el proceso.

---

## XP frente a Scrum

| | Scrum | XP |
|---|---|---|
| **Foco** | Gestión del trabajo | Prácticas de ingeniería |
| **Dice cómo programar** | No | Sí: TDD, pairing, CI, refactor |
| **Iteración** | Sprints de 1 a 4 semanas | Ciclos de 1 semana |
| **Cambios durante la iteración** | Se evitan durante el sprint | Se permite cambiar historias no empezadas por otras del mismo tamaño |
| **Roles** | Product Owner, Scrum Master, Developers | Equipo completo, cliente, coach (más flexible) |

**En la práctica se combinan mucho:** Scrum para organizar y XP para programar. Jeff Sutherland, cocreador de Scrum, ha dicho a menudo que los equipos Scrum más productivos usan prácticas de XP.

---

## Críticas habituales

- **El pair programming parece caro:** dos personas para una tarea. Los defensores responden que compensa en menos bugs y menos tiempo de revisión, pero no a todo el mundo le funciona ni le gusta.
- **El cliente in situ es poco realista:** pocas empresas pueden dedicar a alguien de negocio a tiempo completo.
- **Exige mucha disciplina:** sin TDD y refactor reales, "diseño simple" se convierte en "sin diseño".
- **La 1ª edición era "todo o nada":** las prácticas se apoyaban unas en otras, y quitar una debilitaba las demás. La 2ª edición lo suavizó.
- **Escala mal a organizaciones grandes:** se pensó para equipos de unas 10 personas en la misma sala.
- **Poca documentación:** puede ser un problema en sectores regulados o con mucha rotación de personas.

## Estado actual

XP como "marca" se usa poco, pero **ha ganado en sus prácticas**. Muchas son hoy estándar de la industria, aunque la gente no sepa que vienen de XP:

- Integración continua → **CI/CD**.
- Tests automáticos y **TDD**.
- **Refactorización** como práctica habitual.
- **Historias de usuario** (adoptadas por Scrum).
- **Entregas pequeñas** → despliegue continuo.
- Pairing y mob programming en muchos equipos.

---

## XP con agentes de IA

Las prácticas de XP son justo lo que hace seguro trabajar con agentes:

| Práctica XP | Cómo encaja con agentes de IA |
|---|---|
| **Pair programming** | El agente es el *driver* que teclea; tú eres el *navigator* que revisa, dirige y piensa en el conjunto. Es el modelo más sano de trabajo con IA |
| **TDD** | El test es la spec ejecutable y el criterio objetivo de "terminado" para el agente. Prompt: *"escribe primero el test que falla, luego el código mínimo"* |
| **Baby steps** | Diffs pequeños que puedes revisar de verdad. Evitan los cambios gigantes del agente |
| **Diseño simple (4 reglas)** | Frenan la tendencia de los agentes a la sobreingeniería: abstracciones, capas y configuraciones innecesarias |
| **Refactor / Tidy First** | Los agentes son muy buenos refactorizando con los tests en verde. Puedes pedir *"ordena antes de cambiar"* |
| **Ten-minute build** | Si los tests tardan poco, el agente puede ejecutarlos en cada paso. Un build lento rompe el ciclo |
| **Integración continua y entregas pequeñas** | Commit tras cada paso: si el agente se desvía, vuelves atrás sin perder trabajo |
| **Spike** | El vibe coding es, en el fondo, un spike: un experimento desechable. Válido si luego se tira |
| **Ritmo sostenible** | Revisar código generado cansa. La fatiga hace que acabes aprobando sin leer |

**Kent Beck** ha escrito sobre esto con el nombre de **"augmented coding"**. Su idea es usar agentes **manteniendo TDD y la calidad del código**, en contraposición al vibe coding, donde no importa el código, solo el resultado.

Esto explica por qué Beck y Fowler critican el SDD: va contra el **feedback** y los **baby steps** de XP, porque intenta acertar la especificación completa antes de aprender implementando ([Martin Fowler, Fragments: January 8, 2026](https://martinfowler.com/fragments/2026-01-08.html)).
