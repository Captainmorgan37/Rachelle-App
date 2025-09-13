import streamlit as st
from openai import OpenAI
from PIL import Image
import io

# ---------- Streamlit App ----------
st.set_page_config(page_title="Clothing Describer", page_icon="👗", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # key in secrets.toml or Streamlit Cloud Secrets Manager

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

    # Convert to bytes for OpenAI API
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes = img_bytes.getvalue()

    with st.spinner("Analyzing clothing..."):
        try:
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
                        "content": "Describe this clothing item in one or two sentences."
                    }
                ],
                files=[
                    {
                        "name": "clothing.png",
                        "buffer": io.BytesIO(img_bytes)
                    }
                ],
                max_tokens=150
            )

            description = response.choices[0].message["content"]

        except Exception as e:
            st.error(f"Error: {e}")
            description = None

    if description:
        st.success("### Clothing Description")
        st.write(description)

        # Easy copy box
        st.text_area("Copy description:", description, height=100)
