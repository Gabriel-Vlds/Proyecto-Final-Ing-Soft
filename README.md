# Sistema de Gestion de Donaciones

API REST construida con Flask para registrar usuarios y donaciones. La autenticacion usa tokens JWT y SQLite como base de datos local.

## Requisitos

- Python 3.12 o superior
- pip

## Instalacion y ejecucion

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export JWT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python app.py
```

La API queda disponible en `http://127.0.0.1:5000`. La base `donaciones.db` se crea automaticamente en el directorio desde el que se ejecuta la aplicacion. Define un valor secreto propio para `JWT_SECRET_KEY` en cada entorno; no lo publiques ni reutilices la clave de pruebas.

## Endpoints

- `GET /`: estado del servicio
- `POST /registro`: crea un usuario; requiere `nombre`, `correo` y `password`
- `POST /login`: inicia sesion; requiere `correo` y `password`
- `GET /perfil`: devuelve el perfil del usuario autenticado
- `GET /admin`: acceso restringido al rol `administrador`
- `POST /donaciones`: registra una donacion autenticada; requiere `tipo` y `cantidad`, y acepta `descripcion`
- `GET /mis-donaciones`: lista las donaciones del usuario autenticado

Los endpoints protegidos requieren `Authorization: Bearer <token>`. Los usuarios nuevos reciben el rol `usuario`.

## Pruebas

```bash
python -m pytest -q
```

Las pruebas usan una base SQLite temporal y una clave JWT exclusiva de test; no requieren secretos de GitHub ni modifican la base local.

## Integracion continua

GitHub Actions ejecuta la suite en cada push y pull request hacia el repositorio. El workflow esta en `.github/workflows/tests.yml`.