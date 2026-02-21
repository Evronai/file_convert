# app.py
import streamlit as st
from PIL import Image
import pdf2image
import img2pdf
import os
import tempfile
from pathlib import Path
import io
import zipfile
import base64

# Page configuration
st.set_page_config(
    page_title="File Converter Pro",
    page_icon="🔄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .converter-card {
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔄 File Converter Pro")
st.markdown("Convert your files between different formats easily!")

# Initialize session state for conversion history
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

def get_download_link(file_bytes, filename, text):
    """Generate a download link for a file"""
    b64 = base64.b64encode(file_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="success-message">{text}</a>'
    return href

def convert_pdf_to_images(pdf_bytes, output_format):
    """Convert PDF to images"""
    try:
        with tempfile.TemporaryDirectory() as path:
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                output_folder=path,
                fmt=output_format.lower()
            )
            
            # Save images to bytes
            image_bytes_list = []
            for i, image in enumerate(images):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=output_format)
                img_byte_arr.seek(0)
                image_bytes_list.append((f"page_{i+1}.{output_format.lower()}", img_byte_arr.getvalue()))
            
            return image_bytes_list
    except Exception as e:
        st.error(f"Error converting PDF: {str(e)}")
        return None

def convert_images_to_pdf(image_files):
    """Convert multiple images to PDF"""
    try:
        pdf_bytes = io.BytesIO()
        images = []
        
        for image_file in image_files:
            img = Image.open(image_file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        if images:
            images[0].save(pdf_bytes, 'PDF', save_all=True, append_images=images[1:])
            pdf_bytes.seek(0)
            return pdf_bytes.getvalue()
    except Exception as e:
        st.error(f"Error converting images to PDF: {str(e)}")
        return None

def convert_image_format(image_file, output_format):
    """Convert image from one format to another"""
    try:
        img = Image.open(image_file)
        
        # Handle special cases
        if output_format.upper() == 'JPG':
            output_format = 'JPEG'
        
        if img.mode == 'RGBA' and output_format.upper() in ['JPEG', 'JPG']:
            # Convert RGBA to RGB for JPEG
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = rgb_img
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=output_format.upper())
        img_byte_arr.seek(0)
        
        # Generate filename
        original_name = Path(image_file.name).stem
        extension = output_format.lower()
        if output_format.upper() == 'JPEG':
            extension = 'jpg'
        
        return (f"{original_name}.{extension}", img_byte_arr.getvalue())
    except Exception as e:
        st.error(f"Error converting image: {str(e)}")
        return None

# Main conversion interface
tab1, tab2, tab3, tab4 = st.tabs(["📄 PDF to Images", "🖼️ Images to PDF", "🎨 Image Format Converter", "📊 Conversion History"])

with tab1:
    st.markdown("### 📄 Convert PDF to Images")
    st.markdown("Upload a PDF file and convert it to multiple image formats.")
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            pdf_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_to_img")
        
        with col2:
            output_format = st.selectbox(
                "Output image format",
                ['PNG', 'JPEG', 'WEBP', 'BMP'],
                key="pdf_output_format"
            )
        
        if pdf_file and output_format:
            if st.button("Convert PDF to Images", key="convert_pdf_btn"):
                with st.spinner("Converting PDF to images..."):
                    result_images = convert_pdf_to_images(pdf_file.read(), output_format)
                    
                    if result_images:
                        st.success(f"✅ Successfully converted PDF to {len(result_images)} images!")
                        
                        # Create zip file for multiple images
                        if len(result_images) > 1:
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                                for filename, img_bytes in result_images:
                                    zf.writestr(filename, img_bytes)
                            
                            zip_buffer.seek(0)
                            
                            st.download_button(
                                label="📥 Download All Images (ZIP)",
                                data=zip_buffer,
                                file_name="converted_images.zip",
                                mime="application/zip"
                            )
                        
                        # Display individual download links
                        st.markdown("#### Individual Images:")
                        cols = st.columns(min(3, len(result_images)))
                        for idx, (filename, img_bytes) in enumerate(result_images[:6]):  # Show first 6
                            with cols[idx % 3]:
                                st.download_button(
                                    label=f"📥 {filename}",
                                    data=img_bytes,
                                    file_name=filename,
                                    mime=f"image/{output_format.lower()}"
                                )
                        
                        if len(result_images) > 6:
                            st.info(f"... and {len(result_images) - 6} more images")
                        
                        # Add to history
                        st.session_state.conversion_history.append({
                            'type': 'PDF to Images',
                            'input': pdf_file.name,
                            'output': f"{len(result_images)} images"
                        })

