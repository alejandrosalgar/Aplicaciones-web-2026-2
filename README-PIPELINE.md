# Guía: CI/CD con GitHub Actions

Introducción al **CI/CD** y paso a paso del pipeline que montaremos en este repositorio.

La teoría de APIs está en [`README.md`](README.md) y el taller de base de datos en [`GUIA-NEON-ORM.md`](GUIA-NEON-ORM.md). Esta guía responde a otra pregunta: **¿cómo verificamos automáticamente que lo que se sube al repositorio funciona, y cómo preparamos la base de datos sin entrar a hacerlo a mano?**

---

## 1. ¿Qué es CI/CD?

Son dos prácticas encadenadas.

**CI — Integración Continua** (*Continuous Integration*). Cada vez que alguien propone un cambio, un servidor **descarga el código, lo instala desde cero y lo prueba**. Si algo se rompe, el equipo se entera en minutos y no cuando el proyecto ya está en `main`.

**CD — Entrega / Despliegue Continuo** (*Continuous Delivery / Deployment*). Cuando el cambio se acepta, otro proceso automático se encarga de **llevarlo al ambiente real**: publicar la app, aplicar migraciones de base de datos, cargar datos iniciales.

La diferencia práctica:

| | Cuándo se ejecuta | Qué hace | ¿Modifica algo real? |
| --- | --- | --- | --- |
| **CI** | Al abrir o actualizar un Pull Request | Verifica: instala, importa, prueba, conecta | No, solo revisa |
| **CD** | Al hacer merge a `main` | Aplica: crea tablas, siembra datos, despliega | Sí |

En este curso: el **CI revisa el PR** y el **CD prepara la base de datos en Neon después del merge**.

---

## 2. ¿Por qué se usa?

Sin pipeline, la frase típica es *"en mi máquina sí funciona"*. Con pipeline, el proyecto se construye siempre en una máquina limpia, con las mismas versiones y los mismos pasos.

Lo que ganamos concretamente:

- **Detectar errores temprano.** Un `import` roto o una dependencia que falta en `requirements.txt` aparece en el PR, no cuando un compañero clona el repo.
- **Proteger la rama `main`.** GitHub puede **bloquear el merge** si la verificación falla. `main` deja de ser el lugar donde se descubren los errores.
- **Repetibilidad.** El proceso está escrito en un archivo versionado. No depende de que alguien recuerde ejecutar un comando.
- **Tareas manuales que desaparecen.** Nadie tiene que entrar al SQL Editor de Neon a crear una tabla o insertar los datos de prueba: lo hace el pipeline.
- **Historial.** Cada ejecución queda registrada: quién, cuándo, con qué commit y con qué resultado.

El costo es escribir un par de archivos YAML. La ganancia es que el error lo encuentra la máquina y no la persona que califica.

---

## 3. ¿Qué son los GitHub Actions?

**GitHub Actions** es el sistema de automatización que viene incluido en GitHub. La idea es simple: **"cuando pase X en el repositorio, ejecuta Y en un computador que GitHub me presta"**.

Ese computador prestado se llama **runner**: una máquina virtual limpia (Ubuntu, Windows o macOS) que nace para tu ejecución, corre los comandos y se destruye. No queda nada entre una ejecución y otra, y por eso todo debe estar declarado en el archivo.

### Vocabulario

| Término | Qué es | Ejemplo en nuestro pipeline |
| --- | --- | --- |
| **Workflow** | Un archivo `.yml` con toda la automatización | `ci.yml`, `cd.yml` |
| **Event** (`on`) | El disparador: qué debe pasar para ejecutarlo | Abrir un PR hacia `main` |
| **Job** | Un grupo de pasos que corre en un runner | `verificar` |
| **Step** | Un paso: un comando o una acción reutilizable | `pip install -r requirements.txt` |
| **Action** (`uses`) | Un paso empaquetado que alguien ya escribió | `actions/checkout@v4` |
| **Runner** (`runs-on`) | La máquina virtual donde corre el job | `ubuntu-latest` |
| **Secret** | Un valor sensible guardado cifrado en GitHub | `DATABASE_URL` de Neon |

Los workflows **siempre** viven en la carpeta `.github/workflows/`. Si el archivo está en otro lado, GitHub lo ignora.

### Puntos clave

- Es **gratis** para repositorios públicos (los privados tienen minutos incluidos).
- El runner arranca **vacío**: hay que clonar el repo (`actions/checkout`) e instalar Python (`actions/setup-python`) explícitamente.
- Cada job corre **aislado**. Lo que instalas en un job no existe en otro.
- El resultado se ve en la pestaña **Actions** del repositorio y como un ✅ o ❌ dentro del Pull Request.

