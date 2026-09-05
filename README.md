# Aplicaciones y Servicios Web — ITM 2026-2

Repositorio del curso de **Aplicaciones y Servicios Web** (ITM 2026-2). Aquí construiremos APIs con **FastAPI**, expondremos recursos con **REST** y persistiremos datos en **PostgreSQL** usando un **ORM** contra **Neon**.

---

## 1. ¿Qué es una API?

Una **API** (*Application Programming Interface*, interfaz de programación de aplicaciones) es un contrato entre dos programas: define **qué se puede pedir**, **cómo se pide** y **qué se responde**.

En la web, una API suele ser un servidor HTTP que:

- recibe una petición (método + URL + cabeceras + cuerpo opcional);
- ejecuta una lógica (validar, consultar una base de datos, calcular);
- devuelve una respuesta (código de estado + JSON, HTML, etc.).

Piensa en un restaurante: el menú es la API. El cliente no entra a la cocina; pide platos con un formato claro y recibe un resultado predecible.

**En este curso**, el “menú” serán rutas como `/estudiantes`. Un frontend, Postman, `curl` u otra app podrán crear, listar, actualizar o borrar estudiantes sin conocer cómo está implementada la base de datos.

---

## 2. ¿Cómo funciona una API web?

El flujo típico es **cliente → HTTP → servidor → (opcional) base de datos → respuesta**.

```mermaid
sequenceDiagram
    participant Cliente
    participant API as FastAPI
    participant ORM as ORM (SQLAlchemy)
    participant BD as Neon PostgreSQL

    Cliente->>API: GET /estudiantes
    API->>ORM: consultar modelos
    ORM->>BD: SELECT ...
    BD-->>ORM: filas
    ORM-->>API: objetos Python
    API-->>Cliente: 200 + JSON
```

1. El cliente arma una petición HTTP (`GET /estudiantes`).
2. FastAPI enruta la URL al *endpoint* correspondiente.
3. El *endpoint* valida datos (Pydantic) y llama al ORM si hace falta persistencia.
4. El ORM traduce objetos Python a SQL y habla con PostgreSQL en Neon.
5. La API responde con un **código HTTP** (`200`, `201`, `404`, `422`…) y un cuerpo, casi siempre JSON.

La API **no es** la base de datos. Es la capa que decide qué operaciones se permiten y cómo se exponen.

---

## 3. Tipos de APIs (y cuándo usarlas)

| Tipo | Idea | Cuándo usarla |
| --- | --- | --- |
| **REST** | Recursos (`/estudiantes/1`) + verbos HTTP | APIs públicas o de curso, CRUD, fácil de cachear y de entender |
| **GraphQL** | El cliente pide exactamente los campos que necesita | Frontends complejos, muchas vistas distintas del mismo dato |
| **RPC / gRPC** | “Llama a una función remota” (Protobuf, HTTP/2) | Microservicios internos, alto rendimiento, tipado fuerte |
| **SOAP / XML** | Contratos WSDL, XML, más rígidos | Integraciones legacy o requisitos empresariales antiguos |
| **WebSockets** | Canal persistente bidireccional | Chat, tableros en vivo, notificaciones en tiempo real |
| **API de librería** | Funciones que importas en el mismo proceso | SDK, paquete Python/JS (no es una API de red) |

También se habla de **API abierta** (documentada para terceros), **API interna** (solo el equipo) y **API de socio** (un conjunto cerrado de clientes).

En este repositorio usamos una **API REST HTTP** porque encaja con el CRUD académico, se prueba fácil y FastAPI la documenta sola.

---

## 4. ¿Cuándo conviene una API?

Usa una API cuando:

- varias aplicaciones (web, móvil, otro backend) deben compartir la **misma lógica y los mismos datos**;
- quieres separar **frontend** y **backend**;
- un tercero (o tus compañeros) debe integrarse sin tocar tu código;
- necesitas reglas centrales: autenticación, validación, auditoría.

No hace falta una API si todo vive en un único script local sin clientes externos. En el curso sí la necesitamos: el servidor es el punto único de verdad y el cliente solo habla HTTP.

---

## 5. ¿Qué es REST y por qué la usaremos?

**REST** (*Representational State Transfer*) es un estilo de diseño para APIs HTTP. No es un protocolo ni una librería: es un conjunto de convenciones.

Principios que aplicaremos:

