import streamlit as st
import ollama
from PIL import Image
import io
import base64

st.title("💬 AI Chatbot")


if "previous_model" not in st.session_state:
    st.session_state["previous_model"] = None

model_options = ["LLaMA 3.2", "LLAVA", "CodeLlama"]
selected_model = st.selectbox("Select AI Model:", model_options)


if st.session_state["previous_model"] is not None and st.session_state["previous_model"] != selected_model:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["full_message"] = ""
    if "current_image" in st.session_state:
        del st.session_state["current_image"]


st.session_state["previous_model"] = selected_model


if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    st.session_state["full_message"] = ""


for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="🤖").write(msg["content"])

def generate_response(image_data=None):
    messages = st.session_state.messages
    
    if selected_model == "LLAVA" and image_data:
        messages[-1]["images"] = [image_data]
    
    try:
        if selected_model == "LLAVA":
            model_name = 'llava'
        elif selected_model == "CodeLlama":
            model_name = 'codellama'
        else:
            model_name = 'llama3.2'

        response = ollama.chat(
            model=model_name,
            stream=True,
            messages=messages
        )
        
        for partial_resp in response:
            token = partial_resp["message"]["content"]
            st.session_state["full_message"] += token
            yield token
    except Exception as e:
        yield f"Error: {str(e)}"

if selected_model == "LLAVA":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        st.session_state["current_image"] = img_base64


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["full_message"] = ""

    with st.chat_message("assistant", avatar="🤖"):
        if selected_model == "LLAVA" and "current_image" in st.session_state:
            message_stream = generate_response(st.session_state["current_image"])
        else:
            message_stream = generate_response()
        
        st.write_stream(message_stream)
        
    st.session_state.messages.append({"role": "assistant", "content": st.session_state["full_message"]})