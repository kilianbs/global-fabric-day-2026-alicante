# Diseño: Repo de la charla "Microsoft Fabric CI/CD" — Global Fabric Day 2026 Alicante

**Fecha:** 2026-06-11
**Estado:** Aprobado

## Objetivo

Repositorio público en GitHub que acompaña la charla sobre CI/CD en Microsoft Fabric. Contiene:

1. Una guía paso a paso en español para que los asistentes repliquen la demo completa por su cuenta.
2. El contenido de la demo: definiciones de ítems de Fabric, script de despliegue con la librería **fabric-cicd**, `parameter.yml` y los YAML de pipeline de Azure DevOps.

La demo real vive en un repo de **Azure DevOps** (dos repos): Fabric Git integration conecta con ADO y los pipelines son de ADO. Este repo de GitHub aloja la guía y una **réplica 1:1** del contenido del repo de ADO para que el asistente lo copie a su propio repo.

## Decisiones clave

| Decisión | Elección |
|---|---|
| Flujo demostrado | Branch-out (feature workspaces) + Dev → Prod |
| Herramienta de despliegue | Librería Python **fabric-cicd** (Microsoft) |
| Plataforma CI/CD | Azure DevOps Pipelines (YAML) |
| Entornos | 2 workspaces: **Dev** y **Prod** (sin Test) |
| Configuración por entorno | **Variable Library** con value sets `Dev` y `Prod` |
| Autenticación | Documentar ambas: SP con secreto y SP federado (Workload Identity) |
| Idioma | Español |
| Repos | Dos: demo real en ADO; este repo GitHub = guía + copia replicable |

## Estructura del repositorio

```
global-fabric-day-2026-alicante/
├── README.md                      # Portada: charla, diagrama del flujo, índice, qué cuesta dinero
├── docs/
│   ├── 01-prerrequisitos.md
│   ├── 02-workspaces.md
│   ├── 03-contenido-demo.md
│   ├── 04-git-integration.md
│   ├── 05-service-principal.md
│   ├── 06-fabric-cicd.md
│   ├── 07-pipelines-ado.md
│   └── 08-flujo-completo.md
├── src/                           # Réplica 1:1 del repo de Azure DevOps
│   ├── workspace/                 # Definiciones de ítems (formato Git de Fabric)
│   │   ├── DemoLakehouse.Lakehouse/
│   │   ├── DemoVariables.VariableLibrary/
│   │   ├── DemoNotebook.Notebook/
│   │   ├── DemoPipeline.DataPipeline/
│   │   ├── DemoModel.SemanticModel/
│   │   └── DemoReport.Report/
│   ├── deploy/
│   │   ├── deploy.py              # Invoca fabric-cicd; acepta --environment
│   │   ├── parameter.yml          # Activa value set por entorno + find/replace residual
│   │   └── requirements.txt
│   └── pipelines/
│       ├── azure-pipelines-ci.yml # Validación en PR (parameter.yml, estructura)
│       └── azure-pipelines-cd.yml # Despliegue a Prod al merge en main
└── assets/                        # Capturas e imágenes de la guía
```

Las definiciones de `src/workspace/` se obtienen exportándolas desde el workspace Dev real (commit con Fabric Git integration en ADO y copia a este repo).

## Contenido de la demo

Escenario simple, sin dependencias externas (CSV público descargable por URL, sin gateways):

- **DemoVariables (Variable Library):** variables (`lakehouse_id`, `workspace_id`, …) con dos value sets: **Dev** y **Prod**. Pieza central del mensaje: la configuración por entorno vive dentro de Fabric, versionada en Git.
- **DemoLakehouse:** lakehouse vacío; el notebook crea las tablas.
- **DemoNotebook:** PySpark (~30 líneas, legible en pantalla) — descarga un CSV público, limpia y escribe una tabla Delta en el lakehouse.
- **DemoPipeline (Data Pipeline):** orquesta el notebook; referencia las variables de la librería (`@pipeline().libraryVariables...`) en vez de IDs hardcodeados.
- **DemoModel (modelo semántico):** Direct Lake sobre la tabla, con medidas DAX básicas.
- **DemoReport:** informe de una página, 2-3 visuales.

**Rol de `parameter.yml`:** activar el value set correcto al desplegar (`activeValueSetName`: Prod) más find/replace residual donde las variables no llegan (p. ej., la conexión del modelo Direct Lake al lakehouse, incrustada por ID en la definición). Mensaje de la charla: *"Variable Library para lo que el runtime resuelve; parameter.yml para lo que va incrustado en las definiciones."*