1. **Recurso, no acción.** La URL nombra *qué* es (`/estudiantes`), no *qué hacer* (`/obtenerEstudiantes`).
2. **Verbo HTTP = operación.** `GET` lee, `POST` crea, `PUT` reemplaza, `DELETE` borra.
3. **Sin estado en el servidor (stateless).** Cada petición lleva lo necesario (token, id, cuerpo). El servidor no “recuerda” el paso anterior de la conversación.
4. **Representación.** El recurso se envía como JSON (u otro formato). El cliente ve una *representación*, no la fila cruda de Postgres.
5. **Códigos de estado honestos.** `201` al crear, `404` si no existe, `422` si el body es inválido.

**Por qué REST en este curso**

- Encaja de forma natural con CRUD sobre estudiantes (y luego otros recursos).
- Es el estilo más usado en la industria para APIs web.
- FastAPI genera documentación interactiva (`/docs`) a partir de las rutas REST.
- Es fácil de probar con el navegador, Postman, Thunder Client o `curl`.
- Neon + ORM nos dan persistencia; REST nos da el contrato público encima de esa persistencia.

REST **no** obliga a usar JSON, pero en la práctica nuestro contrato será JSON.

---

## 6. FastAPI

[FastAPI](https://fastapi.tiangolo.com/) es un framework Python para APIs:

- rutas declarativas (`@app.get`, `@app.post`, …);
- validación y serialización con **Pydantic**;
- documentación automática **OpenAPI** en `/docs` (Swagger UI) y `/redoc`;
- `async` nativo y buen rendimiento;
- tipado que el editor y el runtime entienden.

En este repo el punto de entrada es `main.py`. Ejemplo de la API actual (aún en memoria, sin base de datos):

```python
from fastapi import FastAPI

app = FastAPI(
    title="API de ejemplo",
    description="API de ejemplo para el curso de Aplicaciones y Servicios Web ITM 2026-2",
    version="1.0.0",
)
```

### Cómo levantarla

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

- API: `http://127.0.0.1:8000`
- Documentación interactiva: `http://127.0.0.1:8000/docs`

`main:app` significa: archivo `main.py`, objeto `app`. `--reload` reinicia el servidor al guardar.

---

## 7. ORM + Neon + PostgreSQL

### 7.1 ¿Qué es un ORM?

Un **ORM** (*Object-Relational Mapping*) mapea **tablas** a **clases** y **filas** a **objetos**. En lugar de escribir SQL a mano en cada endpoint, trabajas con modelos Python.

Sin ORM:

```sql
SELECT id, nombre, programa FROM estudiantes WHERE id = '...';
```

Con ORM (idea):

```python
estudiante = session.get(Estudiante, estudiante_id)
```

En FastAPI el ORM más habitual es **SQLAlchemy 2** (a veces con **SQLModel**, que une SQLAlchemy + Pydantic).

El ORM **no reemplaza** entender SQL: lo genera por ti, pero tú diseñas las tablas, las relaciones y las transacciones.

### 7.2 ¿Qué es Neon?

[Neon](https://neon.tech/) es **PostgreSQL en la nube**: creas un proyecto, obtienes una URL de conexión (`postgresql://...`) y te conectas igual que a un Postgres local. Ventajas para el curso:

- no instalas Postgres en cada máquina;
- hay un plan gratuito para prácticas;
- la cadena de conexión se guarda en variables de entorno, no en el código.

### 7.3 Conectarse (patrón que usaremos)

1. Crea un proyecto en Neon y copia la **connection string**.
2. Guárdala en un `.env` (nunca la subas a Git):

```env
DATABASE_URL=postgresql://usuario:clave@ep-xxxxx.neon.tech/neondb?sslmode=require
```

3. Dependencias típicas (cuando integremos persistencia):

```text
sqlalchemy
psycopg[binary]
python-dotenv
```

`psycopg` es el driver de PostgreSQL. Neon exige **SSL** (`sslmode=require`).

4. Motor y sesión SQLAlchemy:

```python
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # evita conexiones muertas en serverless (Neon)
)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
```

5. Modelo = tabla:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(120))
    programa: Mapped[str] = mapped_column(String(120))
```

6. Crear tablas (en desarrollo; más adelante usaremos migraciones):

```python
Base.metadata.create_all(bind=engine)
```

7. El endpoint abre una sesión, hace el trabajo y la cierra:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/estudiantes")
def listar_estudiantes(db: Session = Depends(get_db)):
    return db.query(Estudiante).all()  # o select() en SQLAlchemy 2
```

Flujo: **HTTP → FastAPI → sesión ORM → Neon (Postgres) → JSON**.

Hoy `main.py` guarda estudiantes en una lista en memoria: al reiniciar el servidor se pierden. El ORM + Neon es el paso siguiente para que los datos sobrevivan.

---

## 8. Peticiones HTTP: GET, POST, PUT, DELETE y OPTIONS

REST usa el **método** para decir qué operación aplicar sobre el recurso.

| Método | Uso REST | Idempotente | Cuerpo típico | Código típico |
| --- | --- | --- | --- | --- |
| **GET** | Leer uno o muchos | Sí | No | `200` / `404` |
| **POST** | Crear | No | Sí (JSON) | `201` |
| **PUT** | Reemplazar el recurso completo | Sí | Sí | `200` / `404` |
| **DELETE** | Eliminar | Sí | No | `204` / `404` |
| **OPTIONS** | Preguntar qué métodos admite la ruta (CORS / preflight) | Sí | No | `200` |

**Idempotente:** repetir la misma petición deja el mismo estado. Dos `PUT` iguales no duplican; dos `POST` sí pueden crear dos estudiantes.

### GET — leer

```http
GET /estudiantes
GET /estudiantes/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

En el código actual:

- `GET /` — saludo y enlace a `/docs`
- `GET /sumar?a=2&b=3` — query params
- `GET /estudiantes` — lista
- `GET /estudiantes/{id}` — uno; si no existe, `404`

### POST — crear

```http
POST /estudiantes
Content-Type: application/json

{
  "nombre": "Ana Pérez",
  "programa": "Ingeniería de Sistemas"
}
```

Respuesta esperada: `201` y el objeto con `id` generado.

### PUT — reemplazar

Aún no está en `main.py`; el contrato que usaremos:

```http
PUT /estudiantes/{id}
Content-Type: application/json

{
  "nombre": "Ana Pérez Gómez",
  "programa": "Ingeniería de Software"
}
```

`PUT` envía **todo** el recurso. Si más adelante queremos cambiar solo un campo, usaremos **PATCH**.

### DELETE — borrar

```http
DELETE /estudiantes/{id}
```

Si existe: `204` (sin cuerpo) o `200` con un mensaje. Si no: `404`.

### OPTIONS — descubrir y CORS

El navegador, en peticiones *cross-origin* (otro dominio o puerto), envía primero un **preflight**:

```http
OPTIONS /estudiantes
Origin: http://localhost:5173
Access-Control-Request-Method: POST
```

El servidor responde qué orígenes y métodos permite (`Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`). FastAPI lo resuelve con el middleware CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

Tú rara vez llamas `OPTIONS` a mano; el navegador lo hace. En `/docs` puedes ver los métodos de cada ruta.

### Cómo probarlas

1. **Swagger** (`/docs`): elige la ruta, *Try it out*, ejecuta.
2. **curl** (Windows PowerShell usa `curl.exe` o `Invoke-RestMethod`):

```bash
curl http://127.0.0.1:8000/estudiantes

curl -X POST http://127.0.0.1:8000/estudiantes ^
  -H "Content-Type: application/json" ^
  -d "{\"nombre\": \"Ana Pérez\", \"programa\": \"Sistemas\"}"
```

3. **Postman / Thunder Client:** mismo método, URL y body JSON.

---

## 9. Mapa del repositorio

| Archivo | Rol |
| --- | --- |
| `main.py` | Aplicación FastAPI y rutas de ejemplo (en memoria) |
| `requirements.txt` | Dependencias Python (`fastapi`, `uvicorn`) |
| `README.md` | Esta guía conceptual y de uso |
| [`GUIA-NEON-ORM.md`](GUIA-NEON-ORM.md) | Taller: Neon, ORM, encarpetado por capas y API persistente |
| [`README-PIPELINE.md`](README-PIPELINE.md) | Introducción a CI/CD: GitHub Actions, YAML y el pipeline de PR y merge |

Próximos pasos: sigue la [guía práctica Neon + ORM](GUIA-NEON-ORM.md) para crear la base, conectar SQLAlchemy y montar GET/POST/PUT/DELETE contra PostgreSQL. Después, la [guía de CI/CD](README-PIPELINE.md) automatiza la verificación de cada Pull Request y la carga de datos tras el merge.

---

## 10. Recorrido rápido para el estudiante

1. Entiende la API como **contrato HTTP**, no como la base de datos.
2. Diseña **recursos REST** (`/estudiantes`) y elige el **verbo** correcto.
3. Implementa el contrato en **FastAPI** y valídalo con Pydantic.
4. Persiste con **ORM → Neon (PostgreSQL)** para que los datos no vivan solo en memoria.
5. Prueba **GET / POST / PUT / DELETE** en `/docs`; deja **OPTIONS** para CORS.

Con eso tienes el ciclo completo de una aplicación y un servicio web.
