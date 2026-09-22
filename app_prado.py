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
    
    pdf.ln(25)

    x_start_1 = 25
    x_start_2 = 125
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
        pdf.text(x - 5, y_current, f"V-{v['num']}")
        
        bx, by, bw, bh = x + 10, y_current - 5, 50, 30
        pdf.set_draw_color(27, 96, 136)
        pdf.set_line_width(0.8)
        pdf.rect(bx, by, bw, bh)

        # --- DIBUJO DEPENDIENDO DEL TIPO ---
        if v['tipo'] in ["2 pulgadas, 2 hojas corredizas", "3 pulgadas, 2 hojas corredizas"]:
            pdf.line(bx + bw/2, by, bx + bw/2, by + bh)

            pdf.set_line_width(0.3)
            pdf.line(bx + 5, by + bh/2, bx + bw/2 - 5, by + bh/2)
            pdf.line(bx + bw/2 - 5, by + bh/2, bx + bw/2 - 10, by + bh/2 - 3)
            pdf.line(bx + bw/2 - 5, by + bh/2, bx + bw/2 - 10, by + bh/2 + 3)
            
            pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw - 5, by + bh/2)
            pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw/2 + 10, by + bh/2 - 3)
            pdf.line(bx + bw/2 + 5, by + bh/2, bx + bw/2 + 10, by + bh/2 + 3)

            pdf.set_text_color(255, 0, 0)
            str_largo = f"{v['largo']:.2f}"
            w_largo = pdf.get_string_width(str_largo)
            pdf.text(bx + (bw - w_largo)/2, by + bh + 4.5, str_largo)
            pdf.text(bx + bw + 2, by + bh/2 - 1, f"{v['ancho']:.2f}")

            pdf.set_text_color(32, 115, 172)
            str_cerco = f"{v['cerco']:.2f}"
            w_cerco = pdf.get_string_width(str_cerco)
            pdf.text(bx - w_cerco - 1.5, by + bh/2 + 2, str_cerco)
            pdf.text(bx + bw + 2, by + bh/2 + 3.5, f"{v['chambrana_lat']:.2f}")
            
            str_zoclo = f"{v['zoclo']:.2f}"
            w_zoclo = pdf.get_string_width(str_zoclo)
            pdf.text(bx + bw - w_zoclo - 1.5, by + bh - 2, str_zoclo)

        elif v['tipo'] == "2 pulgadas, 2 hojas corredizas, 1 fija":
            w3 = bw / 3
            pdf.line(bx + w3, by, bx + w3, by + bh)
            pdf.line(bx + w3*2, by, bx + w3*2, by + bh)

            pdf.set_font("helvetica", "B", 11)
            pdf.text(bx + w3/2 - 3, by + bh/2 + 3, "F")
            pdf.set_font("helvetica", "", 10)

            pdf.set_line_width(0.3)
            cx = bx + w3 + w3/2
            pdf.line(cx - 5, by + bh/2, cx + 5, by + bh/2)
            pdf.line(cx + 5, by + bh/2, cx + 2, by + bh/2 - 2)
            pdf.line(cx + 5, by + bh/2, cx + 2, by + bh/2 + 2)
            
            rx = bx + w3*2 + w3/2
            pdf.line(rx + 5, by + bh/2, rx - 5, by + bh/2)
            pdf.line(rx - 5, by + bh/2, rx - 2, by + bh/2 - 2)
            pdf.line(rx - 5, by + bh/2, rx - 2, by + bh/2 + 2)

            pdf.set_text_color(255, 0, 0)
            str_largo = f"{v['largo']:.2f}"
            w_largo = pdf.get_string_width(str_largo)
            pdf.text(bx + (bw - w_largo)/2, by + bh + 4.5, str_largo)
            pdf.text(bx + bw + 2, by + bh/2 - 1, f"{v['ancho']:.2f}")

            pdf.set_text_color(32, 115, 172)
            
            str_cf_lbl = "CF"
            w_cf_lbl = pdf.get_string_width(str_cf_lbl)
            pdf.text(bx - w_cf_lbl - 1.5, by + bh/2 - 1.5, str_cf_lbl)
            
            str_cf_num = f"{v['cerco_fijo']:.2f}"
            w_cf_num = pdf.get_string_width(str_cf_num)
            pdf.text(bx - w_cf_num - 1.5, by + bh/2 + 3.5, str_cf_num)

            str_cc = f"CC {v['cerco_corr']:.2f}"
            w_cc = pdf.get_string_width(str_cc)
            pdf.text(bx + w3 + (w3 - w_cc)/2, by - 1, str_cc)

            pdf.text(bx + bw + 2, by + bh/2 + 3.5, f"{v['chambrana_lat']:.2f}")

            str_zf = f"{v['zoclo_fijo']:.2f}"
            w_zf = pdf.get_string_width(str_zf)
            pdf.text(bx + w3 - w_zf - 1.5, by + bh - 1.5, str_zf)
            
            str_zc = f"{v['zoclo_corr']:.2f}"
            w_zc = pdf.get_string_width(str_zc)
            pdf.text(bx + bw - w_zc - 1.5, by + bh - 1.5, str_zc)

        elif v['tipo'] == "2 pulgadas, 2 hojas corredizas, 2 fijas":
            w4 = bw / 4
            pdf.line(bx + w4, by, bx + w4, by + bh)
            pdf.line(bx + w4*2, by, bx + w4*2, by + bh)
            pdf.line(bx + w4*3, by, bx + w4*3, by + bh)

            pdf.set_font("helvetica", "B", 11)
            pdf.text(bx + w4/2 - 3, by + bh/2 + 3, "F")
            pdf.text(bx + w4*3 + w4/2 - 3, by + bh/2 + 3, "F")
            pdf.set_font("helvetica", "", 10)

            pdf.set_line_width(0.3)
            cx = bx + w4 + w4/2
            pdf.line(cx - 3, by + bh/2, cx + 3, by + bh/2)
            pdf.line(cx + 3, by + bh/2, cx, by + bh/2 - 2)
            pdf.line(cx + 3, by + bh/2, cx, by + bh/2 + 2)
            
            rx = bx + w4*2 + w4/2
            pdf.line(rx + 3, by + bh/2, rx - 3, by + bh/2)
            pdf.line(rx - 3, by + bh/2, rx, by + bh/2 - 2)
            pdf.line(rx - 3, by + bh/2, rx, by + bh/2 + 2)

            pdf.set_text_color(255, 0, 0)
            str_largo = f"{v['largo']:.2f}"
            w_largo = pdf.get_string_width(str_largo)
            pdf.text(bx + (bw - w_largo)/2, by + bh + 4.5, str_largo)
            pdf.text(bx + bw + 2, by + bh/2 - 1, f"{v['ancho']:.2f}")

            pdf.set_text_color(32, 115, 172)
            
            str_cf_lbl = "CF"
            w_cf_lbl = pdf.get_string_width(str_cf_lbl)
            pdf.text(bx - w_cf_lbl - 1.5, by + bh/2 - 1.5, str_cf_lbl)
            
            str_cf_num = f"{v['cerco_fijo']:.2f}"
            w_cf_num = pdf.get_string_width(str_cf_num)
            pdf.text(bx - w_cf_num - 1.5, by + bh/2 + 3.5, str_cf_num)

            str_cc = f"CC {v['cerco_corr']:.2f}"
            w_cc = pdf.get_string_width(str_cc)
            pdf.text(bx + (bw - w_cc)/2, by - 1, str_cc)

            pdf.text(bx + bw + 2, by + bh/2 + 3.5, f"{v['chambrana_lat']:.2f}")

            str_zoclo = f"{v['zoclo']:.2f}"
            w_zoclo = pdf.get_string_width(str_zoclo)
            pdf.text(bx + w4 - w_zoclo - 1.5, by + bh - 1.5, str_zoclo)
            pdf.text(bx + bw - w_zoclo - 1.5, by + bh - 1.5, str_zoclo)

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
            pdf.cell(25, 6, f"{c['descripcion']}", border=1)
            pdf.cell(65, 6, f"{c['cant']} pz de {c['largo']:.2f} X {c['ancho']:.2f}", border=1, align="C")
        else:
            pdf.cell(90, 6, "", border=1)
        pdf.ln()

    return bytes(pdf.output())

