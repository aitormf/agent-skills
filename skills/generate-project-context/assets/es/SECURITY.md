<!--
PLANTILLA de SECURITY.md (en la raíz o en .github/)
GitHub la muestra en la pestaña "Security" y al abrir issues.
Rellena los <marcadores> y borra estos comentarios.
Si el repositorio es privado e interno, simplifica: canal interno de reporte y política de secretos/IA.
-->

# Política de seguridad

## Versiones con soporte

| Versión | Soporte de seguridad |
|---|---|
| <rama main / última versión x.y> | ✅ |
| < x.y | ❌ |

## Cómo informar de una vulnerabilidad

**No abras un issue, PR ni discusión pública.**

Usa uno de estos canales:

- **GitHub Private Vulnerability Reporting:** pestaña *Security* → *Report a vulnerability* (preferido).
- **Email:** <security@tu-dominio.com> <!-- opcional: clave PGP para cifrar -->

Incluye, si puedes:

- Descripción del problema e impacto.
- Pasos para reproducirlo o prueba de concepto.
- Versión o commit afectado.
- Si ya es público o conocido por terceros.

### Qué puedes esperar

| Paso | Plazo orientativo |
|---|---|
| Acuse de recibo | <2> días laborables |
| Evaluación inicial y severidad | <5> días laborables |
| Corrección o plan de mitigación | Según severidad: crítica < <7> días, alta < <30> días |
| Divulgación coordinada | Tras publicar la corrección, de acuerdo con quien informó |

Reconoceremos tu aportación en el aviso de seguridad, salvo que prefieras anonimato.

## Alcance

**Dentro:** el código de este repositorio y sus dependencias tal y como se usan aquí.
**Fuera:** <servicios de terceros, ingeniería social, DoS volumétrico, informes de escáneres automáticos sin explotación demostrada>.

## Prácticas de seguridad del proyecto

Para quien contribuye (personas y agentes de IA):

- **Secretos:** nunca en el repositorio. Van en `.env` (ignorado por git) o en el gestor de secretos <nombre>. `.env.example` documenta las variables sin valores. **gitleaks** se ejecuta en pre-commit y en CI; no se salta (`--no-verify`).
- **Si se filtra un secreto:** rótalo **inmediatamente** y avisa a <contacto/canal>. Borrarlo del historial no basta.
- **Dependencias:** Dependabot/Renovate avisan de vulnerabilidades; las dependencias nuevas se justifican en la PR. Comprueba que el paquete existe y es el que crees (cuidado con nombres parecidos, *typosquatting*).
- **Análisis estático:** reglas de seguridad de ruff (`S`, equivalentes a bandit) en `scripts/check.sh` y CI.
- **Revisión:** los cambios en <auth, pagos, permisos, criptografía, migraciones> requieren aprobación de <@equipo-seguridad / CODEOWNERS>.

### Agentes de IA

- No se pegan secretos, datos personales ni datos de clientes en herramientas de IA no aprobadas. Herramientas aprobadas: <lista o enlace a la política>.
- Los agentes trabajan con permisos acotados (`.claude/settings.json`) y sin acceso a `.env`; los permisos personales más amplios van en `.claude/settings.local.json` (fuera de git).
- Se evita combinar en un mismo agente las tres capacidades de la *lethal trifecta* (Simon Willison): acceso a datos privados, contenido no fiable y capacidad de comunicarse con el exterior. Revisa esto al añadir servidores MCP (`.mcp.json`, siempre sin credenciales).
- El código generado por IA pasa exactamente las mismas comprobaciones y revisiones que el escrito a mano.
