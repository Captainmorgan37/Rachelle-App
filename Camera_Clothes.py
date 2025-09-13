import streamlit as st
from openai import OpenAI
from PIL import Image
import io, base64
import pandas as pd

# --- Helper to convert image to base64 ---
def image_to_base64(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- Streamlit App ---
st.set_page_config(page_title="Clothing Describer", page_icon="👗", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("👗 Clothing Description Generator")

# Choose mode
mode = st.radio("Choose input method:", ["📷 Take a Photo", "📂 Upload Existing Photos"])

results = []

if mode == "📷 Take a Photo":
    camera_file = st.camera_input("Take a picture with your camera")
    if camera_file:
        image = Image.open(camera_file)
        st.image(image, caption="Captured Image", use_container_width=True)

        with st.spinner("Analyzing clothing..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
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
                description = response.choices[0].message.content
            except Exception as e:
                description = f"Error: {e}"

        results.append({"filename": "camera_capture.png", "description": description, "image": image})

elif mode == "📂 Upload Existing Photos":
    uploaded_files = st.file_uploader(
        "Upload clothing photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            image = Image.open(file)
            with st.spinner(f"Analyzing {file.name}..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
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
                except Exception as e:
                    description = f"Error: {e}"

            results.append({"filename": file.name, "description": description, "image": image})

# Show results + download if available
if results:
    st.success("✅ Processing complete!")

    # Display results with thumbnails
    for r in results:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(r["image"], width=100)
        with col2:
            st.markdown(f"**{r['filename']}**\n\n{r['description']}")

    # Build DataFrame (without images) for CSV
    df = pd.DataFrame([{"filename": r["filename"], "description": r["description"]} for r in results])

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Descriptions as CSV",
        data=csv,
        file_name="clothing_descriptions.csv",
        mime="text/csv"
    )
