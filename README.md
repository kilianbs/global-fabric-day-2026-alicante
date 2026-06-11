# CI/CD en Microsoft Fabric — Global Fabric Day 2026 (Alicante)

Repositorio de la charla **"CI/CD en Microsoft Fabric"** presentada en el Global Fabric Day 2026 (Alicante). Contiene la guía completa para replicar la demo paso a paso, el script de despliegue, los pipelines de Azure DevOps y las definiciones de los ítems del workspace de Fabric.

## El flujo que vas a montar

```
feature/* (branch-out desde Fabric)
    │  PR a dev
    ▼
dev ──Git integration──▶ Workspace Dev
    │
    │  PR de dev a main ──▶ merge dispara el pipeline CD
    ▼
main ──▶ fabric-cicd ──▶ Workspace Prod  (con aprobación manual)
```

## La guía

| # | Módulo | Qué haces |
| --- | --- | --- |
| 01 | [Prerrequisitos](docs/01-prerrequisitos.md) | Cuentas, capacidad, permisos |
| 02 | [Workspaces](docs/02-workspaces.md) | Crear Dev y Prod |
| 03 | [Contenido de la demo](docs/03-contenido-demo.md) | Lakehouse, Variable Library, notebook, pipeline, modelo, informe |
| 04 | [Git integration](docs/04-git-integration.md) | Conectar Dev a ADO, branch-out |
| 05 | [Service principal](docs/05-service-principal.md) | Identidad del pipeline (2 variantes) |
| 06 | [fabric-cicd](docs/06-fabric-cicd.md) | deploy.py, parameter.yml, prueba local |
| 07 | [Pipelines de ADO](docs/07-pipelines-ado.md) | CI + CD con aprobación |
| 08 | [Flujo completo](docs/08-flujo-completo.md) | El guion de la demo end-to-end |

## Qué hay en el repo

| Carpeta | Contenido |
| --- | --- |
| `src/workspace/` | Definiciones de los ítems de Fabric en formato Git (Lakehouse, Notebook, DataPipeline, VariableLibrary) más `parameter.yml` con los parámetros de despliegue por entorno |
| `src/deploy/` | `deploy.py` (orquesta el despliegue con fabric-cicd), `validate.py` (comprobaciones previas al merge) y `requirements.txt` |
| `src/pipelines/` | YAMLs de los pipelines de Azure DevOps: `azure-pipelines-ci.yml` (validación en PR) y `azure-pipelines-cd.yml` (despliegue a Prod tras merge a main) |
| `docs/` | La guía de ocho módulos que cubre toda la configuración de extremo a extremo |
| `assets/` | Capturas de pantalla y recursos gráficos de apoyo |

> `src/` replica la estructura del repositorio de Azure DevOps de la demo; su contenido se copia en la raíz del repo ADO.

## ¿Cuánto cuesta replicarlo?

Nada. Puedes montar toda la demo con el trial de Microsoft Fabric (60 días) y el tier gratuito de Azure DevOps.

## Recursos

- [Documentación de fabric-cicd](https://microsoft.github.io/fabric-cicd/)
- [fabric-cicd en PyPI](https://pypi.org/project/fabric-cicd/)
- [Tutorial oficial de CI/CD con ADO y fabric-cicd — Microsoft Learn](https://learn.microsoft.com/fabric/cicd/tutorial-fabric-cicd-azure-devops)
- [Variable libraries en Microsoft Fabric](https://learn.microsoft.com/fabric/cicd/variable-library/variable-library-overview)
