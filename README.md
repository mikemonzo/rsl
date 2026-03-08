# Artifact Advisor

Aplicación para evaluar qué campeón aprovecha mejor los artefactos nuevos en **RSL**, usando una heurística basada en rol, substats, main stat, sets preferidos y comparación contra el artefacto actualmente equipado en el mismo slot.

## Funcionalidades

- Carga de datos de campeones y artefactos desde CSV.
- Carga manual de campeones y artefactos desde CLI.
- Edicion manual parcial de campeones y artefactos desde CLI.
- Persistencia en SQLite o PostgreSQL usando SQLModel.
- Recomendación de artefactos nuevos (`is_new=true`) por campeón.
- Comparación `nuevo` vs `actual` por slot con cálculo de mejora (`delta`).
- CLI con Typer para inicializar base de datos, sincronizar datos y generar recomendaciones.
- Arquitectura refactorizada con enfoque DDD (Domain, Application, Infrastructure, Interfaces).

## Estructura del proyecto

- `rsl.py`: punto de entrada de la CLI.
- `advisor/domain/`: entidades y lógica de negocio (scoring).
- `advisor/application/`: casos de uso.
- `advisor/infrastructure/`: CSV y persistencia SQLModel/SQLite.
- `advisor/interfaces/`: capa CLI (Typer).
- `tests/`: pruebas unitarias y de aplicación.

## Requisitos

- Python 3.9+
- Entorno virtual recomendado
- Docker + Docker Compose (modo contenedores)

## Instalación

1. Crear entorno virtual:

```bash
python3 -m venv .venv
```

2. Activar entorno virtual:

```bash
source .venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. (Opcional) Instalar dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
```

## Uso de la aplicación

### 1) Inicializar base de datos

```bash
.venv/bin/python rsl.py init-db --db advisor.db
```

### 2) Sincronizar CSV -> SQLite

```bash
.venv/bin/python rsl.py sync \
  --champions-csv champions.csv \
  --artifacts-csv artifacts.csv \
  --db advisor.db
```

### 3) Generar recomendaciones desde base de datos

```bash
.venv/bin/python rsl.py recommend --source db --db advisor.db
```

### 4) Generar recomendaciones directamente desde CSV

```bash
.venv/bin/python rsl.py recommend \
  --source csv \
  --champions-csv champions.csv \
  --artifacts-csv artifacts.csv
```

### 5) Sincronizar y recomendar en un solo comando

```bash
.venv/bin/python rsl.py recommend \
  --source db \
  --sync-csv \
  --champions-csv champions.csv \
  --artifacts-csv artifacts.csv \
  --db advisor.db
```

### 6) Alta manual de campeones por CLI

```bash
.venv/bin/python rsl.py add-champion \
  --champion-id "kael-01" \
  --name "Kael" \
  --rarity "Rare" \
  --role "DPS / Farmer" \
  --level 60 \
  --stars 6 \
  --hp 24324 \
  --atk 2966 \
  --defense 1451 \
  --speed 146 \
  --crit-rate 93 \
  --crit-damage 145 \
  --resistance 90 \
  --accuracy 47 \
  --preferred-sets "Lethal|Cruel" \
  --notes "Farmer principal" \
  --db advisor.db
```

### 7) Alta manual de artefactos por CLI

```bash
.venv/bin/python rsl.py add-artifact \
  --artifact-id "N1001" \
  --name "Guantes letales nuevos" \
  --set-name "Lethal" \
  --slot "gloves" \
  --rank 6 \
  --level 16 \
  --rarity "Epic" \
  --main-stat "C.RATE" \
  --main-value 60 \
  --substats "C.DMG:20|ATK%:15|SPD:8" \
  --is-new \
  --db advisor.db
```

### 8) Edicion manual de campeones por CLI

```bash
.venv/bin/python rsl.py edit-champion \
  --champion-id "kael-01" \
  --level 60 \
  --speed 175 \
  --preferred-sets "Lethal|Cruel|Perception" \
  --notes "Actualizado para arena" \
  --db advisor.db
```

### 9) Edicion manual de artefactos por CLI

```bash
.venv/bin/python rsl.py edit-artifact \
  --artifact-id "N1001" \
  --main-value 65 \
  --substats "C.DMG:22|ATK%:16|SPD:9" \
  --is-new true \
  --equipped-by "" \
  --db advisor.db
```

### 10) Consulta de campeones desde SQLite

