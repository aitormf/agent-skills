# Secciones de una spec — Guía detallada

Cada sección de la spec responde a una pregunta concreta. Esta guía explica qué va en cada una, qué NO va, y muestra un ejemplo usando una funcionalidad de "álbumes de fotos por fecha".

---

## Secciones obligatorias

### Objetivo

**Pregunta que responde:** ¿Qué queremos conseguir?

Una o dos frases que resumen la funcionalidad y su propósito. No es una descripción técnica, es una declaración de intención. Si alguien lee solo esta sección, debería entender de qué va la spec.

**Ejemplo:**
> Permitir a los usuarios organizar sus fotos en álbumes agrupados por fecha para facilitar la búsqueda y el recuerdo de momentos.

**No incluir aquí:** detalles técnicos, soluciones propuestas, métricas.

---

### Problema que resuelve

**Pregunta que responde:** ¿Por qué necesitamos esto? ¿Qué dolor existe hoy?

Describe la situación actual y por qué es insatisfactoria. Esto ancla toda la spec: si el problema no está claro, las decisiones posteriores no tienen base.

**Ejemplo:**
> Actualmente las fotos se muestran en una lista plana sin organización. Los usuarios con más de 200 fotos no encuentran lo que buscan y abandonan la app. El 40% de los tickets de soporte piden "alguna forma de ordenar fotos".

**No incluir aquí:** la solución propuesta. Este apartado es solo el dolor.

---

### Usuarios

**Pregunta que responde:** ¿Para quién construimos esto? ¿Qué caracteriza a cada tipo de usuario?

Define los perfiles de usuario relevantes: su rol, su nivel técnico, su contexto de uso y sus necesidades principales. No es una lista de nombres, es una descripción de arquetipos que ayuda a tomar decisiones de diseño.

**Ejemplo:**
> - **Usuario casual:** tiene 50–200 fotos, usa la app desde el móvil, quiere encontrar fotos de un viaje concreto sin esfuerzo.
> - **Usuario intensivo:** tiene 2.000+ fotos, usa la app desde escritorio y móvil, necesita organización avanzada y gestión en lote.
> - **Administrador familiar:** gestiona álbumes compartidos con familiares, necesita control de permisos.

**No incluir aquí:** lo que quiere hacer cada usuario (eso va en User stories).

---

### User stories

**Pregunta que responde:** ¿Qué necesita cada usuario y por qué?

Cada user story conecta un tipo de usuario (de la sección anterior) con una necesidad concreta y el beneficio que obtiene. El formato estándar es:

> Como [tipo de usuario], quiero [acción] para [beneficio].

Las user stories son el puente entre los usuarios (quién) y los requisitos funcionales (qué debe hacer el sistema). Una buena story se puede convertir directamente en uno o más requisitos y criterios de aceptación.

**Ejemplo:**
> - Como **usuario casual**, quiero ver mis fotos agrupadas por mes y año para encontrar rápidamente las fotos de un viaje.
> - Como **usuario intensivo**, quiero mover varias fotos a un álbum de una vez para no tener que hacerlo una por una.
> - Como **administrador familiar**, quiero compartir un álbum con permisos de solo lectura para que mi familia vea las fotos sin poder borrarlas.

**Diferencia con Usuarios:** La sección Usuarios describe quién es cada perfil y qué lo caracteriza. Las User stories describen qué quiere hacer cada uno y por qué. Primero defines los actores, luego sus necesidades.

**No incluir aquí:** cómo se implementa, ni detalles de interfaz.

---

### Requisitos funcionales

**Pregunta que responde:** ¿Qué debe hacer el sistema?

Traduce las user stories a capacidades concretas del sistema, en lenguaje verificable. Cada requisito describe un comportamiento observable. Usa "el sistema debe" para distinguirlo de las stories (que usan "como usuario, quiero").

**Ejemplo:**
> - RF-01: El sistema debe agrupar las fotos automáticamente por mes y año basándose en la fecha EXIF.
> - RF-02: El sistema debe permitir crear álbumes manuales con nombre personalizado.
> - RF-03: El sistema debe permitir mover fotos entre álbumes mediante drag & drop (escritorio) o selección múltiple (móvil).
> - RF-04: El sistema debe permitir compartir un álbum con otros usuarios con permisos de lectura o lectura/escritura.

**Diferencia con User stories:** Las stories dicen "el usuario quiere X para Y". Los requisitos dicen "el sistema debe hacer Z". Una story puede generar varios requisitos.

**No incluir aquí:** requisitos de rendimiento o seguridad (van en no funcionales), ni detalles de implementación.

---

### Requisitos no funcionales

**Pregunta que responde:** ¿Qué restricciones de calidad, rendimiento o seguridad debe cumplir?

