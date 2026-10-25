# BDD (Behavior-Driven Development)

> Notas de estudio. Ejemplos basados en una app de carpooling.

## Qué es

**BDD** es una práctica para **definir el comportamiento del software mediante ejemplos concretos**, acordados entre negocio, desarrollo y QA. Esos ejemplos se escriben en un lenguaje que entiende todo el mundo y, además, **se ejecutan como tests automáticos**.

Lo propuso **Dan North** en 2006 (artículo *Introducing BDD*). Partía de una frustración: al enseñar TDD, la gente se atascaba con preguntas como "¿qué testeo?", "¿cuánto?" o "¿cómo lo llamo?". Su respuesta fue cambiar la palabra "test" por "**comportamiento**" y hacerse una sola pregunta: *¿qué debería hacer el sistema?*

Está muy relacionado con:

- **TDD**, del que nace.
- **DDD**, porque usa el lenguaje ubicuo.
- **Specification by Example** (Gojko Adzic) y **ATDD**, que son prácticamente la misma familia.

## La idea central

> El problema no es escribir código, es **entender bien qué hay que construir**. Los malentendidos se detectan mejor con **ejemplos concretos** que con requisitos abstractos.

Comparemos un requisito abstracto con un ejemplo concreto:

- **Abstracto:** "El pasajero puede cancelar la reserva con reembolso según la política."
- **Concreto:** "Si Ana cancela 3 horas antes de un viaje de las 9:00, recupera los 5 €. Si cancela 30 minutos antes, no recupera nada."

El ejemplo concreto provoca enseguida preguntas que el requisito abstracto esconde: *¿y si cancela justo 1 hora antes? ¿Y si es el conductor quien cancela?*

---

## Las tres fases de BDD

Seb Rose y Gáspár Nagy las formalizan en sus *BDD Books*:

| Fase | Qué se hace | Quién |
|---|---|---|
| **1. Discovery** (descubrimiento) | Conversar con ejemplos para entender la regla y encontrar los huecos | Negocio, desarrollo y QA ("Three Amigos") |
| **2. Formulation** (formulación) | Escribir los ejemplos en un formato estructurado: Given / When / Then | Desarrollo y QA, revisado por negocio |
| **3. Automation** (automatización) | Conectar esos escenarios con código para que se ejecuten como tests | Desarrollo |

**El matiz clave:** la mayor parte del valor está en **Discovery**, en las conversaciones. Mucha gente cree que BDD consiste en "escribir tests en Gherkin", y eso es solo la fase 3. Sin las conversaciones, BDD se queda en una forma más verbosa de escribir tests.

---

## 1. Discovery: las conversaciones

### Three Amigos

Antes de empezar una historia se reúnen tres perspectivas, durante unos 20–30 minutos:

- **Negocio / Producto:** qué problema resolvemos.
- **Desarrollo:** cómo se podría construir y qué es difícil.
- **QA / Testing:** qué puede fallar y qué casos límite hay.

### Example Mapping

Es la técnica más usada para estas reuniones. La creó **Matt Wynne** (Cucumber) y se hace con tarjetas de colores:

```
🟨 HISTORIA:  Cancelar una reserva
   🟦 REGLA: Reembolso completo si se cancela con >1h de antelación
       🟩 Ejemplo: cancela 3h antes → recupera 5 €
       🟩 Ejemplo: cancela 1h 1min antes → recupera 5 €
   🟦 REGLA: Sin reembolso si se cancela con ≤1h
       🟩 Ejemplo: cancela 30 min antes → recupera 0 €
       🟩 Ejemplo: cancela justo 1h antes → recupera 0 €
   🟦 REGLA: Si cancela el conductor, el pasajero siempre recupera todo
       🟩 Ejemplo: conductor cancela 10 min antes → pasajero recupera 5 €
   🟥 PREGUNTA: ¿Qué pasa si el viaje ya ha empezado?
   🟥 PREGUNTA: ¿Hay comisión de gestión no reembolsable?
```

- **Amarillo:** la historia.
- **Azul:** las reglas de negocio.
- **Verde:** los ejemplos que ilustran cada regla.
- **Rojo:** las preguntas sin respuesta.

**Cómo se lee el tablero:**

