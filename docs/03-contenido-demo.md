# Módulo 03 — Crear el contenido de la demo

En este módulo construyes los seis ítems de Fabric que forman la demo. Créalos en el orden que se indica: el diagrama muestra el flujo de dependencias de izquierda a derecha, desde la configuración hasta los visuales finales:

```
DemoVariables ──▶ DemoPipeline ──▶ DemoNotebook ──▶ DemoLakehouse ──▶ DemoModel ──▶ DemoReport
 (config)         (orquesta)       (escribe)        (dim_customer)    (Direct Lake)  (visuales)
```

DemoVariables alimenta a DemoPipeline con los GUIDs correctos según el entorno. DemoNotebook escribe la tabla `dim_customer` en DemoLakehouse. DemoModel y DemoReport consumen esa tabla.

> Trabaja siempre dentro del workspace **GFD26 - Dev** a lo largo de este módulo.

---

## 1. DemoLakehouse

Desde el workspace **GFD26 - Dev**, haz clic en **+ New item**, desplázate hasta la sección *Data Engineering* y selecciona **Lakehouse**. En el campo de nombre escribe exactamente `DemoLakehouse` — las mayúsculas importan porque el archivo `parameter.yml` referencia `$items.Lakehouse.DemoLakehouse.$id` para resolver el GUID en tiempo de despliegue.

Una vez creado el lakehouse, fíjate en la URL del navegador: tendrá el formato `app.fabric.microsoft.com/groups/<GUID_workspace>/lakehouses/<GUID_lakehouse>`. Copia ese segundo GUID y apúntalo; lo necesitarás al configurar DemoVariables en el paso siguiente.

*(captura pendiente: assets/03-lakehouse-url.png)*

---

## 2. DemoVariables (Variable Library)

Vuelve al workspace, haz clic en **+ New item** y busca **Variable Library** (sección *Data Engineering*). Ponle el nombre `DemoVariables`.

Una vez abierto el editor de la Variable Library, añade las dos variables que usa el pipeline:

1. Haz clic en **+ Add variable**.
   - Nombre: `lakehouse_id` · Tipo: `String` · Valor: el GUID de DemoLakehouse que copiaste en el paso anterior.
2. Repite el proceso para:
   - Nombre: `workspace_id` · Tipo: `String` · Valor: el GUID del workspace **GFD26 - Dev** (lo apuntaste en el módulo 02).
3. Pulsa **Save** antes de continuar; si lo olvidas, el pipeline leerá un valor vacío.

Ahora añade el value set de producción. En la barra superior del editor de la Variable Library, haz clic en **+ Add value set** y llámalo exactamente `Prod`. Dentro del value set sobrescribe las dos variables con los GUIDs del workspace y el lakehouse de **GFD26 - Prod**. Si el lakehouse de Prod aún no existe (lo es la primera vez), deja provisionalmente los mismos valores que en Dev; el módulo 08 explica cómo actualizarlos tras el primer despliegue.

El value set activo en Dev debe quedarse en **Default** (valor por defecto). El archivo `settings.json` del repositorio de referencia confirma esta configuración: `"activeValueSetName": "Default"`.

Puedes comparar la estructura resultante con `../src/workspace/DemoVariables.VariableLibrary/` de este repositorio.

*(captura pendiente: assets/03-variable-library.png)*

---

## 3. DemoNotebook

Desde el workspace, haz clic en **+ New item** y selecciona **Notebook**. Ponle el nombre `DemoNotebook`.

Lo primero que debes hacer es adjuntar DemoLakehouse como lakehouse por defecto; de lo contrario, la instrucción `saveAsTable` fallará sin indicar un destino. En el panel izquierdo del notebook despliega **Lakehouses**, haz clic en **Add** y selecciona **Existing lakehouse**; elige `DemoLakehouse`. Una vez añadido, márcalo como **Set as default**.

Ahora pega el código. El notebook tiene tres celdas; encuéntralas en `../src/workspace/DemoNotebook.Notebook/notebook-content.py`, en los bloques marcados con `# CELL ********************` (ignora las líneas de metadatos al principio del archivo). El contenido de las celdas es el siguiente:

- **Celda 1** — descarga el CSV público de clientes desde el repositorio de ejemplos de Microsoft Fabric y lo convierte en un DataFrame de Spark.
- **Celda 2** — normaliza los nombres de columna a snake_case.
- **Celda 3** — escribe la tabla Delta `dim_customer` en el lakehouse con `saveAsTable`.

Ejecuta el notebook completo con **Run all**. Al finalizar, ve a DemoLakehouse > **Tables** y comprueba que aparece `dim_customer` con filas. Si el recuento de filas es cero o la tabla no aparece, revisa que el lakehouse esté marcado como default antes de ejecutar.

*(captura pendiente: assets/03-notebook-run.png)*

