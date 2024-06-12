from flask import Flask, render_template, request
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pip

try:
    import psycopg2
except ImportError:
    pip.main(['install', 'psycopg2-binary'])
    import psycopg2

app = Flask(__name__)

# Conectar a la base de datos PostgreSQL
connection = psycopg2.connect(
    host="localhost",
    database="Computadoras",
    user="postgres",
    password="271115"
)

cursor = connection.cursor()

# Leer datos de entrenamiento desde la base de datos
cursor.execute("SELECT modelo, procesador, ram, gpu, precio FROM datos_entrenamiento")
datos_entrenamiento = cursor.fetchall()

# Convertir las categorías a valores numéricos
label_encoder_modelo = LabelEncoder()
label_encoder_procesador = LabelEncoder()
label_encoder_gpu = LabelEncoder()

# Ajustar con todos los datos de entrenamiento
label_encoder_modelo.fit([x[0] for x in datos_entrenamiento])
label_encoder_procesador.fit([x[1] for x in datos_entrenamiento])
label_encoder_gpu.fit([x[3] for x in datos_entrenamiento])

# Convertir las categorías a valores numéricos
X_train = np.array([
    [label_encoder_procesador.transform([x[1]])[0], x[2], label_encoder_gpu.transform([x[3]])[0], x[4]]
    for x in datos_entrenamiento
])
y_train = np.array([label_encoder_modelo.transform([x[0]])[0] for x in datos_entrenamiento])

# Crear e entrenar la SVM con kernel lineal
svm_modelo = SVC(kernel='linear', C=1.0)
svm_modelo.fit(X_train, y_train)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def recomendar():
    procesador_usuario = request.form['procesador']
    ram_usuario = int(request.form['ram'])
    gpu_usuario = request.form['gpu']
    presupuesto_usuario = int(request.form['presupuesto'])

    # Realizar la predicción con la SVM
    try:
        procesador_num = label_encoder_procesador.transform([procesador_usuario])[0]
        gpu_num = label_encoder_gpu.transform([gpu_usuario])[0]
    except ValueError:
        procesador_num = len(label_encoder_procesador.classes_)
        label_encoder_procesador.classes_ = np.append(label_encoder_procesador.classes_, procesador_usuario)
        gpu_num = len(label_encoder_gpu.classes_)
        label_encoder_gpu.classes_ = np.append(label_encoder_gpu.classes_, gpu_usuario)

    modelo_predicho = svm_modelo.decision_function([[procesador_num, ram_usuario, gpu_num, presupuesto_usuario]])

    # Obtener los índices de los modelos ordenados por su puntaje
    indices_top_n = np.argsort(modelo_predicho[0])[-3:][::-1]

    # Obtener los modelos correspondientes a los índices
    modelos_top_n = label_encoder_modelo.inverse_transform(indices_top_n)

    # Obtener las características de los modelos predichos desde la base de datos
    caracteristicas_modelos = []
    for modelo in modelos_top_n:
        cursor.execute("SELECT procesador, ram, gpu, precio FROM datos_entrenamiento WHERE modelo = %s", (modelo,))
        caracteristicas_modelo = cursor.fetchone()
        caracteristicas_modelos.append(caracteristicas_modelo)

    # Combinar las listas antes de pasarlas al renderizado de la plantilla
    modelos_y_caracteristicas = list(zip(modelos_top_n, caracteristicas_modelos))

    return render_template('index.html', modelos_y_caracteristicas=modelos_y_caracteristicas)


if __name__ == '__main__':
    app.run(debug=True)