# --- FUNCIÓN PARA EL DIBUJO EN PANTALLA ---
def generar_dibujo_ventana(v):
    num = v['num']
    tipo = v['tipo']
    largo = v['largo']
    ancho = v['ancho']
    
    if tipo in ["2 pulgadas, 2 hojas corredizas", "3 pulgadas, 2 hojas corredizas"]:
        cerco = v['cerco']
        chambrana_lat = v['chambrana_lat']
        zoclo = v['zoclo']
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
        
    elif tipo == "2 pulgadas, 2 hojas corredizas, 1 fija":
        cerco_fijo = v['cerco_fijo']
        cerco_corr = v['cerco_corr']
        chambrana_lat = v['chambrana_lat']
        zoclo_fijo = v['zoclo_fijo']
        zoclo_corr = v['zoclo_corr']
        svg = (
            f'<div style="display: flex; justify-content: center; margin-bottom: 10px;">'
            f'<svg viewBox="0 0 350 180" width="100%" max-width="350px" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="10" y="20" font-family="Arial" font-size="14" fill="black">V-{num}</text>'
            f'<rect x="50" y="30" width="200" height="110" fill="none" stroke="#1b6088" stroke-width="3"/>'
            f'<line x1="116.6" y1="30" x2="116.6" y2="140" stroke="#1b6088" stroke-width="2"/>'
            f'<line x1="183.3" y1="30" x2="183.3" y2="140" stroke="#1b6088" stroke-width="2"/>'
            f'<text x="83.3" y="92" font-family="Arial" font-size="18" font-weight="bold" fill="black" text-anchor="middle">F</text>'
            f'<line x1="130" y1="85" x2="170" y2="85" stroke="#1b6088" stroke-width="2"/>'
            f'<polyline points="160,75 170,85 160,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
            f'<line x1="235" y1="85" x2="195" y2="85" stroke="#1b6088" stroke-width="2"/>'
            f'<polyline points="205,75 195,85 205,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
            f'<text x="150" y="160" fill="red" font-family="Arial" font-size="14" text-anchor="middle">{largo:.2f}</text>'
            f'<text x="260" y="75" fill="red" font-family="Arial" font-size="14">{ancho:.2f}</text>'
            f'<text x="45" y="78" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">CF</text>'
            f'<text x="45" y="96" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">{cerco_fijo:.2f}</text>'
            f'<text x="150" y="25" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="middle">CC {cerco_corr:.2f}</text>'
            f'<text x="260" y="95" fill="#2073ac" font-family="Arial" font-size="14">{chambrana_lat:.2f}</text>'
            f'<text x="112" y="135" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="end">{zoclo_fijo:.2f}</text>'
            f'<text x="245" y="135" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="end">{zoclo_corr:.2f}</text>'
            f'</svg></div>'
        )
        return svg
        
    elif tipo == "2 pulgadas, 2 hojas corredizas, 2 fijas":
        cerco_fijo = v['cerco_fijo']
        cerco_corr = v['cerco_corr']
        chambrana_lat = v['chambrana_lat']
        zoclo = v['zoclo']
        svg = (
            f'<div style="display: flex; justify-content: center; margin-bottom: 10px;">'
            f'<svg viewBox="0 0 350 180" width="100%" max-width="350px" xmlns="http://www.w3.org/2000/svg">'
            f'<text x="10" y="20" font-family="Arial" font-size="14" fill="black">V-{num}</text>'
            f'<rect x="50" y="30" width="200" height="110" fill="none" stroke="#1b6088" stroke-width="3"/>'
            f'<line x1="100" y1="30" x2="100" y2="140" stroke="#1b6088" stroke-width="2"/>'
            f'<line x1="150" y1="30" x2="150" y2="140" stroke="#1b6088" stroke-width="2"/>'
            f'<line x1="200" y1="30" x2="200" y2="140" stroke="#1b6088" stroke-width="2"/>'
            
            f'<text x="75" y="92" font-family="Arial" font-size="18" font-weight="bold" fill="black" text-anchor="middle">F</text>'
            f'<text x="225" y="92" font-family="Arial" font-size="18" font-weight="bold" fill="black" text-anchor="middle">F</text>'
            
            f'<line x1="110" y1="85" x2="140" y2="85" stroke="#1b6088" stroke-width="2"/>'
            f'<polyline points="130,75 140,85 130,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
            
            f'<line x1="190" y1="85" x2="160" y2="85" stroke="#1b6088" stroke-width="2"/>'
            f'<polyline points="170,75 160,85 170,95" fill="none" stroke="#1b6088" stroke-width="2"/>'
            
            f'<text x="150" y="160" fill="red" font-family="Arial" font-size="14" text-anchor="middle">{largo:.2f}</text>'
            f'<text x="260" y="75" fill="red" font-family="Arial" font-size="14">{ancho:.2f}</text>'
            
            f'<text x="45" y="78" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">CF</text>'
            f'<text x="45" y="96" fill="#2073ac" font-family="Arial" font-size="14" text-anchor="end">{cerco_fijo:.2f}</text>'
            
            f'<text x="150" y="25" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="middle">CC {cerco_corr:.2f}</text>'
            f'<text x="260" y="95" fill="#2073ac" font-family="Arial" font-size="14">{chambrana_lat:.2f}</text>'
            
            f'<text x="95" y="135" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="end">{zoclo:.2f}</text>'
            f'<text x="245" y="135" fill="#2073ac" font-family="Arial" font-size="13" text-anchor="end">{zoclo:.2f}</text>'
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

tipo_ventana = st.selectbox(
    "Selecciona el tipo de ventana:",
    [
        "2 pulgadas, 2 hojas corredizas",
        "2 pulgadas, 2 hojas corredizas, 1 fija",
        "2 pulgadas, 2 hojas corredizas, 2 fijas",
        "3 pulgadas, 2 hojas corredizas"
    ]
)

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
        largo = st.number_input(f"Largo total (cm) - V{i}", min_value=0.0, value=None, step=0.1, format="%.1f", key=f"largo_{i}", placeholder="Ej. 120.0")
        ancho = st.number_input(f"Ancho total (cm) - V{i}", min_value=0.0, value=None, step=0.1, format="%.1f", key=f"ancho_{i}", placeholder="Ej. 100.0")

    if largo is not None and ancho is not None and largo > 0 and ancho > 0:
        if tipo_ventana == "2 pulgadas, 2 hojas corredizas":
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
            
            cristales_necesarios.append({'cant': 2, 'largo': largo_cristal, 'ancho': ancho_cristal, 'descripcion': f"V-{i}"})
            
            v_dict = {'num': i, 'tipo': tipo_ventana, 'largo': largo, 'ancho': ancho, 'cerco': ancho_cerco, 'chambrana_lat': ancho_lados, 'zoclo': medida_zc}
            ventanas_pdf.append(v_dict)

            with col_dibujo:
                dibujo = generar_dibujo_ventana(v_dict)
                st.markdown(dibujo, unsafe_allow_html=True)

        elif tipo_ventana == "2 pulgadas, 2 hojas corredizas, 1 fija":
            ancho_lados = ancho - 2.7
            medida_adaptador = (largo / 3.0) * 2.0
            cerco_fijo = ancho - 3.0
            cerco_corr = ancho - 4.0 
            zoclo_corr = ((largo - 19.0) / 3.0) - 1.0
            zoclo_fijo = zoclo_corr + 2.0
            
            largo_cristal_fijo = zoclo_fijo + 1.5
            ancho_cristal_fijo = cerco_fijo - 9.5
            largo_cristal_corr = zoclo_corr + 1.5
            ancho_cristal_corr = cerco_corr - 9.5

            cortes_chambranas.append({'medida': largo, 'descripcion': f"V{i} (Arriba)"})
            cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Izq)"})
            cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Der)"})
            cortes_rieles.append({'medida': largo, 'descripcion': f"V{i} (Riel Abajo)"})
            cortes_adaptadores.append({'medida': medida_adaptador, 'descripcion': f"V{i} (Adaptador Abajo)"})
            
            cortes_cercos.extend([{'medida': cerco_fijo, 'descripcion': f"V{i} (Cerco Fijo)"}, {'medida': cerco_corr, 'descripcion': f"V{i} (Cerco Corredizo)"}])
            
            cortes_traslapes.extend([{'medida': cerco_fijo, 'descripcion': f"V{i} (Traslape Fijo)"},
                                     {'medida': cerco_corr, 'descripcion': f"V{i} (Traslape Corr 1)"},
                                     {'medida': cerco_corr, 'descripcion': f"V{i} (Traslape Corr 2)"},
                                     {'medida': cerco_corr, 'descripcion': f"V{i} (Traslape Corr 3)"}])
            
            cortes_zoclos.extend([{'medida': zoclo_fijo, 'descripcion': f"V{i} (Zoclo Fijo)"},
                                  {'medida': zoclo_corr, 'descripcion': f"V{i} (Zoclo Corr 1)"},
                                  {'medida': zoclo_corr, 'descripcion': f"V{i} (Zoclo Corr 2)"}])
            
            cortes_cabezales.extend([{'medida': zoclo_fijo, 'descripcion': f"V{i} (Cabezal Fijo)"},
                                     {'medida': zoclo_corr, 'descripcion': f"V{i} (Cabezal Corr 1)"},
                                     {'medida': zoclo_corr, 'descripcion': f"V{i} (Cabezal Corr 2)"}])
            
            cristales_necesarios.append({'cant': 1, 'largo': largo_cristal_fijo, 'ancho': ancho_cristal_fijo, 'descripcion': f"V-{i} (Fijo)"})
            cristales_necesarios.append({'cant': 2, 'largo': largo_cristal_corr, 'ancho': ancho_cristal_corr, 'descripcion': f"V-{i} (Corr)"})

            v_dict = {'num': i, 'tipo': tipo_ventana, 'largo': largo, 'ancho': ancho, 
                      'cerco_fijo': cerco_fijo, 'cerco_corr': cerco_corr, 'chambrana_lat': ancho_lados, 
                      'zoclo_fijo': zoclo_fijo, 'zoclo_corr': zoclo_corr}
            ventanas_pdf.append(v_dict)

            with col_dibujo:
                dibujo = generar_dibujo_ventana(v_dict)
                st.markdown(dibujo, unsafe_allow_html=True)

        elif tipo_ventana == "2 pulgadas, 2 hojas corredizas, 2 fijas":
            ancho_lados = ancho - 2.7
            cerco_fijo = ancho - 3.0
            cerco_corr = ancho - 4.0 
            zoclo = (largo - 29.4) / 4.0
            
            largo_cristal_fijo = zoclo + 1.5
            ancho_cristal_fijo = cerco_fijo - 9.5
            largo_cristal_corr = zoclo + 1.5
            ancho_cristal_corr = cerco_corr - 9.5

            cortes_chambranas.append({'medida': largo, 'descripcion': f"V{i} (Arriba)"})
            cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Izq)"})
            cortes_chambranas.append({'medida': ancho_lados, 'descripcion': f"V{i} (Lado Der)"})
            cortes_rieles.append({'medida': largo, 'descripcion': f"V{i} (Riel Abajo)"})
            
            cortes_cercos.extend([
                {'medida': cerco_fijo, 'descripcion': f"V{i} (Cerco Fijo 1)"},
                {'medida': cerco_fijo, 'descripcion': f"V{i} (Cerco Fijo 2)"},
                {'medida': cerco_corr, 'descripcion': f"V{i} (Cerco Corredizo 1)"},
                {'medida': cerco_corr, 'descripcion': f"V{i} (Cerco Corredizo 2)"}
            ])
            
            cortes_traslapes.extend([
                {'medida': cerco_fijo, 'descripcion': f"V{i} (Traslape Fijo 1)"},
                {'medida': cerco_fijo, 'descripcion': f"V{i} (Traslape Fijo 2)"},
                {'medida': cerco_corr, 'descripcion': f"V{i} (Traslape Corr 1)"},
                {'medida': cerco_corr, 'descripcion': f"V{i} (Traslape Corr 2)"}
            ])
            
            cortes_zoclos.extend([
                {'medida': zoclo, 'descripcion': f"V{i} (Zoclo Fijo 1)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Zoclo Fijo 2)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Zoclo Corr 1)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Zoclo Corr 2)"}
            ])
            
            cortes_cabezales.extend([
                {'medida': zoclo, 'descripcion': f"V{i} (Cabezal Fijo 1)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Cabezal Fijo 2)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Cabezal Corr 1)"},
                {'medida': zoclo, 'descripcion': f"V{i} (Cabezal Corr 2)"}
            ])
            
            cristales_necesarios.append({'cant': 2, 'largo': largo_cristal_fijo, 'ancho': ancho_cristal_fijo, 'descripcion': f"V-{i} (Fijo)"})
            cristales_necesarios.append({'cant': 2, 'largo': largo_cristal_corr, 'ancho': ancho_cristal_corr, 'descripcion': f"V-{i} (Corr)"})

            v_dict = {'num': i, 'tipo': tipo_ventana, 'largo': largo, 'ancho': ancho, 
                      'cerco_fijo': cerco_fijo, 'cerco_corr': cerco_corr, 'chambrana_lat': ancho_lados, 'zoclo': zoclo}
            ventanas_pdf.append(v_dict)

            with col_dibujo:
                dibujo = generar_dibujo_ventana(v_dict)
                st.markdown(dibujo, unsafe_allow_html=True)

        elif tipo_ventana == "3 pulgadas, 2 hojas corredizas":
            ancho_lados = ancho - 2.7
            medida_adaptador = largo - 6.5
            ancho_cerco = ancho - 4.0
            
            # --- LA MATEMÁTICA NUEVA DEL ZOCLO A 3 PULGADAS ---
            medida_zc = (largo - 18.0) / 2.0
            
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
            
            cristales_necesarios.append({'cant': 2, 'largo': largo_cristal, 'ancho': ancho_cristal, 'descripcion': f"V-{i}"})
            
            v_dict = {'num': i, 'tipo': tipo_ventana, 'largo': largo, 'ancho': ancho, 'cerco': ancho_cerco, 'chambrana_lat': ancho_lados, 'zoclo': medida_zc}
            ventanas_pdf.append(v_dict)

            with col_dibujo:
                dibujo = generar_dibujo_ventana(v_dict)
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
            st.info(f"**{cristal['cant']} pieza(s)** de {cristal['largo']:.2f} cm (Largo) x {cristal['ancho']:.2f} cm (Ancho) ➔ {cristal['descripcion']}")