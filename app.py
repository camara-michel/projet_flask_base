import pymysql
import os
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen.canvas import Canvas
from datetime import datetime

from reportlab.lib.utils import ImageReader



app = Flask(__name__)
@app.route('/')
def home():
  return render_template("home.html")

@app.route('/about')
def about():
  return render_template("about.html")

@app.route('/contact', methods = ['GET','POST'])
def contact():
  if request.method == 'POST':
    nom = request.form['nom']
    message = request.form['message']
    return f" <h1> Merci {nom}, Votre message a été reçu  </h1>  <p> {message} </p>"
  return render_template("contact.html") 

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        port=3308,
        user='root',
        password='',
        database='flask_pdf',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/filter', methods=['GET', 'POST'])
def filter():
    commandes = []
    if request.method == 'POST':
        try:
          date = request.form['date']
          conn = get_db_connection()
          with conn.cursor() as cursor:
              cursor.execute("SELECT * FROM commandes WHERE date_commande = %s", (date,))
              commandes = cursor.fetchall()
          conn.close()
        except Exception as e:
           return f"❌ Erreur : {e}"
           
    return render_template("filter.html", commandes=commandes)


def add_header_footer(canvas: Canvas, doc):
    canvas.saveState()
    
    entete_path = os.path.join('static', 'entete_2.png')
    canvas.drawImage(ImageReader(entete_path), x=0, y=A4[1] - 100, width=A4[0], height=100)

    # Image du pied de page
    pied_path = os.path.join('static', 'pied_page_2.png')
    canvas.drawImage(ImageReader(pied_path), x=0, y=0, width=A4[0], height=50)

    canvas.restoreState()


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    date = request.form['date']
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM commandes WHERE date_commande = %s", (date,))
        commandes = cursor.fetchall()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    titre = Paragraph(f"<b>Commandes du {date}</b>", styles["Title"])
    elements.append(Spacer(1, 24))
    elements.append(titre)
    elements.append(Spacer(1, 12))

    data = [["Nom du client", "Produit", "Quantité"]]
    for c in commandes:
        data.append([c["nom_client"], c["produit"], str(c["quantite"])])

    table = Table(data, colWidths=[150, 150, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"commandes_{date}.pdf", mimetype='application/pdf')

if __name__== '__main__':
  app.run(debug=True)

