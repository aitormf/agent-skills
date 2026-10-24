# DDD (Domain-Driven Design)

> Notas de estudio. Aún sin decidir si se aplicará en el equipo.
> Ejemplos basados en una app de carpooling.

## Qué es

**DDD** es una forma de diseñar software complejo **poniendo en el centro el dominio de negocio**: cómo funciona de verdad el negocio, sus reglas y su vocabulario. Lo propuso **Eric Evans** en *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003, el "libro azul"). **Vaughn Vernon** lo hizo más práctico en *Implementing Domain-Driven Design* (2013, el "libro rojo") y en *Domain-Driven Design Distilled* (2016).

A diferencia de Scrum o XP, **no es un proceso de trabajo**. Es una forma de **diseñar** y de **modelar**. Se combina con cualquier metodología.

Su idea central: la complejidad difícil de un sistema no suele ser técnica (bases de datos, frameworks), sino **de negocio**. Por eso el código tiene que reflejar fielmente el modelo de ese negocio, construido junto con los expertos del dominio.

## Las dos mitades de DDD

| Parte | Pregunta que responde | Nivel |
|---|---|---|
| **Diseño estratégico** | ¿Cómo dividimos el sistema y qué parte importa más? | Arquitectura, equipos, organización |
| **Diseño táctico** | ¿Cómo modelamos el código dentro de cada parte? | Clases, objetos, reglas |

Mucha gente empieza por la parte táctica (entidades, repositorios...). Evans y Vernon insisten en que **lo valioso es la estratégica**. La táctica sin la estratégica suele acabar en sobreingeniería.

---

## 1. Diseño estratégico

### Lenguaje ubicuo (Ubiquitous Language)

Es un vocabulario **común y preciso** entre negocio y desarrollo, que aparece **tal cual en el código**.

- Si negocio habla de "viaje", "trayecto", "plaza" y "reserva", el código tiene `Trip`, `Seat` y `Booking`, no `RideEntity` ni `UserTransaction2`.
- Si una palabra cambia de significado en una conversación, es una señal de que hay **dos conceptos distintos**.
- **Por qué importa:** cuando el código habla como el negocio, desaparecen las traducciones mentales, y con ellas los errores que se cuelan en esas traducciones.

### Subdominios

El negocio se divide en áreas, y no todas valen lo mismo:

| Tipo | Qué es | Ejemplo carpooling | Estrategia |
|---|---|---|---|
| **Core** | Lo que te diferencia de la competencia | El emparejamiento de conductores y pasajeros, los precios | Invertir aquí: mejores personas, DDD a fondo |
| **Supporting** | Necesario y específico, pero no diferencial | Valoraciones, gestión de incidencias | Hacerlo bien pero simple |
| **Generic** | Lo que todo el mundo necesita igual | Pagos, autenticación, envío de emails | Comprarlo o usar SaaS (Stripe, Auth0) |

**Por qué importa:** te dice **dónde gastar el esfuerzo**. Aplicar DDD completo a un subdominio genérico es tirar el dinero.

### Bounded Context (contexto delimitado)

Es **el concepto más importante de DDD**: una frontera dentro de la cual un modelo y su lenguaje tienen un significado único y coherente.

La misma palabra significa cosas distintas según el contexto. Por ejemplo, "Usuario":

- En **Viajes**: conductor o pasajero, con ruta, horario y plazas.
- En **Pagos**: titular, con método de pago y facturas.
- En **Identidad**: email, contraseña y roles.

El error clásico es construir **un único `User` gigante** con 80 campos que sirva para todo. DDD propone **un modelo por contexto**, cada uno con solo lo que necesita, conectados por un identificador común.

**Por qué importa:** evita el "big ball of mud", ese modelo único que nadie entiende y que se rompe al tocarlo. Los bounded contexts suelen corresponder a **equipos** y a veces a **microservicios** (aunque no tienen por qué).

### Context Mapping

Describe **cómo se relacionan** los contextos. Los patrones principales:

| Patrón | Significado |
|---|---|
| **Shared Kernel** | Dos contextos comparten una parte pequeña del modelo |
| **Customer / Supplier** | Uno depende del otro y negocian juntos qué necesita |
| **Conformist** | Te adaptas al modelo del otro sin poder influir (por ejemplo, una API externa) |
| **Anti-Corruption Layer (ACL)** | Una capa traduce el modelo ajeno al tuyo para que no te "contamine" |
| **Open Host Service / Published Language** | Expones una API o un formato estable para muchos consumidores |
| **Separate Ways** | No integrarse en absoluto |