Son restricciones transversales que no describen funcionalidad sino cómo de bien debe funcionar. Cubren rendimiento, seguridad, accesibilidad, compatibilidad, etc.

**Ejemplo:**
> - RNF-01: La vista de álbumes debe cargar en menos de 2 segundos con hasta 5.000 fotos.
> - RNF-02: Las miniaturas deben generarse en segundo plano sin bloquear la interfaz.
> - RNF-03: Los álbumes compartidos deben requerir autenticación; no se accede por URL pública.
> - RNF-04: La interfaz debe ser usable en pantallas desde 320px de ancho.

**No incluir aquí:** funcionalidad (va en requisitos funcionales), ni objetivos vagos como "debe ser rápido".

---

### Casos límite

**Pregunta que responde:** ¿Qué pasa en situaciones raras, extremas o inesperadas?

Los casos límite son los escenarios que no están en el flujo principal pero que, si no se contemplan, causan bugs o mala experiencia. Piensa en: datos vacíos, datos masivos, datos corruptos, acciones simultáneas, permisos insuficientes.

**Ejemplo:**
> - ¿Qué pasa si una foto no tiene fecha EXIF? → Se agrupa en "Sin fecha".
> - ¿Qué pasa si el usuario borra un álbum compartido? → Las fotos vuelven a "Sin álbum", los otros usuarios ven un aviso.
> - ¿Qué pasa si se suben 500 fotos de golpe? → Se procesan en cola con barra de progreso.
> - ¿Qué pasa si dos usuarios mueven la misma foto a la vez? → Gana la última escritura, sin error.

**No incluir aquí:** flujos normales ni funcionalidad nueva (eso es un requisito, no un edge case).

---

### Criterios de aceptación

**Pregunta que responde:** ¿Cómo verificamos que esto funciona correctamente?

Son las pruebas concretas que determinan si la funcionalidad está completa. Deben ser comprobables — si no puedes demostrar que se cumple o no, reescríbelo. El formato recomendado es Given/When/Then (Dado/Cuando/Entonces).

**Ejemplo:**
> - Dado un usuario con 300 fotos con fecha EXIF, cuando abre la vista de álbumes, entonces ve las fotos agrupadas por mes y año en orden cronológico descendente.
> - Dado un álbum con 50 fotos, cuando el usuario arrastra 3 fotos a otro álbum, entonces las fotos desaparecen del álbum origen y aparecen en el destino sin recargar la página.
> - Dado un álbum compartido como solo lectura, cuando un invitado intenta borrar una foto, entonces el sistema muestra "No tienes permisos" y la foto no se borra.

**Señal de mal criterio:** "El usuario debe tener una buena experiencia" → no es comprobable.

**Señal de buen criterio:** "Cuando el usuario guarda el formulario con campos válidos, el sistema confirma en menos de 2 segundos" → comprobable y medible.

---

### Seguridad

**Pregunta que responde:** ¿Qué datos toca, quién puede hacer qué y cómo se prueba que nadie más puede?

Obligatoria si la funcionalidad maneja datos personales, autenticación o entradas externas; si no, se borra. El código generado con IA suele compilar y pasar los tests siendo inseguro, y la autorización es lo que peor detectan las herramientas automáticas: solo la cubren tests escritos a propósito. Esta sección es de donde salen esos tests.

**Ejemplo:**
> - Datos: fotos y metadatos de ubicación (sensibles: revelan dónde vive el usuario).
> - Autorización: solo el propietario ve, renombra o borra sus álbumes; los compartidos son de solo lectura para los invitados.
> - Entradas no fiables: nombre del álbum (longitud y caracteres), metadatos EXIF de la foto.
> - Tests negativos: sin sesión → 401; otro usuario pide un álbum ajeno → 404; nombre de 10.000 caracteres → 422.

## Secciones opcionales

Estas secciones añaden valor en features medianas y grandes. En tareas pequeñas o bugs, puedes omitirlas.

### Alcance

**Pregunta que responde:** ¿Hasta dónde llega esta spec?

Define los límites de lo que SÍ se incluye. Es útil cuando la funcionalidad podría interpretarse de forma más amplia de lo que se pretende.

**Ejemplo:**
> Esta spec cubre la organización de fotos en álbumes por fecha y la compartición básica. Incluye la vista de álbumes, la creación/edición/borrado de álbumes, y la compartición con permisos.

---

### Fuera de alcance

**Pregunta que responde:** ¿Qué NO entra aunque parezca relacionado?

Especialmente importante cuando trabajan agentes AI: un agente no puede inferir lo que excluyes por omisión. Si no dices explícitamente que algo no entra, puede implementarlo.