---

## 4. DemoPipeline

Desde el workspace, haz clic en **+ New item** y selecciona **Data pipeline**. Ponle el nombre `DemoPipeline`.

En el lienzo del pipeline, añade una actividad de tipo **Notebook**:

1. Haz clic en **Add activity** > **Notebook**.
2. En la pestaña **Settings** de la actividad, selecciona el workspace **GFD26 - Dev** y elige `DemoNotebook` en el desplegable de notebooks.
3. Ahora parametriza el workspace a través de la variable de librería para que el pipeline funcione en cualquier entorno. En el campo **Workspace**, haz clic en el icono de expresión (la llave `{}`) y escribe:

   ```
   @pipeline().libraryVariables.DemoVariables.workspace_id
   ```

   Esta expresión le indica al pipeline que lea el valor de la variable `workspace_id` de la librería `DemoVariables` en tiempo de ejecución. Cuando fabric-cicd despliega el pipeline en Prod, el value set `Prod` de DemoVariables ya contiene los GUIDs correctos de ese entorno.

4. Guarda el pipeline con **Save**.

Ejecuta el pipeline con **Run** y espera a que la actividad termine con el estado *Succeeded*. Si el estado es *Failed*, abre el detalle de la actividad y comprueba el mensaje de error; los más frecuentes se recogen en la tabla de errores al final de este módulo.

*(captura pendiente: assets/03-pipeline-run.png)*

---

## 5. DemoModel (modelo semántico Direct Lake)

El modelo semántico Direct Lake se crea directamente desde el lakehouse. Abre **DemoLakehouse**, despliega el menú **New semantic model** (esquina superior derecha o desde el menú de tres puntos del lakehouse) y sigue estos pasos:

1. En el diálogo de selección de tablas marca **dim_customer**.
2. En el campo de nombre escribe `DemoModel` y haz clic en **Confirm**.

Fabric crea el modelo y lo abre en el editor de modelos semánticos. Añade al menos una medida para que el informe tenga algo que mostrar:

- Selecciona la tabla `dim_customer` en el panel de campos, haz clic en **New measure** e introduce:

  ```dax
  Total Customers = COUNTROWS(dim_customer)
  ```

- Opcionalmente añade una segunda medida, por ejemplo:

  ```dax
  Clientes únicos = DISTINCTCOUNT(dim_customer[CustomerKey])
  ```

Guarda el modelo.

*(captura pendiente: assets/03-semantic-model.png)*

---

## 6. DemoReport

Con el modelo semántico abierto, haz clic en **New report** en la barra superior. Fabric abre el editor de informes con DemoModel ya conectado.

Construye una página sencilla con dos o tres visualizaciones:

1. **Tarjeta** — arrastra la medida `Total Customers` al lienzo para ver el número total de clientes.
2. **Tabla o gráfico de barras** — arrastra algunas columnas de `dim_customer` (por ejemplo, `GeographyKey` o `CommuteDistance`) para mostrar una distribución básica de los datos.
3. Ajusta títulos y colores si lo deseas; lo importante es que el informe cargue datos reales.

Cuando termines, ve a **File > Save** y guarda el informe con el nombre exacto `DemoReport`. Confirma que el nombre aparece así en la lista de ítems del workspace.

*(captura pendiente: assets/03-report.png)*

---

## ✅ Checkpoint

- [ ] La tabla `dim_customer` existe en DemoLakehouse y tiene filas (visible en la pestaña Tables)
- [ ] El pipeline DemoPipeline ejecuta DemoNotebook sin errores usando la expresión de variable de librería
- [ ] DemoReport se abre y muestra datos de `dim_customer`

---

## Errores típicos

| Síntoma | Causa | Solución |
| --- | --- | --- |
| `saveAsTable` falla con error de lakehouse no encontrado | DemoNotebook no tiene DemoLakehouse como default lakehouse | En el panel de lakehouses del notebook, añade DemoLakehouse y márcalo como default; vuelve a ejecutar |
| El pipeline falla con "Variable library not found" | DemoVariables no se guardó tras añadir las variables | Abre DemoVariables, comprueba que las dos variables tienen valor y pulsa Save; vuelve a ejecutar el pipeline |
| DemoModel no aparece disponible al crear el informe | El modelo aún no se ha guardado o `dim_customer` no tenía filas al crearlo | Ejecuta el notebook, verifica que la tabla tiene filas y vuelve a crear el modelo desde DemoLakehouse |
| La expresión de variable en el pipeline no se evalúa | Se pegó la expresión como texto plano sin activar el modo expresión | Haz clic en el icono `{}` del campo Workspace antes de pegar la expresión |

---

⬅️ [Módulo 02](02-workspaces.md) · ➡️ [Módulo 04 — Git integration](04-git-integration.md)