Ejemplo: integras Stripe. En vez de que `PaymentIntent` de Stripe aparezca por todo tu código, pones un **ACL** que lo traduce a tu `Pago`. Si algún día cambias de proveedor, solo tocas esa capa.

---

## 2. Diseño táctico (dentro de un bounded context)

### Entidad (Entity)

Un objeto con **identidad propia que se mantiene en el tiempo**, aunque cambien sus datos.

- `Trip` (viaje) es una entidad: el viaje `#123` sigue siendo el mismo aunque cambie la hora.

### Value Object

Un objeto **definido solo por sus valores**, sin identidad e **inmutable**.

- `Money(5, EUR)`, `Location(lat, lng)`, `TimeWindow(08:00–08:30)`.
- Dos `Money(5, EUR)` son iguales e intercambiables.
- **Por qué importa:** las reglas viven dentro del objeto (no hay dinero negativo, no se suman monedas distintas), en lugar de repetirse por todo el código. Es una de las piezas de DDD que más rinde y más fácil de adoptar.

### Agregado (Aggregate)

Un **grupo de entidades y value objects que se tratan como una unidad** de consistencia, con una **raíz** (aggregate root) que es la única puerta de entrada.

- `Trip` es la raíz e incluye sus `Booking` (reservas).
- Regla: "no se pueden reservar más plazas de las disponibles". Esa invariante **la protege el agregado**:

```ts
class Trip {
  private bookings: Booking[] = [];
  constructor(readonly id: TripId, private seats: number) {}

  book(passengerId: PassengerId): Booking {
    if (this.bookings.length >= this.seats) {
      throw new NoSeatsAvailable(this.id);
    }
    const booking = Booking.create(passengerId);
    this.bookings.push(booking);
    this.record(new SeatBooked(this.id, passengerId)); // evento de dominio
    return booking;
  }
}
```

Nadie puede añadir un `Booking` saltándose `trip.book()`.

Reglas de diseño de Vernon:

- Agregados **pequeños**.
- Se referencian entre sí **por ID**, no por objeto.
- **Una transacción modifica un solo agregado**.
- Entre agregados, **consistencia eventual** mediante eventos.

**Por qué importa:** las reglas de negocio no pueden saltarse, y los límites de consistencia quedan claros.

### Evento de dominio (Domain Event)

Algo **relevante para el negocio que ya ha ocurrido**, nombrado en pasado: `SeatBooked`, `TripCancelled`, `PaymentCaptured`.

- Otros agregados o contextos reaccionan a él. Por ejemplo, Pagos cobra al recibir `SeatBooked`, y Notificaciones avisa al conductor.
- **Por qué importa:** desacopla los contextos y deja explícito lo que pasa en el negocio. Es la base de arquitecturas orientadas a eventos y de **Event Sourcing**.

### Repositorio (Repository)

Una abstracción para **guardar y recuperar agregados**, como si fueran una colección en memoria: `tripRepository.findById(id)` y `save(trip)`.

- Hay **un repositorio por agregado**, no por tabla.
- El dominio no sabe si detrás hay Postgres, Mongo o una API.

### Servicio de dominio (Domain Service)

Lógica de negocio que **no encaja naturalmente en una sola entidad**.

- Ejemplo: `MatchingService`, que empareja un pasajero con el mejor viaje entre muchos.

### Servicio de aplicación (Application Service)

**Orquesta un caso de uso** sin contener reglas de negocio: carga el agregado, llama al método de dominio, guarda y publica los eventos.

```ts
async function bookSeat(cmd: BookSeatCommand) {
  const trip = await tripRepo.findById(cmd.tripId);
  trip.book(cmd.passengerId);
  await tripRepo.save(trip);
}
```

### Factory

Encapsula la creación de objetos complejos o con reglas al nacer.

---

## 3. Arquitectura que suele acompañar a DDD

DDD no obliga a ninguna, pero encaja de forma natural con la **arquitectura hexagonal** (Ports & Adapters), Clean Architecture u Onion:

```
[ API / UI / colas ]  →  Aplicación (casos de uso)  →  DOMINIO (puro, sin dependencias)
                                     ↓
                     Infraestructura (BD, Stripe, email) implementa los puertos
```

- El **dominio no depende de nada técnico**. Las dependencias apuntan hacia dentro.
- **Por qué importa:** puedes testear las reglas de negocio sin base de datos, y cambiar la tecnología sin tocar el negocio.

