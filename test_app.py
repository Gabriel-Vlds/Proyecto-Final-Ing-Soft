import pytest
import app
import database


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    database_path = tmp_path / "donaciones_test.db"
    monkeypatch.setattr(database, "DATABASE", str(database_path))
    database.init_db()

    app.app.config["TESTING"] = True
    app.app.config["JWT_SECRET_KEY"] = "test-only-secret-key-at-least-32"

    with app.app.test_client() as cliente:
        for nombre, correo in (
            ("Santiago", "santiago@test.com"),
            ("Administrador", "admin@test.com"),
        ):
            respuesta = cliente.post(
                "/registro",
                json={
                    "nombre": nombre,
                    "correo": correo,
                    "password": "123456",
                },
            )
            assert respuesta.status_code == 201

        connection = database.get_db()
        connection.execute(
            "UPDATE usuarios SET rol = ? WHERE correo = ?",
            ("administrador", "admin@test.com"),
        )
        connection.commit()
        connection.close()

        yield cliente


def obtener_token(cliente, correo="santiago@test.com", password="123456"):
    respuesta = cliente.post(
        "/login",
        json={
            "correo": correo,
            "password": password
        }
    )

    return respuesta.get_json()["token"]


def test_inicio(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200


def test_registro_sin_datos(cliente):
    respuesta = cliente.post(
        "/registro",
        json={}
    )

    assert respuesta.status_code == 400


def test_login_usuario_inexistente(cliente):
    respuesta = cliente.post(
        "/login",
        json={
            "correo": "usuarioquenoexiste@test.com",
            "password": "123456"
        }
    )

    assert respuesta.status_code == 401


def test_login_password_incorrecta(cliente):
    respuesta = cliente.post(
        "/login",
        json={
            "correo": "santiago@test.com",
            "password": "password_incorrecta"
        }
    )

    assert respuesta.status_code == 401


def test_perfil_sin_token(cliente):
    respuesta = cliente.get("/perfil")

    assert respuesta.status_code == 401


def test_perfil_con_token(cliente):
    token = obtener_token(cliente)

    respuesta = cliente.get(
        "/perfil",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 200


def test_admin_sin_token(cliente):
    respuesta = cliente.get("/admin")

    assert respuesta.status_code == 401


def test_admin_como_administrador(cliente):
    token = obtener_token(cliente, correo="admin@test.com")

    respuesta = cliente.get(
        "/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 200


def test_registrar_donacion(cliente):
    token = obtener_token(cliente)

    respuesta = cliente.post(
        "/donaciones",
        json={
            "tipo": "Alimentos",
            "cantidad": 10,
            "descripcion": "Prueba de donación"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 201


def test_registrar_donacion_sin_datos(cliente):
    token = obtener_token(cliente)

    respuesta = cliente.post(
        "/donaciones",
        json={},
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 400


def test_mis_donaciones(cliente):
    token = obtener_token(cliente)

    respuesta = cliente.get(
        "/mis-donaciones",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 200


def test_admin_como_usuario(cliente):
    token = obtener_token(cliente)

    respuesta = cliente.get(
        "/admin",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert respuesta.status_code == 403