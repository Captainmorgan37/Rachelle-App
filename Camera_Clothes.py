import streamlit as st
from openai import OpenAI
from PIL import Image
import io, base64
import pandas as pd
from collections import defaultdict

# ---------- Helper ----------
def image_to_base64(img: Image.Image) -> str:
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# ---------- Streamlit App ----------
st.set_page_config(page_title="Clothing Describer", page_icon="👗", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("👗 Clothing Batch Description Generator (Manual Grouping)")
st.write("Upload multiple photos. Assign an Item ID to each photo to group them together.")

uploaded_files = st.file_uploader(
    "Upload clothing photos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("Step 1: Assign Item IDs")
    file_groups = {}

    # Let user assign group IDs
    for file in uploaded_files:
        image = Image.open(file)
        st.image(image, caption=file.name, use_container_width=True)
        item_id = st.text_input(f"Item ID for {file.name}", value=file.name.split(".")[0])
        file_groups[file.name] = {"file": file, "item_id": item_id}

    if st.button("Generate Descriptions"):
        grouped = defaultdict(list)
        for fname, data in file_groups.items():
            grouped[data["item_id"]].append(data["file"])

        results = []
        progress = st.progress(0)
        total_items = len(grouped)

        for idx, (item_id, files) in enumerate(grouped.items(), start=1):
            # Prepare multiple images for one item
            image_inputs = []
            for f in files:
                img = Image.open(f)
                image_inputs.append({
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64," + image_to_base64(img)}
                })

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a fashion assistant. Provide one description per item (use all images together)."},
                        {"role": "user", "content": [{"type": "text", "text": "Describe this clothing item:"}] + image_inputs}
                    ],
                    max_tokens=150
                )

                description = response.choices[0].message.content

            except Exception as e:
                description = f"Error: {e}"

            results.append({"item_id": item_id, "description": description})
            progress.progress(idx / total_items)

        # Show results
        df = pd.DataFrame(results)
        st.success("✅ Descriptions generated for all grouped items!")
        st.dataframe(df)

        # Download CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Descriptions as CSV",
            data=csv_bytes,
            file_name="clothing_descriptions.csv",
            mime="text/csv"
        )