- Muchas tarjetas rojas indican que la historia aún no está lista.
- Muchas azules indican que la historia es demasiado grande y hay que partirla.
- Cada tarjeta verde se convertirá en un escenario.

**Por qué funciona:** en 25 minutos sale a la luz lo que, de otro modo, aparecería como bug en producción o como discusión a mitad de sprint.

---

## 2. Formulation: Gherkin

Los ejemplos se escriben en **Gherkin**, un formato estructurado en lenguaje natural. Se puede escribir en español (`# language: es`), pero aquí se usa en inglés porque es lo más habitual:

```gherkin
Feature: Cancelar una reserva
  Como pasajero
  Quiero cancelar una reserva
  Para no pagar un viaje que no voy a hacer

  Rule: Reembolso completo si se cancela con más de 1 hora de antelación

    Scenario: Cancelación con tiempo suficiente
      Given Ana tiene una reserva de 5 € en un viaje que sale a las 09:00
      When Ana cancela la reserva a las 06:00
      Then Ana recibe un reembolso de 5 €
      And la plaza vuelve a estar disponible

  Rule: Sin reembolso si se cancela con 1 hora o menos

    Scenario Outline: Cancelación tardía
      Given Ana tiene una reserva de 5 € en un viaje que sale a las 09:00
      When Ana cancela la reserva a las <hora>
      Then Ana recibe un reembolso de <reembolso>

      Examples:
        | hora  | reembolso |
        | 08:00 | 0 €       |
        | 08:30 | 0 €       |
        | 08:59 | 0 €       |
```

La estructura de cada escenario:

- **Given** (Dado): el contexto o estado inicial.
- **When** (Cuando): la acción o evento, y **solo uno**.
- **Then** (Entonces): el resultado observable esperado.

### Cómo escribir buenos escenarios

1. **Declarativos, no imperativos.** Hay que describir *qué* pasa, no *cómo* se hace clic.
   - ❌ `When hago clic en "Mis reservas" And hago clic en "Cancelar" And confirmo el diálogo`
   - ✅ `When Ana cancela la reserva`
2. **Lenguaje de negocio**, que es el lenguaje ubicuo de DDD. Nada de tablas, endpoints ni IDs técnicos.
3. **Un solo comportamiento por escenario.**
4. **Ejemplos concretos y realistas**: "Ana", "5 €", "09:00", no "usuario1" ni "X".
5. **Pocos escenarios por regla.** Hay que cubrir la regla y sus límites, no todas las combinaciones posibles.

---

## 3. Automation: ejecutar los escenarios

Cada línea de Gherkin se conecta con código mediante **step definitions** (definiciones de pasos):

```ts
Given('Ana tiene una reserva de {int} € en un viaje que sale a las {string}',
  async (price, time) => {
    trip = Trip.create({ departure: time, seats: 3, price: Money.eur(price) });
    booking = trip.book(passengerId('ana'));
  });

When('Ana cancela la reserva a las {string}', async (time) => {
  refund = trip.cancelBooking(booking.id, at(time));
});

Then('Ana recibe un reembolso de {int} €', (amount) => {
  expect(refund).toEqual(Money.eur(amount));
});
```

Herramientas habituales:

| Ecosistema | Herramienta |
|---|---|
| JS/TS | Cucumber.js, Playwright-BDD |
| Java/Kotlin | Cucumber-JVM, JBehave |
| Python | behave, pytest-bdd |
| .NET | Reqnroll (sucesor de SpecFlow) |
| Ruby | Cucumber (el original) |

### ¿A qué nivel se automatiza?

Esta es una de las decisiones más importantes y donde más equipos se equivocan:

- **A través de la UI** (navegador): lento, frágil y caro de mantener. Solo para unos pocos flujos críticos.
- **A nivel de API o de dominio**: rápido y estable. **Es lo recomendado para la mayoría de escenarios.**

El ejemplo de arriba llama directamente al agregado `Trip`. Ahí encaja perfecto con DDD: el escenario testea la regla de negocio, no la pantalla.

---

## BDD frente a TDD

