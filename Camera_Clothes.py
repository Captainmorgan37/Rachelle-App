import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# ---------- Helper to convert PIL Image to base64 ----------
def image_to_base64(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# ---------- Streamlit App ----------
st.set_page_config(page_title="Clothing Describer", page_icon="👗", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # API key from secrets.toml or Streamlit Cloud Secrets Manager

st.title("👗 Clothing Description Generator")
st.write("Take or upload a picture of clothing, and I'll generate a description for you.")

# Upload or Camera input
uploaded_file = st.file_uploader("Upload a clothing photo", type=["jpg", "jpeg", "png"])
camera_file = st.camera_input("Or take a picture with your camera")

image_source = camera_file or uploaded_file

if image_source:
    # Open and show the image
    image = Image.open(image_source)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing clothing..."):
        # Send to OpenAI Vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # fast multimodal model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a fashion assistant. "
                        "Always give short, clear product-style descriptions: color, type of clothing, "
                        "material/style if visible."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this clothing item in one or two sentences."},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_to_base64(image)}}
                    ]
                }
            ],
            max_tokens=150
        )

        description = response.choices[0].message["content"]

    st.success("### Clothing Description")
    st.write(description)

    # Easy copy box
    st.text_area("Copy description:", description, height=100)
