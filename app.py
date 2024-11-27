from flask import Flask, render_template
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

app = Flask(__name__)

# Configuración de la conexión a MySQL con SQLAlchemy
def get_sqlalchemy_engine():
    return create_engine("mysql+mysqlconnector://root:@localhost/transport_db")

# Obtener datos combinados desde la base de datos
def get_combined_data():
    engine = get_sqlalchemy_engine()

    try:
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
    except Exception as e:
        print(f"Error al combinar datos: {e}")
        raise

# Crear gráfico de área interactivo con Plotly
def create_plotly_area_chart(df):
    try:
        if 'dateTime' not in df.columns:
            raise ValueError("La columna 'date' no existe en el DataFrame.")
        
        fig = px.area(
            df,
            x='dateTime',  # Columna de fechas
            y='travelCost',  # Valor a graficar
            color='transportation_use',  # Agrupar por tipo de transporte
            title='Tendencia de Costos por Tipo de Transporte',
            labels={'date': 'Fecha', 'travelCost': 'Costo de Viaje'},
        )

        # Ajustar el diseño
        fig.update_layout(
            xaxis_title='Fecha',
            yaxis_title='Costo de Viaje',
            template='plotly_white',
        )

        return fig.to_html(full_html=False)
    except Exception as e:
        print(f"Error al crear gráfico de área: {e}")
        raise

# Crear gráfico de barras interactivo con Plotly
def create_plotly_bar_chart(df):
    try:
        fig = px.bar(
            df,
            x='transportation_use',
            color='transportation_use',
            title='Frecuencia por Tipo de Transporte',
            labels={'transportation_use': 'Tipo de Transporte', 'count': 'Frecuencia'},
        )
        fig.update_layout(
            xaxis_title='Tipo de Transporte',
            yaxis_title='Frecuencia',
            template='plotly_white',
            showlegend=False,
        )
        return fig.to_html(full_html=False)
    except Exception as e:
        print(f"Error al crear gráfico de barras: {e}")
        raise

# Crear gráfico de dispersión interactivo con Plotly
def create_plotly_scatter(df):
    try:
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
    except Exception as e:
        print(f"Error al crear gráfico de dispersión: {e}")
        raise

# Crear gráfico de pastel interactivo con Plotly
def create_plotly_pie(df):
    try:
        fig = px.pie(
            df,
            names='transportation_use',
            values='travelCost',
            title='Distribución de Costos por Tipo de Transporte',
            hole=0.3
        )
        return fig.to_html(full_html=False)
    except Exception as e:
        print(f"Error al crear gráfico de pastel: {e}")
        raise

# Rutas de Flask
@app.route('/')
def index():
    try:
        # Obtener datos combinados desde la base de datos
        df = get_combined_data()

        # Crear gráficos
        plotly_area_chart = create_plotly_area_chart(df)
        plotly_bar_chart = create_plotly_bar_chart(df)
        plotly_scatter = create_plotly_scatter(df)
        plotly_pie = create_plotly_pie(df)

        return render_template(
            'index.html',
            plotly_area_chart=plotly_area_chart,
            plotly_bar_chart=plotly_bar_chart,
            plotly_scatter=plotly_scatter,
            plotly_pie=plotly_pie
        )
    except Exception as e:
        return f"Error al procesar la solicitud: {e}"

if __name__ == "__main__":
    app.run(debug=True)
