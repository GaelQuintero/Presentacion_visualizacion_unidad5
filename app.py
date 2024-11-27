from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine
import io
import base64

app = Flask(__name__)

# Configuración de la conexión a MySQL con SQLAlchemy
def get_sqlalchemy_engine():
    return create_engine("mysql+mysqlconnector://root:@localhost/transport_db")

# Obtener datos combinados desde la base de datos
def get_combined_data():
    engine = get_sqlalchemy_engine()

    # Consultar las tablas
    routes_query = "SELECT * FROM routes;"
    use_transport_query = "SELECT * FROM use_transport;"

    df_routes = pd.read_sql(routes_query, engine)
    df_use_transport = pd.read_sql(use_transport_query, engine)

    # Combinar las tablas asegurando evitar conflictos de nombres
    df = pd.merge(df_routes, df_use_transport, on="idRoute", how="inner", suffixes=('_routes', '_use'))

    # Verificar las columnas combinadas
    print("Columnas del DataFrame combinado:", df.columns.tolist())

    return df

# Crear gráfico de barras con Matplotlib
def create_matplotlib_plot(df):
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='transportation_use', palette='viridis', order=df['transportation_use'].value_counts().index)
    plt.title('Frecuencia por Tipo de Transporte')
    plt.xlabel('Tipo de Transporte')
    plt.ylabel('Frecuencia')

    # Guardar el gráfico en memoria
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    # Convertir a base64 para incrustar en HTML
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

# Crear gráfico de dispersión interactivo con Plotly
def create_plotly_scatter(df):
    fig = px.scatter(
        df,
        x='travelCost',
        y='distance',
        color='transportation_use',
        size='travelCost',
        hover_data=['nameRoute'],
        title='Relación entre Costo y Distancia por Tipo de Transporte'
    )
    return fig.to_html(full_html=False)

# Crear gráfico de pastel interactivo con Plotly
def create_plotly_pie(df):
    fig = px.pie(
        df,
        names='transportation_use',
        values='travelCost',
        title='Distribución de Costos por Tipo de Transporte',
        hole=0.3  # Para un gráfico de dona, ajusta a 0.3 o menos
    )
    return fig.to_html(full_html=False)

# Rutas de Flask

@app.route("/")
def index():
    try:
        # Obtener datos combinados desde la base de datos
        df = get_combined_data()

        # Crear gráficos
        matplotlib_plot = create_matplotlib_plot(df)
        plotly_scatter = create_plotly_scatter(df)
        plotly_pie = create_plotly_pie(df)

        return render_template("index.html", matplotlib_plot=matplotlib_plot, plotly_scatter=plotly_scatter, plotly_pie=plotly_pie)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
