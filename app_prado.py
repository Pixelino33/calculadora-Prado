import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- INYECCIÓN DE CSS PARA LOS BOTONES Y DISEÑO LIMPIO ---
st.markdown("""
    <style>
    button[data-testid="stepDown"] { transition: all 0.2s ease-in-out; }
    button[data-testid="stepDown"]:hover { background-color: #ff4b4b !important; color: white !important; border-color: #ff4b4b !important; }
    button[data-testid="stepDown"]:focus { background-color: transparent !important; color: inherit !important; }
    button[data-testid="stepDown"]:focus:hover { background-color: #ff4b4b !important; color: white !important; }

    button[data-testid="stepUp"] { transition: all 0.2s ease-in-out; }
    button[data-testid="stepUp"]:hover { background-color: #00cc66 !important; color: white !important; border-color: #00cc66 !important; }
    button[data-testid="stepUp"]:focus { background-color: transparent !important; color: inherit !important; }
    button[data-testid="stepUp"]:focus:hover { background-color: #00cc66 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN PARA TRADUCIR CORTES A BARRAS PARA EL PDF ---
def obtener_texto_compras(lista):
    if not lista: return "-"
    conteo = {}
    for barra in lista:
        t = barra['tamano_comprado']
        conteo[t] = conteo.get(t, 0) + 1
    return " + ".join([f"{c} pz de {t:g}cm" for t, c in sorted(conteo.items(), reverse=True)])

# --- FUNCIÓN PARA EL PDF DESCARGABLE ---
def crear_pdf_prado(ventanas_datos, totales_aluminio, cristales_necesarios):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=10)

    pdf.cell(15, 8, "Cliente:")
    pdf.line(30, pdf.get_y()+6, 110, pdf.get_y()+6)
    pdf.set_x(120)
    pdf.cell(15, 8, "Número:")
    pdf.line(140, pdf.get_y()+6, 195, pdf.get_y()+6)
    pdf.ln(8)

    pdf.cell(15, 8, "Fecha:")
    pdf.line(30, pdf.get_y()+6, 110, pdf.get_y()+6)
    pdf.set_x(120)
    pdf.cell(18, 8, "Dirección:")
    pdf.line(140, pdf.get_y()+6, 195, pdf.get_y()+6)
    pdf.ln(15)

    x_start_1 = 20
    x_start_2 = 115
    y_current = pdf.get_y()

    for i, v in enumerate(ventanas_datos):
        col = i % 2
        x = x_start_1 if col == 0 else x_start_2

        if col == 0 and i > 0:
            y_current += 55

        if y_current > 230:
            pdf.add_page()
            y_current = 20

        pdf.set_text_color(0, 0, 0)
        pdf.text(x, y_current, f"V-{v['num']}")

        pdf.set_draw_color(27, 96, 136)
        pdf.set_line_width(0.8)
        bx, by, bw, bh = x + 10, y_current - 5, 50, 30
        pdf.rect(bx, by, bw, bh)
        pdf.line(bx + bw/2, by, bx + bw/2, by + bh)

        pdf.set_line_width(0.3)
        pdf.line(bx + 5, by + bh/2, bx + bw/2 - 5, by + bh/2)
        pdf.line(bx + bw/2 - 5, by + bh/2, bx + bw/2 - 10, by + bh/2 - 3)
        pdf.line(bx + bw/2 - 5, by + bh/2, bx + bw/2 - 10, by + bh/2 + 3)
        
        pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw - 5, by + bh/2)
        pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw/2 + 10, by + bh/2 - 3)
        pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw/2 + 10, by + bh/2 + 3)

        pdf.set_text_color(255, 0, 0)
        pdf.text(bx + bw/2 - 5, by + bh + 5, f"{v['largo']:.2f}")
        pdf.text(bx + bw + 2, by + 10, f"{v['ancho']:.2f}")

        pdf.set_text_color(32, 115, 172)
        pdf.text(x, by + bh - 2, f"{v['cerco']:.2f}")
        pdf.text(bx + bw + 2, by + bh - 2, f"{v['chambrana_lat']:.2f}")
        pdf.text(bx + bw - 12, by + bh - 2, f"{v['zoclo']:.2f}")

    pdf.set_y(y_current + 45)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(90, 8, "Aluminio:", border=1)
    pdf.cell(90, 8, "Cristal:", border=1)
    pdf.ln()

    pdf.set_font("helvetica", "", 9)
    aluminio_keys = list(totales_aluminio.keys())
    max_rows = max(len(aluminio_keys), len(cristales_necesarios))

    for r in range(max_rows):
        if r < len(aluminio_keys):
            k = aluminio_keys[r]
            val = totales_aluminio[k]
            pdf.cell(25, 6, f"{k}:", border=1)
            pdf.cell(65, 6, f"{val}", border=1, align="R")
        else:
            pdf.cell(90, 6, "", border=1)

        if r < len(cristales_necesarios):
            c = cristales_necesarios[r]
            pdf.cell(20, 6, f"{c['descripcion']}", border=1)
            pdf.cell(70, 6, f"{c['largo']:.2f} X {c['ancho']:.2f}", border=1, align="C")
        else:
            pdf.cell(90, 6, "", border=1)
        pdf.ln()

    return bytes(pdf.output())

# --- FUNCIÓN PARA EL DIBUJO EN PANTALLA ---
def generar_dibujo_ventana(num, largo, ancho, cerco, chambrana_lat, zoclo):
    svg = (
        f'<div style="display: flex; justify-content: center; margin-bottom: 10px;">'
        f'<svg viewBox="0 0 350 180" width="100%" max-width="350px" xmlns="http://www.w3.org/2000/svg">'
        f'<text x="10" y="20" font-family="Arial" font-size="14" fill="black">V-{num}</text>'
        f'<rect x="50" y="30" width="200" height="110" fill="none" stroke="#1b6088" stroke-width="3"/>'
        f'<line x1="150" y1="30" x2="150" y2="140" stroke="#1b6088" stroke-width="2"/>'
        f'<line x1="80" y1="85" x2="120" y2="85" stroke="#1b6088" stroke-width="2"/>'
        f'<polyline points="110,75 120,85 110,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
        f'<line x1="180" y1="85" x2="220" y2="85" stroke="#1b6088" stroke-width="2"/>'
        f'<polyline points="190,75 180,85 190,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
        f'<text x="150" y="160" fill="red" font-family="Arial" font-size="14" text-anchor="middle">{largo:.2f}</text>'
        f'<text x="45" y="90" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">{cerco:.2f}</text>'
        f'<text x="260" y="75" fill="red" font-family="Arial" font-size="14">{ancho:.2f}</text>'
        f'<text x="260" y="95" fill="#2073ac" font-family="Arial" font-size="14">{chambrana_lat:.2f}</text>'
        f'<text x="245" y="135" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">{zoclo:.2f}</text>'
        f'</svg></div>'
    )
    return svg
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
    if not lista: return
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

# --- INTERFAZ PRINCIPAL ---
st.set_page_config(page_title="Calculadora de Materiales", layout="centered", page_icon="🪟")

st.title("Calculadora de Materiales")
st.write("**Tipo de Ventana:** Corrediza")

# La cantidad de ventanas se queda en 1 por default para que siempre muestre al menos una caja
num_ventanas = st.number_input("Cantidad de ventanas a armar:", min_value=1, max_value=50, value=1, step=1)

cortes_chambranas = []
cortes_rieles = []
cortes_adaptadores = []
cortes_cercos = []
cortes_traslapes = []
cortes_zoclos = []
cortes_cabezales = []
cristales_necesarios = [] 
ventanas_pdf = []

st.write("---")

for i in range(1, num_ventanas + 1):
    st.markdown(f"### Ventana {i}")
    
    col_medidas, col_dibujo = st.columns([1, 1])
    
    with col_medidas:
        # Aquí está la magia: value=None hace que arranquen totalmente vacías
        largo = st.number_input(f"Largo total (cm) - V{i}", min_value=0.0, value=None, step=0.1, format="%.1f", key=f"largo_{i}", placeholder="Ej. 120.0")
        ancho = st.number_input(f"Ancho total (cm) - V{i}", min_value=0.0, value=None, step=0.1, format="%.1f", key=f"ancho_{i}", placeholder="Ej. 100.0")

    # Solo hacemos los cálculos si Prado ya tecleó ambos números
    if largo is not None and ancho is not None and largo > 0 and ancho > 0:
        ancho_lados = ancho - 2.7
        medida_adaptador = largo - 6.5
        ancho_cerco = ancho - 4.0
        medida_zc = (largo - 16.5) / 2.0
        largo_cristal = medida_zc + 1.5
        ancho_cristal = ancho_cerco - 9.5

        cortes_chambranas.append({'medida': largo, 'descripcion': f"V{i} (Arriba)"})
        cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Izq)"})
        cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Der)"})
        cortes_rieles.append({'medida': largo, 'descripcion': f"V{i} (Riel Abajo)"})
        cortes_adaptadores.append({'medida': medida_adaptador, 'descripcion': f"V{i} (Adaptador Abajo)"})
        cortes_cercos.extend([{'medida': ancho_cerco, 'descripcion': f"V{i} (Cerco 1)"}, {'medida': ancho_cerco, 'descripcion': f"V{i} (Cerco 2)"}])
        cortes_traslapes.extend([{'medida': ancho_cerco, 'descripcion': f"V{i} (Traslape 1)"}, {'medida': ancho_cerco, 'descripcion': f"V{i} (Traslape 2)"}])
        cortes_zoclos.extend([{'medida': medida_zc, 'descripcion': f"V{i} (Zoclo 1)"}, {'medida': medida_zc, 'descripcion': f"V{i} (Zoclo 2)"}])
        cortes_cabezales.extend([{'medida': medida_zc, 'descripcion': f"V{i} (Cabezal 1)"}, {'medida': medida_zc, 'descripcion': f"V{i} (Cabezal 2)"}])
        cristales_necesarios.append({'largo': largo_cristal, 'ancho': ancho_cristal, 'descripcion': f"V-{i}"})

        ventanas_pdf.append({'num': i, 'largo': largo, 'ancho': ancho, 'cerco': ancho_cerco, 'chambrana_lat': ancho_lados, 'zoclo': medida_zc})

        with col_dibujo:
            dibujo = generar_dibujo_ventana(i, largo, ancho, ancho_cerco, ancho_lados, medida_zc)
            st.markdown(dibujo, unsafe_allow_html=True)
            
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

    totales_aluminio = {
        "Chambrana": obtener_texto_compras(chambranas),
        "Riel": obtener_texto_compras(rieles),
        "Adaptador": obtener_texto_compras(adaptadores),
        "Cerco": obtener_texto_compras(cercos),
        "Traslape": obtener_texto_compras(traslapes),
        "Zoclo": obtener_texto_compras(zoclos),
        "Cabezal": obtener_texto_compras(cabezales),
    }

    # --- AQUÍ ARMAMOS EL NOMBRE CON LA FECHA DE HOY ---
    fecha_hoy = datetime.now().strftime("%d-%m-%Y")
    nombre_archivo_pdf = f"Presupuesto_{fecha_hoy}.pdf"

    pdf_bytes = crear_pdf_prado(ventanas_pdf, totales_aluminio, cristales_necesarios)
    
    st.download_button(
        label="📄 Descargar Hoja de Presupuesto (PDF)",
        data=pdf_bytes,
        file_name=nombre_archivo_pdf,
        mime="application/pdf"
    )

    st.header("📋 Resultados de la compra")
    mostrar_resultados_ui(chambranas, "Chambranas")
    mostrar_resultados_ui(rieles, "Rieles")
    mostrar_resultados_ui(adaptadores, "Adaptadores")
    mostrar_resultados_ui(cercos, "Cercos")
    mostrar_resultados_ui(traslapes, "Traslapes")
    mostrar_resultados_ui(zoclos, "Zoclos")
    mostrar_resultados_ui(cabezales, "Cabezales")

    if cristales_necesarios:
        st.subheader("🛒 CRISTALES")
        for cristal in cristales_necesarios:
            st.info(f"**2 piezas** de {cristal['largo']:.2f} cm (Largo) x {cristal['ancho']:.2f} cm (Ancho) ➔ {cristal['descripcion']}")