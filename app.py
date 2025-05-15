from flask import Flask, render_template, redirect, url_for, request, session
import uuid
from uuid6 import uuid7
from faker import Faker
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
fake = Faker()

db = {"v4": [], "v7": []}
person_counter = 1


def generate_person(id_generator):
    global person_counter
    person = {
        "uuid": str(id_generator()),
        "id": person_counter,
        "name": fake.name(),
        "email": fake.email(),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    person_counter += 1
    return person

@app.route("/pessoa/<identifier>")
def view_person(identifier):
    all_people = db["v4"] + db["v7"]
    person = None

    # Tenta buscar por ID inteiro
    if identifier.isdigit():
        person_id = int(identifier)
        person = next((p for p in all_people if p["id"] == person_id), None)
    else:
        # Se não for número, tenta por UUID
        person = next((p for p in all_people if p["uuid"] == identifier), None)

    if not person:
        return f"<h2>Usuário com identificador '{identifier}' não encontrado</h2><a href='/'>Voltar</a>"

    return render_template("person.html", person=person)


@app.route("/")
def index():
    sort_order = request.args.get("sort", "asc")
    last_added = session.get("last_added")

    v4_sorted = sorted(db["v4"], key=lambda x: str(x["uuid"]), reverse=(sort_order == "desc"))
    v7_sorted = sorted(db["v7"], key=lambda x: str(x["uuid"]), reverse=(sort_order == "desc"))

    return render_template(
        "index.html",
        v4=v4_sorted,
        v7=v7_sorted,
        sort_order=sort_order,
        last_added=last_added
    )

@app.route("/clear")
def clear_data():
    db["v4"].clear()
    db["v7"].clear()
    session.pop("last_added", None)
    return redirect(url_for("index"))


@app.route("/add")
def add_person():
    person_v4 = generate_person(lambda: uuid.uuid4())
    person_v7 = generate_person(lambda: uuid7())

    db["v4"].append(person_v4)
    db["v7"].append(person_v7)

    # Armazenar o último adicionado para destaque visual
    session["last_added"] = {
        "v4": person_v4["id"],
        "v7": person_v7["id"]
    }

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