## Flujo CI/CD

**Ramas:** `feature/*` → `dev` → `main`

```
feature/* (branch-out desde Fabric, opcional)
    │  PR a dev
    ▼
dev ──Git integration──▶ Workspace Dev   (o desarrollo directo en Dev)
    │
    │  PR de dev a main ──▶ merge dispara azure-pipelines-cd.yml
    ▼
main ──▶ fabric-cicd ──▶ Workspace Prod  (aprobación manual opcional en Environment de ADO)
```

1. **Workspace Dev conectado a Git** en la rama `dev`. Desarrollo directo en Dev (commit desde Fabric) o branch-out a `feature/*` con PR de vuelta a `dev`.
2. **PR de `dev` a `main`** = evento de promoción. El merge dispara el pipeline CD.
3. **Pipeline CD (un stage):** instala fabric-cicd, ejecuta `deploy.py --environment Prod` → publica los ítems en el workspace Prod activando el value set Prod. Ligado a un Environment de ADO con aprobación manual (momento destacado de la demo en vivo).
4. **CI en PR hacia `main` (`azure-pipelines-ci.yml`):** ligero — valida `parameter.yml` (utilidad de validación de fabric-cicd) y la coherencia de la estructura. Sin despliegue.

El workspace **Prod no está conectado a Git**: solo recibe despliegues de fabric-cicd.

## Autenticación

La guía documenta las dos variantes; el YAML incluye ambas rutas:

- **SP con secreto:** variables secretas del pipeline (`CLIENT_ID`, `CLIENT_SECRET`, `TENANT_ID`); `deploy.py` usa `ClientSecretCredential`. La más sencilla de replicar.
- **SP federado:** service connection con Workload Identity Federation + tarea `AzureCLI@2`; `deploy.py` usa `AzureCliCredential`. Práctica recomendada, sin secretos.

Requisitos del service principal: rol Admin/Member en el workspace Prod y tenant setting "Service principals can use Fabric APIs" habilitado.

## La guía (módulos de `docs/`)

| Módulo | Contenido |
|---|---|
| 01-prerrequisitos | Capacidad Fabric (trial sirve), org de ADO, permisos Entra ID para app registrations, Python local opcional. Tabla "qué necesitas antes de empezar". |
| 02-workspaces | Crear Dev y Prod, asignar capacidad, convenciones de nombres. |
| 03-contenido-demo | Crear los ítems en Dev (Lakehouse, Variable Library con 2 value sets, Notebook, Data Pipeline, modelo, informe) usando `src/` como referencia. |
| 04-git-integration | Repo en ADO con ramas `dev` y `main`; conectar workspace Dev a `dev`; branch-out y PR a `dev`; políticas de rama en `main`. |
| 05-service-principal | App registration, las dos variantes de auth, permisos en workspace Prod, tenant settings. |
| 06-fabric-cicd | La librería, `deploy.py`, `parameter.yml` (value sets + find/replace), prueba de despliegue en local. |
| 07-pipelines-ado | Los dos YAML, variables/variable groups, Environment con aprobación, service connection federada. |
| 08-flujo-completo | Recorrido end-to-end: cambio en feature → PR a dev → verificar Dev → PR a main → pipeline → aprobar → verlo en el informe de Prod. Guion de la charla y checklist del asistente. |

Cada módulo termina con un bloque **"✅ Checkpoint"** (verificación del paso) y los **errores típicos** de ese paso (tenant setting deshabilitado, SP sin permisos, etc.).

**README.md:** título de la charla, diagrama del flujo completo, tabla de contenidos, y aviso de costes (todo replicable con trial de Fabric y tier gratuito de ADO).

## Fuera de alcance

- Entorno Test intermedio (la demo es Dev → Prod).
- Automatización del sync de Git integration vía API (se menciona como posible, no se implementa).
- Gateways, conexiones a orígenes externos autenticados, despliegue de capacidades/infra.

## Verificación

- La guía se valida replicando la demo de cero en un tenant limpio siguiendo solo los módulos.
- `deploy.py` y `parameter.yml` se prueban primero en local (módulo 06) y luego desde el pipeline (módulo 07).
- El criterio de éxito final es el del módulo 08: un cambio hecho en una rama feature acaba visible en el informe del workspace Prod tras la aprobación del pipeline.
