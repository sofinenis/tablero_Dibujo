import os
import streamlit as st
import base64
from openai import OpenAI
import openai
#from PIL import Image
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_drawable_canvas import st_canvas

if 'mi_respuesta' not in st.session_state:
    st.session_state.mi_respuesta = None
    
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."


# Streamlit 
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')
#image = Image.open('OIG9.jpg')
#st.image(image, width=350) 
with st.sidebar:
    st.subheader("Acerca de:")
    st.subheader("En esta aplicación veremos la capacidad que ahora tiene una máquina de interpretar un boceto")
st.subheader("Dibuja el boceto en el panel  y presiona el botón para analizarla")

# Add canvas component
bg_image = st.sidebar.file_uploader("Cargar Imagen:", type=["png", "jpg"])
# Specify canvas parameters in application
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
#stroke_color = '#FFFFFF' # Set background color to white
#bg_color = '#000000'
stroke_color = st.color_picker("Color de Trazo", "#000000")
bg_color = '#FFFFFF'
#realtime_update = st.sidebar.checkbox("Update in realtime", True)
drawing_mode = st.sidebar.selectbox(
    "Herramienta de dibujo:",
    ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
  )

# Create a canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=Image.open(bg_image) if bg_image else None,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('Ingresa tu Clave')
#os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
os.environ['OPENAI_API_KEY'] = ke


# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)


#if show_details:
    # Text input for additional details about the image, shown only if toggle is True
additional_details = st.text_area("Adiciona contexto de la imagen aqui:")
profile_ = st.radio(
    "Selecciona si quieres alguna experticia",
    ["Matemáticas", "Historia", "Programación","Mejoramiento de imágenes"],index=None)

profile_Math="""You are an expert in solving mathematical equations and you solve 
                  by showing step by step what you do, always solve the equation on image. 
                  You always use LaTeX format to write all the mathematical formulas of the answer.
                  You have a MathJax render environment.
                  - Any LaTeX text between single dollar sign ($) will be rendered as a TeX formula;
                  - Use $(tex_formula)$ in-line delimiters to display equations instead of backslash;
                  - The render environment only uses $ (single dollarsign) as a container delimiter, never output $$.
                  Example: $x^2 + 3x$ is output for "x² + 3x" to appear as TeX.`
                  Example: $ \int (x^2 ) is output ∫ x²dx
                  Example: $ ^\circ is output °
                  Example:$  \frac is output /
                  Example:$ \(x^2 ) is output x²
                  Example :$ \sqrt is output √
                  Example :$ \cdot is ⋅
                """
profile_Hist=""" Eres un experto en contar historias infantiles, crea una breve historia a partir de la imagen
                 , la historia debe ser breve.
                 """ 
profile_Prog=""" Eres un experto en programación, describe lo que realiza el código que aparece en la imagen y si 
                 el código tiene mala sintaxis o está equivocado corrígelo.
                 """ 

profile_imgenh =""" Do not mention that it is a simple drawing, describe briefly all the objects that appear in the image in spanish
                 """ 

if profile_ == "Matemáticas":
   Expert= profile_Math  
if profile_ == "Historia":
   Expert= profile_Hist
if profile_ == "Programación":
   Expert= profile_Prog 
if profile_ == "Mejoramiento de imágenes":
   Expert= profile_imgenh      
#else :
#   Expert= " "
# Button to trigger the analysis
analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'),'RGBA')
        input_image.save('img.png')
        
      # Codificar la imagen en base64
        if bg_image:
           image_ = Image.open(bg_image)
           image_.save('img.png') 
        base64_image = encode_image_to_base64("img.png")
            
        prompt_text = (f"{Expert},describe in spanish briefly the image,{additional_details}")
    
      # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url":f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
              model= "gpt-4o-mini",  #o1-preview ,gpt-4o-mini
              messages=[
                {
                   "role": "user",
                   "content": [
                     {"type": "text", "text": prompt_text},
                     {
                       "type": "image_url",
                       "image_url": {
                         "url": f"data:image/png;base64,{base64_image}",
                       },
                     },
                   ],
                  }
                ],
              max_tokens=500,
              )
            #response.choices[0].message.content
            if response.choices[0].message.content is not None:
                    full_response += response.choices[0].message.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)
            if Expert== profile_imgenh:
               st.session_state.mi_respuesta= response.choices[0].message.content #full_response 
    
            # Display the response in the app
            #st.write(response.choices[0])
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    # Warnings for user action required

    if not api_key:
        st.warning("Por favor ingresa tu API key.")
