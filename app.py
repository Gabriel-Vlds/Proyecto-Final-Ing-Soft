from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db, init_db


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "clave-secreta-proyecto-donaciones"

jwt = JWTManager(app)

init_db()


@app.route("/")
def inicio():
    return jsonify({
        "mensaje": "Sistema de Gestión de Donaciones funcionando"
    })


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()

    nombre = datos.get("nombre")
    correo = datos.get("correo")
    password = datos.get("password")

    if not nombre or not correo or not password:
        return jsonify({
            "mensaje": "Todos los campos son obligatorios"
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_db()

    try:
        connection.execute(
            """
            INSERT INTO usuarios (nombre, correo, password, rol)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, correo, password_hash, "usuario")
        )

        connection.commit()

    except Exception:
        connection.close()

        return jsonify({
            "mensaje": "El correo ya está registrado"
        }), 400

    connection.close()

    return jsonify({
        "mensaje": "Usuario registrado correctamente"
    }), 201


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()

    correo = datos.get("correo")
    password = datos.get("password")

    connection = get_db()

    usuario = connection.execute(
        "SELECT * FROM usuarios WHERE correo = ?",
        (correo,)
    ).fetchone()

    connection.close()

    if not usuario:
        return jsonify({
            "mensaje": "Correo o contraseña incorrectos"
        }), 401

    if not check_password_hash(usuario["password"], password):
        return jsonify({
            "mensaje": "Correo o contraseña incorrectos"
        }), 401

    token = create_access_token(
        identity=str(usuario["id"]),
        additional_claims={
            "rol": usuario["rol"]
        }
    )

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": token,
        "rol": usuario["rol"]
    }), 200

def verificar_admin():
    claims = get_jwt()
    return claims.get("rol") == "administrador"

@app.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()

    connection = get_db()

    usuario = connection.execute(
        """
        SELECT id, nombre, correo, rol
        FROM usuarios
        WHERE id = ?
        """,
        (usuario_id,)
    ).fetchone()

    connection.close()

    if not usuario:
        return jsonify({
            "mensaje": "Usuario no encontrado"
        }), 404

    return jsonify({
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "correo": usuario["correo"],
        "rol": usuario["rol"]
    })

def verificar_admin():
    claims = get_jwt()
    return claims.get("rol") == "administrador"


@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    if not verificar_admin():
        return jsonify({
            "mensaje": "Acceso denegado. Se requiere rol de administrador."
        }), 403

    return jsonify({
        "mensaje": "Bienvenido al panel de administrador"
    }), 200

@app.route("/donaciones", methods=["POST"])
@jwt_required()
def registrar_donacion():
    usuario_id = get_jwt_identity()
    datos = request.get_json()

    tipo = datos.get("tipo")
    cantidad = datos.get("cantidad")
    descripcion = datos.get("descripcion", "")

    if not tipo or not cantidad:
        return jsonify({
            "mensaje": "El tipo y la cantidad son obligatorios"
        }), 400

    connection = get_db()

    connection.execute(
        """
        INSERT INTO donaciones
        (usuario_id, tipo, cantidad, descripcion)
        VALUES (?, ?, ?, ?)
        """,
        (usuario_id, tipo, cantidad, descripcion)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "mensaje": "Donación registrada correctamente"
    }), 201


@app.route("/mis-donaciones", methods=["GET"])
@jwt_required()
def mis_donaciones():
    usuario_id = get_jwt_identity()

    connection = get_db()

    donaciones = connection.execute(
        """
        SELECT id, tipo, cantidad, descripcion
        FROM donaciones
        WHERE usuario_id = ?
        """,
        (usuario_id,)
    ).fetchall()

    connection.close()

    resultado = []

    for donacion in donaciones:
        resultado.append({
            "id": donacion["id"],
            "tipo": donacion["tipo"],
            "cantidad": donacion["cantidad"],
            "descripcion": donacion["descripcion"]
        })

    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)