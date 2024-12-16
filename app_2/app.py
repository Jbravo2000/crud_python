from flask import Flask, render_template, request, redirect, url_for, flash,send_file
from flask_mysqldb import MySQL
from flask_bootstrap import Bootstrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = '123456'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Ajusta con tu usuario
app.config['MYSQL_PASSWORD'] = ''  # Ajusta con tu contraseña
app.config['MYSQL_DB'] = 'crud_python'

mysql = MySQL(app)
Bootstrap(app)

# Página de login
@app.route('/')
def login():
    return render_template('login.html')

# Verificar login (simple ejemplo)
@app.route('/login', methods=['POST'])
def validate_login():
    username = request.form['username']
    password = request.form['password']
    # Aquí validas contra la base de datos
    if username == 'admin' and password == 'admin':  # Cambio por validación real
        return redirect(url_for('index'))
    else:
        flash('Usuario o contraseña incorrectos.')
        return redirect(url_for('login'))

# Página principal con barra lateral
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/generate_report')
def generate_report():
    # Obtener datos de la base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    usuario = cur.fetchall()
    cur.close()

    # Crear un archivo PDF en memoria
    pdf_buffer = io.BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    pdf.setTitle("Reporte de Usuarios")

    # Título del PDF
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 750, "Reporte de Usuarios")

    # Encabezados de la tabla
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 700, "ID")
    pdf.drawString(100, 700, "Nombre")
    pdf.drawString(300, 700, "Correo Electrónico")
    pdf.drawString(500, 700, "Telefono")

    # Datos de la tabla
    pdf.setFont("Helvetica", 10)
    y_position = 680
    for user in usuario:
        pdf.drawString(50, y_position, str(user[0]))       # ID
        pdf.drawString(100, y_position, user[1])          # Nombre
        pdf.drawString(300, y_position, user[2])          # Email
        pdf.drawString(500, y_position, user[3])          # Telefono
        y_position -= 20

        # Verifica si la página necesita avanzar
        if y_position < 50:
            pdf.showPage()
            y_position = 750

    # Finalizar el PDF
    pdf.save()

    # Preparar el archivo para descargar
    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="reporte_usuarios.pdf",
        mimetype="application/pdf"
    )

# Mostrar usuarios
@app.route('/users')
def usuario():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', usuario=data)

# Página de Ingresar: redirige a la lista de usuarios
@app.route('/ingresar')
def ingresar():
        return redirect(url_for('usuario'))

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        telefono = request.form['telefono']
        try:
            # Guardar en la base de datos
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuario (name, email, telefono) VALUES (%s, %s, %s)", (name, email, telefono))
            mysql.connection.commit()
            cur.close()
            flash('Usuario agregado correctamente.', 'success')
        except Exception as e:
            flash('Error al Agregar el Usuario: ' + str(e), 'danger')
        return redirect(url_for('usuario'))
    else:
        return render_template('add_user.html')


# Página de Actualizar: muestra la lista con la opción de seleccionar un usuario para editar
@app.route('/update_select')
def update():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    usuario = cur.fetchall()
    cur.close()
    return render_template('update_select.html', usuario=usuario)

# Página de Eliminar: muestra la lista con la opción de seleccionar un usuario para eliminar
@app.route('/delete_select')
def delete():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    users = cur.fetchall()
    cur.close()
    return render_template('delete_select.html', users=users)
    
# Reportes
@app.route('/reports')
def reports():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")  # Ejemplo: mostrar todos los usuarios como reporte
    data = cur.fetchall()
    cur.close()
    return render_template('reports.html', usuario=data)

# Ruta para actualizar un usuario
@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':  # Si se envía el formulario
        name = request.form['name']
        email = request.form['email']
        telefono = request.form['telefono']
        cur.execute("""
            UPDATE usuario 
            SET name = %s, email = %s, telefono = %s
            WHERE id = %s
        """, (name, email, telefono, id))
        mysql.connection.commit()
        cur.close()
        flash('Usuario actualizado correctamente.')
        return redirect(url_for('usuario'))

    # Si es GET: cargar datos actuales del usuario
    cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()
    return render_template('update_user.html', user=user)


@app.route('/delete/<int:id>')
def delete_user(id):
    # Eliminar el usuario de la base de datos
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuario WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    # Mensaje de confirmación y redirección
    flash('Usuario eliminado correctamente', 'success')
    return redirect(url_for('usuario'))


if __name__ == '__main__':
    app.run(debug=True)
#pip install reportlab