Patrones que suelen ir con DDD: **CQRS** (separar escritura y lectura) y **Event Sourcing** (guardar los eventos en vez del estado). Son **opcionales**: añaden mucha complejidad y solo compensan en dominios concretos.

---

## 4. Cómo se descubre el dominio

- **Event Storming** (Alberto Brandolini): un taller con negocio y desarrollo, con post-its de colores en una pared. Se colocan los eventos de dominio en orden temporal y de ahí salen comandos, agregados y bounded contexts. Es la técnica más usada para arrancar con DDD.
- **Domain Storytelling**: los expertos cuentan escenarios reales y se dibujan.
- **Context Mapping**: un dibujo de los contextos y sus relaciones.

---

## 5. Cuándo usarlo y cuándo no

**Úsalo cuando:**

- El dominio es **complejo**, con muchas reglas, excepciones y conceptos que se cruzan.
- Es el **core** del negocio y va a vivir y evolucionar años.
- Hay varios equipos y necesitas fronteras claras.

**No lo uses (o solo en versión ligera) cuando:**

- Es básicamente un **CRUD** (formularios contra tablas).
- Es un subdominio genérico o un prototipo.
- No tienes acceso a expertos del dominio.

## 6. Críticas habituales

- **Sobreingeniería:** se aplica la parte táctica completa (repositorios, factories, CQRS...) a problemas simples.
- **Curva de aprendizaje alta,** con mucha jerga.
- **"DDD de clases" sin estrategia:** el patrón es copiar entidades y repositorios sin bounded contexts ni lenguaje ubicuo. Se obtiene todo el coste y ningún beneficio.
- **Exige acceso real a negocio.** Sin expertos del dominio, el modelo es una suposición.

Igual que con el SDD: **el valor está en pensar el modelo, no en la ceremonia**.

---

## 7. DDD y desarrollo con agentes de IA

- **El lenguaje ubicuo es contexto excelente para el agente.** Un glosario del dominio en `CLAUDE.md` o `AGENTS.md` hace que el agente nombre y razone como el negocio.
- **Los bounded contexts acotan el contexto del agente.** Trabajar dentro de un contexto pequeño evita llenar la ventana de contexto (la "dumb zone" de la que habla Dex Horthy).
- **Agregados y value objects protegen las invariantes.** Si el agente intenta saltarse una regla, el modelo o los tests lo impiden. Es una red de seguridad frente al código generado.
- **Un dominio puro se testea fácil,** así que encaja con TDD y con "el test como spec ejecutable".

---

## 8. Conclusión

**La idea general de DDD:** alta cohesión dentro de cada parte y bajo acoplamiento entre partes, con definiciones claras. Hay cuatro matices que conviene tener en cuenta para no quedarse solo con la mitad.

1. **Las partes son contextos, no entidades.** "Pagos" y "Gestión de viajes" son **bounded contexts**. Las **entidades** (`Trip`, `Booking`) viven *dentro* de cada contexto. Una misma idea, como "Usuario", aparece en varios contextos con un modelo distinto en cada uno. No es una única entidad compartida.

2. **Se divide por significado, no solo por funcionalidad.** La frontera no se pone donde "hace cosas distintas", sino **donde cambia el lenguaje**. Si "viaje" significa algo distinto para Operaciones y para Facturación, ahí hay una frontera. Por eso el **lenguaje ubicuo** es la herramienta para decidir dónde cortar.

3. **Las abstracciones son el medio, no el objetivo.** Lo que da el desacoplamiento es:
   - Comunicar contextos por **IDs y eventos** (`SeatBooked`), no compartiendo objetos ni tablas.
   - **Agregados** que protegen sus reglas dentro de cada contexto.
   - Un **ACL** frente a sistemas externos, como Stripe.
   - Un dominio que **no depende de la infraestructura** (arquitectura hexagonal).

   Meter interfaces y capas sin fronteras bien pensadas solo añade complejidad. El acoplamiento sigue ahí, pero más escondido.

4. **No todas las partes merecen el mismo esfuerzo.** DDD también es **priorizar**:
   - **Core** (por ejemplo, el emparejamiento de viajes): modelado cuidadoso.
   - **Genérico** (pagos, autenticación): comprarlo o integrarlo con un ACL fino, sin modelarlo a fondo.

> **En una frase:** dividir el sistema en contextos con un lenguaje y un modelo propios, comunicarlos con contratos mínimos (IDs y eventos) para que cambiar uno no rompa los demás, y gastar el esfuerzo de diseño solo donde está el valor del negocio.