---

## 4. ¿Qué es un archivo YAML?

**YAML** (*YAML Ain't Markup Language*, extensión `.yml` o `.yaml`) es un formato para escribir **configuración** de forma legible. No es un lenguaje de programación: no tiene `if` ni ciclos, solo describe datos.

Sirve lo mismo que JSON, pero sin llaves ni comillas por todos lados:

```json
{ "nombre": "CI", "pasos": ["instalar", "probar"] }
```

```yaml
nombre: CI
pasos:
  - instalar
  - probar
```

### Reglas que tienes que respetar

**1. La indentación es la estructura.** Lo que está más a la derecha pertenece a lo de arriba.

```yaml
jobs:
  verificar:
    runs-on: ubuntu-latest
```

`verificar` está dentro de `jobs`, y `runs-on` está dentro de `verificar`.

**2. Solo espacios, nunca tabulaciones.** Un `Tab` rompe el archivo. Usa 2 espacios por nivel.

**3. Clave y valor se separan con `dos puntos + espacio`.**

```yaml
name: CI - Verificar Pull Request
```

**4. Las listas usan guion.**

```yaml
branches:
  - main
  - develop
```

También se puede en línea: `branches: [main, develop]`.

**5. Los comentarios empiezan con `#`.**

**6. Texto de varias líneas con `|`.** Se usa mucho para ejecutar varios comandos:

```yaml
run: |
  python -m venv .venv
  pip install -r requirements.txt
```

**7. Cuidado con `on`, `yes`, `no`.** YAML los interpreta como booleanos. Por eso a veces verás `"on"` entre comillas.

**8. `${{ ... }}` es una expresión de GitHub**, no de YAML. GitHub la reemplaza por su valor antes de ejecutar: `${{ secrets.DATABASE_URL }}` se convierte en la cadena de conexión real.

Si algo falla con un mensaje raro tipo `mapping values are not allowed here`, casi siempre es indentación.

---

## 5. El flujo que haremos

```mermaid
flowchart TD
    A["Rama feature/mi-cambio"] --> B["Abro Pull Request hacia main"]
    B --> C{"CI: ci.yml"}
    C --> D["Instala dependencias"]
    D --> E["Compila el codigo"]
    E --> F["Importa la app FastAPI"]
    F --> G["Prueba la conexion a Neon"]
    G -->|Falla| H["Merge bloqueado - corrijo y hago push"]
    H --> C
    G -->|Pasa| I["Merge a main"]
    I --> J{"CD: cd.yml"}
    J --> K["create_all: crea tablas nuevas"]
    K --> L["Seeder: inserta datos que no existan"]
    L --> M["Base de datos lista"]
```

En palabras:

1. Trabajo en una rama aparte y abro un **Pull Request** hacia `main`.
2. GitHub dispara el workflow de **CI**: monta un runner limpio, instala el proyecto, verifica que el código compile, que la app FastAPI se pueda importar y que la **conexión a la base de datos responda**.
3. Si algo falla, el PR queda marcado en rojo y el merge se bloquea. Corrijo, hago `push` y el CI vuelve a correr solo.
4. Cuando todo está verde, hago **merge**. Ese merge es un `push` a `main`, y eso dispara el workflow de **CD**.
5. El CD ejecuta dos cosas contra Neon: **crear las tablas nuevas** que hayan aparecido en los modelos ORM, y **ejecutar el seeder**, que inserta los datos base **solo si no existen**.

La palabra clave del último paso es **idempotente**: puedo ejecutar el seeder diez veces y la base queda igual que si lo ejecutara una sola vez. No duplica filas.

---

## 6. Paso 1 — Guardar la conexión como Secret

El pipeline necesita la URL de Neon, pero **esa cadena jamás se escribe en el YAML** (el repositorio es público y quedaría en el historial de Git para siempre).

1. En GitHub, entra al repositorio → **Settings**.
2. Menú lateral: **Secrets and variables** → **Actions**.
3. Botón **New repository secret**.
4. Completa:
   - **Name:** `DATABASE_URL`
   - **Secret:** tu cadena de Neon, la misma del `.env`

```text
postgresql://USUARIO:CONTRASEÑA@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require
```

5. **Add secret**.

Desde ese momento el workflow puede leerlo con `${{ secrets.DATABASE_URL }}`. GitHub lo entrega cifrado al runner y **lo oculta en los logs**: si intentas imprimirlo, verás `***`.

> **Recomendación:** crea en Neon un **branch** aparte (por ejemplo `ci`) y usa esa URL para el secret. Así el pipeline no toca la base donde estás trabajando. Neon permite crear branches de la base como si fueran ramas de Git.

> **Nota:** los PR que vienen de un *fork* no reciben secrets, por seguridad. En el curso trabajamos con ramas dentro del mismo repositorio, así que no es problema.

---

## 7. Paso 2 — Script que verifica la conexión

El CI necesita algo concreto que ejecutar para saber si la base responde. Un script pequeño y separado de la API.

### `scripts/verificar_bd.py`

```python
"""Comprueba que la base de datos responda. Lo usa el workflow de CI."""

import sys

from sqlalchemy import text

from src.database.database import engine


def main() -> int:
    try:
        with engine.connect() as conexion:
            version = conexion.execute(text("SELECT version()")).scalar()
    except Exception as error:
        print(f"ERROR: no se pudo conectar a la base de datos -> {error}")
        return 1

    print(f"Conexion correcta. PostgreSQL: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Dos detalles que importan en un pipeline:

- **El código de salida.** `return 0` significa éxito, cualquier otro número significa fallo. GitHub Actions marca el paso en rojo cuando el comando devuelve algo distinto de cero. Por eso usamos `sys.exit()`.
- **No imprimimos la URL.** Solo la versión de PostgreSQL, que confirma que la conexión funcionó sin filtrar credenciales.

Se ejecuta así (desde la raíz del repositorio):

```bash
python -m scripts.verificar_bd
```

Usamos `-m` y no `python scripts/verificar_bd.py` porque `-m` agrega la carpeta actual al `sys.path`, y así el `import src.database.database` encuentra el paquete.

---

## 8. Paso 3 — El seeder

Un **seeder** (de *seed*, semilla) es un script que carga los **datos iniciales** que la aplicación necesita para existir: catálogos, roles, un usuario administrador o, en nuestro caso, unas personas de ejemplo.

La regla es que **debe poder correr muchas veces sin duplicar nada**. Como el CD se ejecuta en cada merge a `main`, el seeder correrá decenas de veces durante el semestre.

### `src/database/seeder.py`

```python
"""Datos iniciales de la base. Se puede ejecutar cuantas veces se quiera."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.database import Base, SessionLocal, engine
from src.entities.personas import Persona

PERSONAS_SEMILLA = [
    {"nombre": "Ana Perez", "programa": "Ingenieria de Sistemas"},
    {"nombre": "Carlos Ramirez", "programa": "Ingenieria de Software"},
    {"nombre": "Laura Gomez", "programa": "Ingenieria Electronica"},
]


def crear_tablas() -> None:
    """Crea las tablas que aun no existen. No modifica las que ya estan."""
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas/creadas.")


def sembrar_personas(db: Session) -> int:
    insertadas = 0

    for datos in PERSONAS_SEMILLA:
        existe = db.scalar(
            select(Persona).where(Persona.nombre == datos["nombre"])
        )
        if existe is not None:
            print(f"Ya existe: {datos['nombre']}")
            continue

        db.add(Persona(**datos))
        insertadas += 1
        print(f"Insertada: {datos['nombre']}")

    db.commit()
    return insertadas


def main() -> None:
    crear_tablas()

    db = SessionLocal()
    try:
        total = sembrar_personas(db)
    finally:
        db.close()

    print(f"Seeder terminado. Filas nuevas: {total}")


if __name__ == "__main__":
    main()
```

Qué hace cada parte:

| Línea | Efecto |
| --- | --- |
| `Base.metadata.create_all(bind=engine)` | Recorre los modelos registrados y ejecuta `CREATE TABLE` **solo para las que no existen** |
| `select(Persona).where(...)` | Pregunta a la base si esa fila ya está |
| `continue` | Si ya existe, no hace nada: **esto es lo que lo vuelve idempotente** |
| `db.add(...)` | Marca la fila como nueva |
| `db.commit()` | Escribe de verdad en Neon |

Importante sobre `create_all`: **crea tablas nuevas, pero no modifica columnas de tablas existentes**. Si le agregas un campo a `Persona`, `create_all` no lo añade a la tabla que ya está en Neon. Para eso existen las **migraciones** (Alembic), que veremos más adelante. Para el curso, `create_all` + seeder alcanza.

Prueba local antes de subirlo:

```bash
python -m src.database.seeder
```

Ejecútalo **dos veces**. La segunda debe imprimir `Ya existe:` en todas las personas y `Filas nuevas: 0`. Si duplica filas, el seeder está mal.

---

## 9. Paso 4 — Workflow de CI (al crear el Pull Request)

### `.github/workflows/ci.yml`

```yaml
name: CI - Verificar Pull Request

# Se dispara al abrir un PR hacia main y en cada push a ese PR
on:
  pull_request:
    branches:
      - main

jobs:
  verificar:
    name: Verificar codigo y conexion a la base de datos
    runs-on: ubuntu-latest

    steps:
      - name: Descargar el codigo del repositorio
        uses: actions/checkout@v4

      - name: Instalar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Verificar que el codigo compile
        run: python -m compileall -q main.py src

      - name: Verificar que la app FastAPI se pueda importar
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python -c "from main import app; print(f'Rutas registradas: {len(app.routes)}')"

      - name: Verificar la conexion a la base de datos
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python -m scripts.verificar_bd
```

Paso por paso:

| Paso | Qué comprueba realmente |
| --- | --- |
| `checkout` | Trae el código del PR al runner. Sin esto la carpeta está vacía |
| `setup-python` | Instala Python 3.11. `cache: pip` guarda las dependencias entre ejecuciones para que sea más rápido |
| `pip install` | Que el `requirements.txt` esté completo y las versiones existan |
| `compileall` | Que no haya errores de sintaxis en ningún archivo |
| Importar la app | Que los imports, los modelos y los routers estén bien enlazados. Si alguien renombró un módulo, falla aquí |
| `verificar_bd` | Que la cadena de conexión funcione y Neon responda |

Sobre `env`: las variables se declaran **por paso**, no globalmente, para que el secret solo esté disponible donde de verdad se necesita. La app lee `DATABASE_URL` gracias a `pydantic-settings` en `src/database/config.py`: en tu máquina la toma del `.env`, y en el runner la toma de la variable de entorno. **El mismo código funciona en los dos lados sin cambios.**

Si algún paso devuelve un código distinto de cero, el job se detiene ahí y el PR queda en ❌.

---

## 10. Paso 5 — Workflow de CD (al hacer merge)

Hacer merge de un PR a `main` es, técnicamente, un **push a `main`**. Ese es nuestro disparador.

### `.github/workflows/cd.yml`

```yaml
name: CD - Migrar y sembrar la base de datos

on:
  push:
    branches:
      - main
  # Permite ejecutarlo a mano desde la pestana Actions
  workflow_dispatch:

# Evita que dos merges seguidos escriban en la base al mismo tiempo
concurrency:
  group: cd-main
  cancel-in-progress: false

jobs:
  migrar-y-sembrar:
    name: Crear tablas nuevas y cargar datos base
    runs-on: ubuntu-latest

    steps:
      - name: Descargar el codigo del repositorio
        uses: actions/checkout@v4

      - name: Instalar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Crear tablas nuevas y ejecutar el seeder
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python -m src.database.seeder
```

Dos bloques nuevos:

- **`workflow_dispatch`** agrega un botón *Run workflow* en la pestaña **Actions**. Sirve para volver a sembrar sin tener que hacer un commit.
- **`concurrency`** garantiza que solo haya una ejecución a la vez con el grupo `cd-main`. Si se mergean dos PR casi simultáneos, el segundo espera en vez de escribir en la base al tiempo que el primero. `cancel-in-progress: false` es intencional: **nunca queremos cancelar a mitad una escritura en la base de datos**.

Al terminar, en el log verás algo como:

```text
Tablas verificadas/creadas.
Insertada: Ana Perez
Ya existe: Carlos Ramirez
Ya existe: Laura Gomez
Seeder terminado. Filas nuevas: 1
```

Y puedes confirmarlo en el SQL Editor de Neon:

```sql
SELECT nombre, programa FROM personas ORDER BY nombre;
```

---

## 11. Paso 6 — Bloquear el merge si el CI falla

Los workflows por sí solos **avisan**, pero no impiden nada. Para que un PR en rojo no se pueda mergear hay que proteger la rama.

1. Repositorio → **Settings** → **Branches** (o **Rules** → **Rulesets** en la interfaz nueva).
2. **Add branch protection rule**.
3. **Branch name pattern:** `main`.
4. Marca **Require a pull request before merging**.
5. Marca **Require status checks to pass before merging**.
6. En el buscador de checks elige **`Verificar codigo y conexion a la base de datos`** (el `name` del job).
7. Guarda.

> El check solo aparece en esa lista **después** de que el workflow haya corrido al menos una vez. Si no lo ves, abre un PR de prueba primero.

Con eso, el botón *Merge* queda deshabilitado hasta que el CI esté en verde.

---

## 12. Estructura final de archivos

```text
Aplicaciones-web-2026-2/
├── .github/
│   └── workflows/
│       ├── ci.yml                  # se dispara al abrir un PR a main
│       └── cd.yml                  # se dispara al hacer merge a main
├── scripts/
│   └── verificar_bd.py             # prueba la conexion (usado por el CI)
├── src/
│   ├── api/personas.py
│   ├── crud/personas.py
│   ├── database/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── seeder.py               # create_all + datos base (usado por el CD)
│   ├── entities/personas.py
│   └── schemas/personas.py
├── main.py
├── requirements.txt
├── README.md
├── GUIA-NEON-ORM.md
└── README-PIPELINE.md              # esta guia
```

---

## 13. Probarlo de punta a punta

```bash
git checkout -b feature/pipeline
git add .github scripts src/database/seeder.py README-PIPELINE.md
git commit -m "Agregar pipeline de CI/CD"
git push -u origin feature/pipeline
```

Luego, en GitHub:

1. **Compare & pull request** → base `main`, compare `feature/pipeline`.
2. Crea el PR y baja hasta la sección de checks. Verás *Some checks haven't completed yet*.
3. Entra a **Details** para leer el log paso a paso mientras corre.
4. Cuando quede en verde, pulsa **Merge pull request**.
5. Ve a la pestaña **Actions**: el workflow de CD debe estar ejecutándose.
6. Abre el SQL Editor de Neon y confirma que la tabla `personas` tiene las filas del seeder.

Para comprobar que el CI **de verdad bloquea**, haz un PR con un error a propósito (por ejemplo, borra una línea de `requirements.txt` o escribe mal un import) y observa el ❌.

---

## 14. Errores frecuentes

| Síntoma | Causa habitual | Qué hacer |
| --- | --- | --- |
| El workflow no aparece en Actions | El archivo no está en `.github/workflows/` o la extensión no es `.yml` | Revisa la ruta exacta y el nombre |
| `Invalid workflow file` | Indentación con tabulaciones o mal alineada | Usa 2 espacios; valida el YAML en el editor |
| `ValidationError: database_url Field required` | El secret no existe o está mal escrito | El nombre debe ser exactamente `DATABASE_URL` |
| `ModuleNotFoundError: No module named 'src'` | Ejecutaste `python scripts/archivo.py` | Usa `python -m scripts.archivo` desde la raíz |
| `password authentication failed` | La URL del secret está incompleta o cortada | Cópiala de nuevo desde **Connect** en Neon |
| `SSL connection required` | Se perdió `?sslmode=require` al pegar | Consérvalo en el secret |
| Timeout en la conexión | El compute de Neon estaba dormido | Vuelve a ejecutar el workflow; `pool_pre_ping=True` ayuda |
| El seeder duplica filas | Falta la consulta de existencia o cambiaste el nombre en `PERSONAS_SEMILLA` | Revisa el `if existe is not None: continue` |
| El check no aparece en branch protection | El workflow nunca ha corrido | Abre un PR de prueba y vuelve a configurarlo |
| Merge permitido con el CI en rojo | Falta la protección de rama | Configura **Require status checks** (sección 11) |

---

## 15. Qué no hacer

- **No escribas la cadena de conexión en el YAML.** Ni "temporalmente": queda en el historial de Git.
- **No apuntes el pipeline a la base de datos de tu tarea.** Usa un branch de Neon dedicado.
- **No pongas `DELETE` ni `DROP` en el seeder.** Un seeder solo agrega lo que falta.
- **No hagas que el CD borre y recree tablas** para "empezar limpio": perderías los datos reales.
- **No uses la URL con `-pooler`** para crear tablas; usa la conexión directa.
- **No ignores un check en rojo.** Si el pipeline molesta, es porque está encontrando algo.

---

## 16. Lista de verificación

- [ ] Secret `DATABASE_URL` creado en **Settings → Secrets and variables → Actions**
- [ ] `scripts/verificar_bd.py` corre local y muestra la versión de PostgreSQL
- [ ] `src/database/seeder.py` corre local **dos veces** sin duplicar filas
- [ ] `.github/workflows/ci.yml` y `.github/workflows/cd.yml` creados
- [ ] PR abierto hacia `main` y el CI en verde
- [ ] Branch protection exigiendo el check del CI
- [ ] Merge hecho y el CD ejecutado sin errores
- [ ] Tabla `personas` con los datos del seeder visible en Neon
- [ ] Un segundo merge no duplica los datos
```