with tab2:
    st.markdown("### 🖼️ Convert Images to PDF")
    st.markdown("Upload multiple images and combine them into a single PDF.")
    
    with st.container():
        image_files = st.file_uploader(
            "Choose images",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
            accept_multiple_files=True,
            key="img_to_pdf"
        )
        
        if image_files:
            if st.button("Convert Images to PDF", key="convert_img_btn"):
                with st.spinner("Converting images to PDF..."):
                    pdf_data = convert_images_to_pdf(image_files)
                    
                    if pdf_data:
                        st.success(f"✅ Successfully converted {len(image_files)} images to PDF!")
                        
                        # Preview images
                        st.markdown("#### Preview:")
                        cols = st.columns(min(4, len(image_files)))
                        for idx, img_file in enumerate(image_files[:4]):
                            with cols[idx]:
                                img = Image.open(img_file)
                                st.image(img, caption=img_file.name, use_container_width=True)
                        
                        if len(image_files) > 4:
                            st.info(f"... and {len(image_files) - 4} more images")
                        
                        # Download button
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name="converted.pdf",
                            mime="application/pdf"
                        )
                        
                        # Add to history
                        st.session_state.conversion_history.append({
                            'type': 'Images to PDF',
                            'input': f"{len(image_files)} images",
                            'output': "PDF file"
                        })

with tab3:
    st.markdown("### 🎨 Image Format Converter")
    st.markdown("Convert single images between different formats.")
    
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            image_file = st.file_uploader(
                "Choose an image",
                type=['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif'],
                key="img_convert"
            )
        
        with col2:
            from_format = st.selectbox(
                "From format",
                ['PNG', 'JPEG', 'WEBP', 'BMP', 'GIF'],
                key="from_format"
            )
        
        with col3:
            to_format = st.selectbox(
                "To format",
                ['PNG', 'JPEG', 'WEBP', 'BMP', 'GIF'],
                key="to_format"
            )
        
        if image_file and from_format and to_format:
            if st.button("Convert Image", key="convert_img_format_btn"):
                with st.spinner("Converting image format..."):
                    result = convert_image_format(image_file, to_format)
                    
                    if result:
                        filename, img_bytes = result
                        st.success(f"✅ Successfully converted to {to_format}!")
                        
                        # Display preview
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Original Image:**")
                            st.image(image_file, use_container_width=True)
                        
                        with col2:
                            st.markdown("**Converted Image:**")
                            st.image(img_bytes, use_container_width=True)
                        
                        # Download button
                        st.download_button(
                            label=f"📥 Download as {to_format}",
                            data=img_bytes,
                            file_name=filename,
                            mime=f"image/{to_format.lower()}"
                        )
                        
                        # Add to history
                        st.session_state.conversion_history.append({
                            'type': 'Image Format',
                            'input': f"{from_format} image",
                            'output': f"{to_format} image"
                        })

with tab4:
    st.markdown("### 📊 Conversion History")
    
    if st.session_state.conversion_history:
        for idx, conversion in enumerate(reversed(st.session_state.conversion_history)):
            with st.container():
                st.markdown(f"""
                <div style="padding: 10px; margin: 5px 0; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #4CAF50;">
                    <strong>{conversion['type']}</strong><br>
                    Input: {conversion['input']}<br>
                    Output: {conversion['output']}
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("Clear History"):
            st.session_state.conversion_history = []
            st.rerun()
    else:
        st.info("No conversion history yet. Start converting files!")

# Sidebar with additional information
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("""
    **File Converter Pro** helps you convert files quickly and easily.
    
    ### Features:
    - 📄 PDF to Images
    - 🖼️ Images to PDF
    - 🎨 Image Format Conversion
    - 📊 Conversion History
    
    ### Supported Formats:
    - PDF
    - PNG, JPEG, WEBP, BMP, GIF
    
    ### How to use:
    1. Select conversion type
    2. Upload your file(s)
    3. Choose output format
    4. Click convert
    5. Download results
    """)
    
    st.markdown("---")
    st.markdown("### 📝 Tips")
    st.info("""
    - For PDF to images, you can download all images as ZIP
    - Images to PDF preserves the order you upload them
    - JPEG format doesn't support transparency
    """)
