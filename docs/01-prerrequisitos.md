# Módulo 01 — Prerrequisitos

En este módulo repasas todo lo que necesitas tener listo antes de empezar. Si lo montas por primera vez, reserva unas dos o tres horas para seguir la guía con calma, probar cada paso y no saltarte los checkpoints.

## Qué necesitas

| Recurso | Detalle | Coste |
| --- | --- | --- |
| Tenant de Microsoft Entra ID | Con permiso para crear app registrations (o que un admin te cree una) | Gratis |
| Capacidad de Microsoft Fabric | Trial de 60 días válido — activar desde app.fabric.microsoft.com | Gratis (trial) |
| Organización de Azure DevOps | dev.azure.com, tier gratuito | Gratis |
| Python 3.10+ local (opcional) | Solo para probar fabric-cicd en local (módulo 06) | Gratis |

## Permisos y tenant settings de Fabric

Para seguir esta demo necesitas ser administrador del tenant de Fabric, o bien pedirle a un admin que active los ajustes necesarios antes de empezar. Sin estos permisos algunos pasos simplemente no aparecerán en la interfaz.

En el **Admin portal** de Fabric (`app.fabric.microsoft.com > Settings > Admin portal`) asegúrate de que están habilitados los siguientes ajustes:

- **Users can create Fabric items** — permite crear notebooks, lakehouses, pipelines, etc.
- **Service principals can use Fabric APIs** — imprescindible para el módulo 07, donde el pipeline de ADO se autentica con una service principal para desplegar a Prod.
- **Users can synchronize workspace items with their Git repositories** (sección *Git integration*) — habilita la conexión de workspaces a ramas de Azure Repos.

## Conocimientos previos

Basta con saber Git a nivel básico: crear ramas, hacer un commit, abrir un pull request y hacer merge. No hace falta experiencia previa con la librería fabric-cicd; la guía la introduce paso a paso en el módulo 06.

## ✅ Checkpoint

- [ ] Puedes entrar en app.fabric.microsoft.com y crear un workspace de prueba
- [ ] Tienes una organización de ADO con un proyecto
- [ ] Sabes quién puede tocar los tenant settings si algo falla

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| "Upgrade to a paid version" al crear ítems | Sin capacidad asignada | Activar el trial de Fabric |
| No aparece la opción de Git en el workspace | Tenant setting de Git deshabilitado | Pedir al admin que lo habilite |

➡️ Siguiente: [Módulo 02 — Workspaces](02-workspaces.md)