| | TDD | BDD |
|---|---|---|
| **Pregunta** | ¿Funciona este código? | ¿Hace el sistema lo que el negocio necesita? |
| **Audiencia** | Desarrolladores | Negocio, desarrollo y QA |
| **Lenguaje** | Código | Lenguaje de negocio (Gherkin) |
| **Granularidad** | Unidades pequeñas (funciones, clases) | Comportamientos o reglas de negocio |
| **Ciclo** | Rojo → verde → refactor, en minutos | Escenario → (muchos ciclos TDD dentro) → escenario en verde |

**No compiten, se complementan.** Es el llamado *doble ciclo*: un escenario BDD falla, y para hacerlo pasar se hacen varios ciclos TDD por dentro.

```
Escenario BDD (rojo)
   └─ test unitario (rojo) → código → verde → refactor
   └─ test unitario (rojo) → código → verde → refactor
Escenario BDD (verde) ✓
```

## BDD frente a SDD

| | SDD | BDD |
|---|---|---|
| **La spec es...** | Markdown en prosa | Ejemplos ejecutables |
| **¿Se desfasa del código?** | Sí, es el problema principal | No: si se desfasa, **el test falla** |
| **¿Quién la valida?** | Alguien que la lee (o la aprueba sin leer) | La máquina, en cada ejecución |
| **Tamaño** | Tiende a crecer ("montañas de markdown") | Acotado: pocos ejemplos por regla |

**BDD es, en cierto modo, lo que el SDD intenta ser:** una especificación que guía el desarrollo. La diferencia es que la de BDD **está viva porque se ejecuta**. Resuelve justo la crítica de "la spec se desfasa del código". También encaja con lo que defienden Birgitta Böckeler y Augment sobre el nivel "spec-anchored", donde los tests mantienen la spec alineada con el código.

---

## BDD con agentes de IA

1. **Los escenarios son la spec perfecta para un agente:** son cortos, concretos, sin ambigüedad y verificables. Encaja con la recomendación de Addy Osmani de una spec pequeña con criterios claros.
2. **El humano define el qué; el agente implementa el cómo.**
   - Prompt: *"Implementa lo necesario para que pasen los escenarios de `cancelar_reserva.feature`. No modifiques el `.feature`."*
   - El agente tiene un criterio objetivo de "terminado": los escenarios pasan.
3. **Protección contra el agente "creativo":** si cambia el comportamiento sin querer, un escenario falla.
4. **El agente también ayuda en Discovery:** puedes pedirle *"dada esta regla, propón ejemplos límite y preguntas abiertas"*. Es un Example Mapping asistido, aunque las respuestas las sigue dando negocio.
5. **Riesgo a vigilar:** que el agente genere los escenarios *y* el código. Entonces se validan a sí mismos y no aportan nada. **Los escenarios los escribe o revisa un humano.**

En el flujo de la guía de desarrollo con IA, en el nivel de "feature mediana o crítica", la spec corta y viva puede ser un `.feature`, en lugar de un markdown.

---

## Críticas habituales y antipatrones

- **Gherkin como lenguaje de scripting de tests:** escenarios imperativos, llenos de clics y selectores. Se pierde todo el valor y queda un test UI frágil con más pasos.
- **Saltarse Discovery:** QA o desarrollo escriben el Gherkin solos, sin conversación. Negocio nunca lo lee, así que la capa de lenguaje natural es puro coste.
- **Mantenimiento caro:** cientos de escenarios a nivel de UI, lentos e inestables.
- **Explosión de escenarios:** probar todas las combinaciones en Gherkin en lugar de en tests unitarios.
- **Capa extra innecesaria:** si negocio no va a leer nunca los escenarios, algunos equipos prefieren tests normales con nombres descriptivos (`it('reembolsa todo si se cancela con más de 1h')`). Así conservan el *pensamiento* BDD sin la herramienta.

Es la misma lección que con SDD y DDD: **el valor está en las conversaciones y los ejemplos, no en la herramienta**.

## Cuándo usarlo

- **Sí:** reglas de negocio con matices (precios, reembolsos, permisos, emparejamiento), cuando hay malentendidos frecuentes entre negocio y desarrollo, o en features críticas.
- **No, o en versión ligera:** CRUDs simples, código técnico sin reglas de negocio, prototipos, o cuando negocio no va a participar.