```bash
.venv/bin/python rsl.py list-champions \
  --champion-id "kael" \
  --role "DPS" \
  --rarity "Rare" \
  --db advisor.db
```

### 11) Consulta de artefactos desde SQLite

```bash
.venv/bin/python rsl.py list-artifacts \
  --slot "boots" \
  --set-name "Perception" \
  --is-new true \
  --db advisor.db
```

### Opciones útiles

- `--top-n`: cantidad de campeones a mostrar por artefacto.
- `--db`: ruta del archivo SQLite o `DATABASE_URL` (ejemplo PostgreSQL).
- `--source`: origen de datos (`db` o `csv`).
- `list-champions`: filtros por `--champion-id`, `--name-contains`, `--role`, `--rarity`.
- `list-artifacts`: filtros por `--artifact-id`, `--slot`, `--set-name`, `--equipped-by`, `--is-new`.

## Modo contenedores (multi-servicio)

El proyecto incluye `docker-compose.yml` con 3 servicios:

- `db`: PostgreSQL (ligero con imagen `postgres:alpine`).
- `controller`: backend actual (CLI Typer + lógica DDD).
- `view`: placeholder frontend en `nginx` (se desarrollará más adelante).

Archivos clave:

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `view/index.html`

### Levantar servicios

```bash
docker compose up -d --build
```

### Ejecutar comandos del backend dentro del contenedor `controller`

```bash
docker compose exec controller python rsl.py init-db
docker compose exec controller python rsl.py sync --champions-csv champions.csv --artifacts-csv artifacts.csv
docker compose exec controller python rsl.py recommend --source db
```

`controller` usa por defecto:

```text
DATABASE_URL=postgresql+psycopg://rsl:rsl@db:5432/rsl_advisor
```

### Frontend placeholder

- URL: `http://localhost:8080`
- Actualmente muestra una página de placeholder.

## Formato de entrada CSV

### champions.csv

Columnas esperadas:

- `champion_id, name, rarity, role, level, stars, hp, atk, defense, speed, crit_rate, crit_damage, resistance, accuracy, preferred_sets, notes`

`preferred_sets` usa separador `|`.

Ejemplo:

```csv
champion_id,name,rarity,role,level,stars,hp,atk,defense,speed,crit_rate,crit_damage,resistance,accuracy,preferred_sets,notes
kael-01,Kael,Rare,DPS / Farmer,60,6,24324,2966,1451,146,93,145,90,47,Lethal|Cruel,Farmer y daño general
```

### artifacts.csv

Columnas esperadas:

- `artifact_id, name, set_name, slot, rank, level, rarity, main_stat, main_value, substats, equipped_by, is_new`
- `equipped_by` debe contener `champion_id` (no nombre).

`substats` usa formato `STAT:valor|STAT:valor`.

Ejemplo:

```csv
artifact_id,name,set_name,slot,rank,level,rarity,main_stat,main_value,substats,equipped_by,is_new
N001,Nuevas botas percepción,Perception,boots,6,16,Epic,SPD,45,"ACC:32|HP%:10|DEF%:12",kael-01,true
```

## Cómo funciona el scoring

Para cada artefacto nuevo:

1. Calcula score del artefacto para cada campeón (pesos por rol).
2. Busca artefacto actual del campeón en el mismo slot.
3. Calcula `delta = score_nuevo - score_actual`.
4. Ordena por mejor mejora (`delta`) y score final.

La heurística tiene en cuenta:

- Pesos por rol (`ROLE_WEIGHTS`)
- Penalizaciones por stats poco útiles (`ANTI_WEIGHTS`)
- Main stats preferidos por slot/rol
- Bonus por set preferido
- Bonus contextual para ACC/SPD según stats base del campeón

## Pruebas

Ejecutar tests:

```bash
.venv/bin/python -m pytest tests -q
```

Actualmente incluye pruebas para:

- Parsing de substats
- Ranking de recomendaciones
- Sincronización CSV -> DB
- Construcción de recomendaciones para artefactos nuevos

## Limitaciones actuales

- Heurística configurable, no optimizador exhaustivo de builds.
- No contempla restricciones avanzadas de speed tuning o sinergias de set complejas.
- No incluye interfaz web (solo CLI).

## Roadmap sugerido

- Exportar recomendaciones a JSON/CSV.
- Añadir tests de CLI con `CliRunner`.
- Añadir endpoint API (FastAPI) para integrar con frontend.
- Introducir migraciones formales de base de datos.
