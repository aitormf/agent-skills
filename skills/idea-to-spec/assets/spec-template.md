---
status: borrador   # borrador | aprobada | obsoleta. Solo una persona la marca como aprobada.
issue:             # opcional: enlace o ID en el tracker (p. ej. TRIBBU-123)
---

# Nombre de la funcionalidad

## Objetivo
<!-- Qué queremos conseguir. Una o dos frases que resuman la funcionalidad y su propósito. -->

## Problema que resuelve
<!-- Qué dolor existe hoy. Describe la situación actual y por qué es insatisfactoria. No incluir la solución. -->

## Usuarios
<!-- Para quién construimos esto. Define perfiles con rol, nivel técnico y contexto de uso. -->

## User stories
<!-- Qué necesita cada usuario y por qué. Formato: "Como [usuario], quiero [acción] para [beneficio]". -->

## Requisitos funcionales
<!-- Qué debe hacer el sistema. Comportamientos observables y verificables. Formato: "RF-01: El sistema debe..." -->

## Requisitos no funcionales
<!-- Restricciones de calidad: rendimiento, seguridad, accesibilidad, compatibilidad. Formato: "RNF-01: ..." -->

## Casos límite
<!-- Qué pasa en situaciones raras o extremas: datos vacíos, masivos, corruptos, acciones simultáneas. -->

## Criterios de aceptación
<!-- Cómo se verifica que funciona. Formato: "Dado [contexto], cuando [acción], entonces [resultado]". -->

## Alcance
<!-- Hasta dónde llega esta spec. Qué SÍ se incluye. Opcional en tareas pequeñas. -->

## Fuera de alcance
<!-- Qué NO entra aunque parezca relacionado. Importante para agentes AI: no infieren por omisión. -->

## Entidades / Modelo de datos
<!-- Conceptos principales del dominio, atributos clave y relaciones. No es diseño de base de datos. Opcional. -->

## Métricas de éxito
<!-- Cómo sabremos que funciona en el mundo real. Métricas medibles post-lanzamiento. Opcional. -->

## Dependencias
<!-- Sistemas, APIs o funcionalidades que deben existir antes o durante la implementación. Opcional. -->

## Riesgos
<!-- Qué puede salir mal o complicar la implementación. Incertidumbres técnicas o de negocio. Opcional. -->

## Supuestos
<!-- Qué damos por hecho sin haberlo validado. Hacerlos explícitos permite cuestionarlos. Opcional. -->

## Preguntas abiertas
<!-- Qué no sabemos todavía. Es preferible listarlas a inventar la respuesta. Opcional. -->


## Seguridad
<!-- Obligatoria si la funcionalidad toca datos, autenticación o entradas externas. Si no, bórrala. -->
- Datos que maneja y su sensibilidad:
- Quién puede hacer qué (matriz de autorización):
- Entradas no fiables y cómo se validan:
- Tests negativos requeridos (sin auth, otro usuario, entrada maliciosa, límites):