**Ejemplo:**
> - Edición de fotos (recorte, filtros, rotación).
> - Álbumes inteligentes por reconocimiento facial.
> - Sincronización con servicios externos (Google Photos, iCloud).
> - Versión offline.

---

### Entidades / Modelo de datos

**Pregunta que responde:** ¿Qué conceptos maneja el sistema y cómo se relacionan?

Describe las entidades principales del dominio, sus atributos clave y sus relaciones. No es un diseño de base de datos — es un modelo conceptual.

**Ejemplo:**
> - **Foto:** id, url, fecha EXIF, fecha de subida, propietario.
> - **Álbum:** id, nombre, tipo (automático/manual), creador, fecha de creación.
> - **Pertenencia:** una foto puede estar en varios álbumes. Un álbum tiene muchas fotos.
> - **Compartición:** un álbum se comparte con usuarios, cada uno con un nivel de permiso (lectura / lectura+escritura).

---

### Métricas de éxito

**Pregunta que responde:** ¿Cómo sabremos que esto funciona en el mundo real?

Son métricas medibles que validan que la funcionalidad cumple su objetivo después de lanzarla. Se diferencian de los criterios de aceptación en que estos verifican el comportamiento técnico, mientras que las métricas miden el impacto.

**Ejemplo:**
> - El 70% de los usuarios con más de 100 fotos usan la vista de álbumes al menos una vez por semana.
> - Los tickets de soporte relacionados con "encontrar fotos" se reducen un 50% en 3 meses.
> - El tiempo medio para encontrar una foto concreta baja de 45 segundos a 15 segundos.

---

### Dependencias

**Pregunta que responde:** ¿De qué depende esta funcionalidad para poder implementarse?

Sistemas, APIs, servicios o funcionalidades que deben existir antes o durante la implementación.

**Ejemplo:**
> - Servicio de almacenamiento de imágenes (ya existe, v2.3).
> - API de lectura de metadatos EXIF (por implementar, bloqueante).
> - Sistema de autenticación y permisos (ya existe, necesita extensión para permisos por álbum).

---

### Riesgos

**Pregunta que responde:** ¿Qué puede salir mal o complicar la implementación?

Identifica incertidumbres técnicas, de negocio o de uso que podrían afectar al resultado.

**Ejemplo:**
> - El 30% de las fotos subidas desde WhatsApp no tienen fecha EXIF → la agrupación automática puede ser incompleta.
> - El rendimiento de la vista de álbumes con usuarios de 10.000+ fotos no está validado.
> - El sistema de permisos actual no soporta permisos por recurso, solo por rol global → puede requerir refactor.

---

### Supuestos

**Pregunta que responde:** ¿Qué estamos dando por hecho sin haberlo validado?

Son afirmaciones que tratamos como ciertas para avanzar, pero que podrían resultar falsas. Hacerlas explícitas permite cuestionarlas.

**Ejemplo:**
> - Asumimos que la mayoría de fotos tienen fecha EXIF válida.
> - Asumimos que los usuarios entienden el concepto de "álbum" sin necesidad de onboarding.
> - Asumimos que el almacenamiento actual soporta la carga adicional de miniaturas.

---

### Preguntas abiertas

**Pregunta que responde:** ¿Qué no sabemos todavía y necesitamos resolver antes (o durante) la implementación?

Preguntas explícitas que aún no tienen respuesta. Es preferible listarlas a inventar la respuesta. Se resuelven con la persona durante `idea-to-spec` o en la revisión (`review-spec` → `apply-review`). Ver la [guía de SDD](README.md).

**Ejemplo:**
> - ¿Permitimos álbumes vacíos o se crean solo cuando tienen al menos una foto?
> - ¿El orden cronológico por defecto es ascendente o descendente?
> - ¿Qué límite ponemos al nombre del álbum (caracteres, longitud)?
> - ¿Los álbumes automáticos por fecha son editables o solo de lectura?

---

## Resumen visual

```
Obligatorias                          Opcionales
─────────────────────────             ─────────────────────────
Objetivo ................. para qué   Alcance .............. hasta dónde sí
Problema que resuelve .... por qué    Fuera de alcance ..... hasta dónde no
Usuarios ................. para quién Entidades ............ qué conceptos maneja
User stories ............. qué quieren Métricas de éxito .... cómo medir impacto
Requisitos funcionales ... qué hace   Dependencias ......... de qué depende
Requisitos no funcionales  cómo de bien Riesgos ............. qué puede fallar
Casos límite ............. qué pasa si Supuestos ............ qué asumimos
Criterios de aceptación .. cómo se verifica Preguntas abiertas .. qué no sabemos
Seguridad (si toca datos,
  auth o entradas) ....... quién puede qué
```
