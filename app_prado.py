import streamlit as st

# --- INYECCIÓN DE CSS PARA LOS BOTONES Y DISEÑO LIMPIO ---
st.markdown("""
    <style>
    /* Botón de MENOS (-) */
    button[data-testid="stepDown"] {
        transition: all 0.2s ease-in-out;
    }
    button[data-testid="stepDown"]:hover {
        background-color: #ff4b4b !important; /* Rojo */
        color: white !important;
        border-color: #ff4b4b !important;
    }
    button[data-testid="stepDown"]:focus {
        background-color: transparent !important;
        color: inherit !important;
    }
    button[data-testid="stepDown"]:focus:hover {
        background-color: #ff4b4b !important;
        color: white !important;
    }

    /* Botón de MÁS (+) */
    button[data-testid="stepUp"] {
        transition: all 0.2s ease-in-out;
    }
    button[data-testid="stepUp"]:hover {
        background-color: #00cc66 !important; /* Verde */
        color: white !important;
        border-color: #00cc66 !important;
    }
    button[data-testid="stepUp"]:focus {
        background-color: transparent !important;
        color: inherit !important;
    }
    button[data-testid="stepUp"]:focus:hover {
        background-color: #00cc66 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------

def empacar_piezas(cortes, tamanos_disponibles):
    cortes.sort(key=lambda x: x['medida'], reverse=True)
    lista_de_compras = []
    tamanos_asc = sorted(tamanos_disponibles)
    largo_maximo = max(tamanos_disponibles)
    
    for pieza in cortes:
        acomodada = False
        for barra in lista_de_compras:
            if barra['espacio_libre'] >= pieza['medida']:
                barra['cortes'].append(pieza)
                barra['espacio_libre'] -= pieza['medida']
                barra['espacio_usado'] += pieza['medida']
                acomodada = True
                break
        
        if not acomodada:
            lista_de_compras.append({
                'tamano_comprado': largo_maximo,
                'espacio_libre': largo_maximo - pieza['medida'],
                'espacio_usado': pieza['medida'],
                'cortes': [pieza]
            })

    for barra in lista_de_compras:
        for tamano in tamanos_asc:
            if barra['espacio_usado'] <= tamano:
                barra['tamano_comprado'] = tamano
                barra['espacio_libre'] = tamano - barra['espacio_usado']
                break

    return lista_de_compras

def mostrar_resultados_ui(lista, nombre_material):
    if not lista:
        return
        
    st.subheader(f"🛒 {nombre_material.upper()}")
    
    conteo_tamanos = {}
    for barra in lista:
        t = barra['tamano_comprado']
        conteo_tamanos[t] = conteo_tamanos.get(t, 0) + 1
        
    for tamano in sorted(conteo_tamanos.keys(), reverse=True):
        st.success(f"**{conteo_tamanos[tamano]} pieza(s)** de {tamano} cm")
    
    with st.expander(f"Ver guía de cortes para {nombre_material}"):
        for i, barra in enumerate(lista, 1):
            st.markdown(f"**Barra {i} (Comprar de {barra['tamano_comprado']} cm):**")
            for corte in barra['cortes']:
                st.write(f"  - {corte['medida']:.2f} cm ➔ {corte['descripcion']}")
        st.divider()

# Aquí empieza la página web
st.set_page_config(page_title="Calculadora de Materiales", layout="centered")

st.title("Calculadora de Materiales")
st.write("**Tipo de Ventana:** Corrediza")

num_ventanas = st.number_input("Cantidad de ventanas a armar:", min_value=1, max_value=50, value=1, step=1)

cortes_chambranas = []
cortes_rieles = []
cortes_adaptadores = []
cortes_cercos = []
cortes_traslapes = []
cortes_zoclos = []
cortes_cabezales = []
cristales_necesarios = [] 

st.write("---")

for i in range(1, num_ventanas + 1):
    st.markdown(f"### Medidas Ventana {i}")
    col1, col2 = st.columns(2)
    
    with col1:
        largo = st.number_input(f"Largo (cm) - V{i}", min_value=0.0, value=100.0, step=0.1, format="%.1f", key=f"largo_{i}")
    with col2:
        ancho = st.number_input(f"Ancho (cm) - V{i}", min_value=0.0, value=100.0, step=0.1, format="%.1f", key=f"ancho_{i}")

    if largo > 0 and ancho > 0:
        # Perfiles de aluminio
        cortes_chambranas.append({'medida': largo, 'descripcion': f"V{i} (Arriba)"})
        ancho_lados = ancho - 2.7
        cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Izq)"})
        cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Der)"})
        
        cortes_rieles.append({'medida': largo, 'descripcion': f"V{i} (Riel Abajo)"})
        
        medida_adaptador = largo - 6.5
        cortes_adaptadores.append({'medida': medida_adaptador, 'descripcion': f"V{i} (Adaptador Abajo)"})
        
        ancho_cerco = ancho - 4.0
        cortes_cercos.extend([{'medida': ancho_cerco, 'descripcion': f"V{i} (Cerco 1)"}, 
                              {'medida': ancho_cerco, 'descripcion': f"V{i} (Cerco 2)"}])
        cortes_traslapes.extend([{'medida': ancho_cerco, 'descripcion': f"V{i} (Traslape 1)"}, 
                                 {'medida': ancho_cerco, 'descripcion': f"V{i} (Traslape 2)"}])
        
        medida_zc = (largo - 16.5) / 2.0
        cortes_zoclos.extend([{'medida': medida_zc, 'descripcion': f"V{i} (Zoclo 1)"}, 
                              {'medida': medida_zc, 'descripcion': f"V{i} (Zoclo 2)"}])
        cortes_cabezales.extend([{'medida': medida_zc, 'descripcion': f"V{i} (Cabezal 1)"}, 
                                 {'medida': medida_zc, 'descripcion': f"V{i} (Cabezal 2)"}])

        # --- CÁLCULO DE CRISTALES ---
        largo_cristal = medida_zc + 1.5
        ancho_cristal = ancho_cerco - 9.5
        cristales_necesarios.append({
            'largo': largo_cristal,
            'ancho': ancho_cristal,
            'descripcion': f"Ventana {i}"
        })

st.write("---")

if st.button("Calcular Material", type="primary", use_container_width=True):
    tamanos_basicos = [610.0, 305.0]
    tamanos_especiales = [610.0, 460.0, 230.0]

    chambranas = empacar_piezas(cortes_chambranas, tamanos_basicos)
    rieles = empacar_piezas(cortes_rieles, tamanos_basicos)
    adaptadores = empacar_piezas(cortes_adaptadores, tamanos_basicos)
    cercos = empacar_piezas(cortes_cercos, tamanos_especiales)
    traslapes = empacar_piezas(cortes_traslapes, tamanos_especiales)
    zoclos = empacar_piezas(cortes_zoclos, tamanos_basicos)
    cabezales = empacar_piezas(cortes_cabezales, tamanos_basicos)

    st.header("📋 Resultados de la compra")
    
    mostrar_resultados_ui(chambranas, "Chambranas")
    mostrar_resultados_ui(rieles, "Rieles")
    mostrar_resultados_ui(adaptadores, "Adaptadores")
    mostrar_resultados_ui(cercos, "Cercos")
    mostrar_resultados_ui(traslapes, "Traslapes")
    mostrar_resultados_ui(zoclos, "Zoclos")
    mostrar_resultados_ui(cabezales, "Cabezales")

    # --- MOSTRAR LOS CRISTALES DIRECTO A COMPRA ---
    if cristales_necesarios:
        st.subheader("🛒 CRISTALES")
        for cristal in cristales_necesarios:
            st.info(f"**2 piezas** de {cristal['largo']:.2f} cm (Largo) x {cristal['ancho']:.2f} cm (Ancho) ➔ {cristal['descripcion']}")