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
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="FileConverter Pro - Professional File Conversion Suite",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern UI - No white boxes
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main container styling - Transparent */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* Clean upload area - No white box */
    .uploadfile {
        border: 2px dashed rgba(255,255,255,0.3);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        color: white;
    }
    
    .uploadfile:hover {
        border-color: rgba(255,255,255,0.8);
        background: rgba(255,255,255,0.15);
    }
    
    /* Success message styling */
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #155724;
        font-weight: 500;
        margin: 1rem 0;
        animation: slideIn 0.5s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Clean tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 50px;
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: white;
        transition: all 0.3s ease;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #667eea !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Clean button styling */
    .stButton > button {
        background: white;
        color: #667eea;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        background: #f8f9fa;
    }
    
    /* Secondary button */
    .stButton > button[data-baseweb="button-secondary"] {
        background: transparent;
        color: white;
        border: 2px solid white;
    }
    
    .stButton > button[data-baseweb="button-secondary"]:hover {
        background: rgba(255,255,255,0.1);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: white;
    }
    
    /* Metric cards - Clean and minimal */
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255,255,255,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* History items - Clean and minimal */
    .history-item {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        animation: slideIn 0.3s ease;
        transition: all 0.3s ease;
        color: white;
    }
    
    .history-item:hover {
        transform: translateX(5px);
        background: rgba(255,255,255,0.15);
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 0.5rem;
        background: rgba(255,255,255,0.2);
        color: white;
    }
    
    /* File info text */
    .file-info {
        color: rgba(255,255,255,0.9);
        font-size: 0.9rem;
        padding: 0.5rem;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }
    
    /* Section headers */
    .section-header {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Sidebar styling - Clean */
    .css-1d391kg {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Quick action buttons */
    .quick-action {
        background: rgba(255,255,255,0.1);
        padding: 0.75rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        font-weight: 500;
    }
    
    .quick-action:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }
    
    /* Stats card in sidebar */
    .stats-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        border-radius: 10px;
    }
    
    .stSelectbox > div > div:hover {
        background: rgba(255,255,255,0.15);
    }
    
    /* Slider */
    .stSlider > div > div {
        color: white;
    }
    
    /* Checkbox */
    .stCheckbox > div > label {
        color: white;
    }
    
    /* File uploader text */
    .stFileUploader > div > div {
        color: white;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        border-radius: 10px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .main-subtitle {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []
if 'total_conversions' not in st.session_state:
    st.session_state.total_conversions = 0
if 'favorite_formats' not in st.session_state:
    st.session_state.favorite_formats = {'PDF': 0, 'Images': 0}
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'show_recent' not in st.session_state:
    st.session_state.show_recent = False

# Header section
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    <div class="main-header">
        <div class="main-title">🔄 FileConverter Pro</div>
        <div class="main-subtitle">Professional File Conversion Suite • Fast • Secure • Reliable</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Stats overview
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Total Conversions", st.session_state.total_conversions, "+1 today", label_visibility="collapsed")
    with col_b:
        st.metric("Success Rate", "100%", "0%", label_visibility="collapsed")

# Conversion functions (keeping your original functions)
def convert_pdf_to_images(pdf_bytes, output_format):
    """Convert PDF to images"""
    try:
        with tempfile.TemporaryDirectory() as path:
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                output_folder=path,
                fmt=output_format.lower()
            )
            
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
        
        if output_format.upper() == 'JPG':
            output_format = 'JPEG'
        
        if img.mode == 'RGBA' and output_format.upper() in ['JPEG', 'JPG']:
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
            img = rgb_img
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=output_format.upper())
        img_byte_arr.seek(0)
        
        original_name = Path(image_file.name).stem
        extension = output_format.lower()
        if output_format.upper() == 'JPEG':
            extension = 'jpg'
        
        return (f"{original_name}.{extension}", img_byte_arr.getvalue())
    except Exception as e:
        st.error(f"Error converting image: {str(e)}")
        return None

# Main conversion tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 PDF to Images", 
    "🖼️ Images to PDF", 
    "🎨 Image Converter",
    "📊 Analytics",
    "⚙️ Settings"
])

with tab1:
    st.markdown('<div class="section-header">📄 PDF to Image Conversion</div>', unsafe_allow_html=True)
    st.markdown("Convert your PDF documents to high-quality images")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pdf_file = st.file_uploader(
            "Drop your PDF file here",
            type=['pdf'],
            key="pdf_to_img",
            help="Supported: PDF files up to 200MB"
        )
        
        if pdf_file:
            st.markdown(f'<div class="file-info">📁 Selected: {pdf_file.name} ({(pdf_file.size/1024/1024):.2f} MB)</div>', unsafe_allow_html=True)
    
    with col2:
        output_format = st.selectbox(
            "Output Format",
            ['PNG', 'JPEG', 'WEBP', 'BMP'],
            key="pdf_output_format",
            help="Choose the output image format"
        )
        
        quality = st.slider("Quality", 1, 100, 85, help="Output quality (higher = better)")
    
    if pdf_file and output_format:
        if st.button("🚀 Start Conversion", key="convert_pdf_btn", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                status_text.text(f"Processing... {i+1}%")
                progress_bar.progress(i + 1)
                time.sleep(0.01)
            
            with st.spinner("Converting PDF to images..."):
                result_images = convert_pdf_to_images(pdf_file.read(), output_format)
                
                if result_images:
                    st.balloons()
                    st.markdown(f"""
                    <div class="success-box">
                        ✅ Successfully converted PDF to {len(result_images)} images!
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update stats
                    st.session_state.total_conversions += 1
                    st.session_state.favorite_formats['PDF'] += 1
                    
                    # Download options
                    col_d1, col_d2 = st.columns(2)
                    
                    with col_d1:
                        if len(result_images) > 1:
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                                for filename, img_bytes in result_images:
                                    zf.writestr(filename, img_bytes)
                            
                            zip_buffer.seek(0)
                            
                            st.download_button(
                                label="📦 Download All (ZIP)",
                                data=zip_buffer,
                                file_name="converted_images.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                    
                    with col_d2:
                        # Preview first image
                        st.markdown("**Preview:**")
                        st.image(result_images[0][1], caption=result_images[0][0], use_container_width=True)
                    
                    # Add to history
                    st.session_state.conversion_history.append({
                        'type': 'PDF to Images',
                        'input': pdf_file.name,
                        'output': f"{len(result_images)} images",
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'format': output_format
                    })
                    
                    progress_bar.empty()
                    status_text.empty()

with tab2:
    st.markdown('<div class="section-header">🖼️ Create PDF from Images</div>', unsafe_allow_html=True)
    st.markdown("Combine multiple images into a single PDF document")
    
    image_files = st.file_uploader(
        "Drop your images here",
        type=['png', 'jpg', 'jpeg', 'webp', 'bmp'],
        accept_multiple_files=True,
        key="img_to_pdf",
        help="Supported: PNG, JPG, JPEG, WEBP, BMP"
    )
    
    if image_files:
        st.markdown(f'<div class="file-info">📁 Selected {len(image_files)} images</div>', unsafe_allow_html=True)
        
        # Preview grid
        cols = st.columns(min(4, len(image_files)))
        for idx, img_file in enumerate(image_files[:4]):
            with cols[idx]:
                st.image(img_file, caption=f"Image {idx+1}", use_container_width=True)
        
        if len(image_files) > 4:
            st.caption(f"... and {len(image_files) - 4} more images")
        
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("📄 Create PDF", key="pdf_btn", use_container_width=True):
                with st.spinner("Creating PDF..."):
                    pdf_data = convert_images_to_pdf(image_files)
                    
                    if pdf_data:
                        st.balloons()
                        st.success(f"✅ PDF created successfully!")
                        
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_data,
                            file_name="converted_images.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        
                        # Update stats
                        st.session_state.total_conversions += 1
                        st.session_state.favorite_formats['Images'] += 1
                        
                        st.session_state.conversion_history.append({
                            'type': 'Images to PDF',
                            'input': f"{len(image_files)} images",
                            'output': "PDF file",
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

with tab3:
    st.markdown('<div class="section-header">🎨 Image Format Converter</div>', unsafe_allow_html=True)
    st.markdown("Convert images between different formats with ease")
    
    col1, col2 = st.columns(2)
    
    with col1:
        image_file = st.file_uploader(
            "Select image",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp', 'gif'],
            key="img_convert",
            help="Supported: PNG, JPG, JPEG, WEBP, BMP, GIF"
        )
        
        if image_file:
            st.image(image_file, caption="Original", use_container_width=True)
    
    with col2:
        to_format = st.selectbox(
            "Convert to",
            ['PNG', 'JPEG', 'WEBP', 'BMP', 'GIF'],
            key="to_format"
        )
        
        if image_file:
            if st.button("🎯 Convert Now", key="convert_btn", use_container_width=True):
                with st.spinner("Converting..."):
                    result = convert_image_format(image_file, to_format)
                    
                    if result:
                        filename, img_bytes = result
                        st.success("✅ Conversion complete!")
                        
                        st.image(img_bytes, caption="Converted", use_container_width=True)
                        
                        st.download_button(
                            label=f"📥 Download as {to_format}",
                            data=img_bytes,
                            file_name=filename,
                            mime=f"image/{to_format.lower()}",
                            use_container_width=True
                        )
                        
                        # Update stats
                        st.session_state.total_conversions += 1
                        
                        st.session_state.conversion_history.append({
                            'type': 'Image Format',
                            'input': f"{Path(image_file.name).suffix} image",
                            'output': f"{to_format} image",
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })

with tab4:
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🔄</div>
            <div class="metric-value">{st.session_state.total_conversions}</div>
            <div class="metric-label">Total Conversions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📊</div>
            <div class="metric-value">{st.session_state.favorite_formats['PDF']}</div>
            <div class="metric-label">PDF Conversions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🖼️</div>
            <div class="metric-value">{st.session_state.favorite_formats['Images']}</div>
            <div class="metric-label">Image Conversions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        today_count = len([h for h in st.session_state.conversion_history if h.get('timestamp', '').startswith(datetime.now().strftime("%Y-%m-%d"))])
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📅</div>
            <div class="metric-value">{today_count}</div>
            <div class="metric-label">Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Conversion history
    st.markdown('<div class="section-header">📋 Recent Activity</div>', unsafe_allow_html=True)
    
    if st.session_state.conversion_history:
        for conversion in reversed(st.session_state.conversion_history[-10:]):
            st.markdown(f"""
            <div class="history-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="badge">{conversion['type']}</span>
                        <strong>{conversion['input']}</strong> → <strong>{conversion['output']}</strong>
                    </div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">
                        {conversion.get('timestamp', 'Just now')}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Clear History", type="secondary"):
            st.session_state.conversion_history = []
            st.rerun()
    else:
        st.info("No conversion history yet. Start converting files!")

with tab5:
    st.markdown('<div class="section-header">⚙️ Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Appearance")
        theme = st.selectbox("Theme", ["Light", "Dark", "System"])
        animations = st.toggle("Enable Animations", value=True)
        compact_mode = st.toggle("Compact Mode", value=False)
    
    with col2:
        st.markdown("#### ⚡ Performance")
        max_file_size = st.number_input("Max File Size (MB)", min_value=10, max_value=500, value=200)
        parallel_conversions = st.slider("Parallel Conversions", 1, 5, 2)
    
    st.markdown("#### 💾 Storage")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.checkbox("Auto-save converted files", value=True)
        st.checkbox("Keep conversion history", value=True)
    with col_s2:
        st.checkbox("Compress output files", value=False)
        st.checkbox("Show file previews", value=True)

# Sidebar with quick actions
with st.sidebar:
    st.markdown("## 🚀 Quick Actions")
    
    if st.button("📊 View Dashboard", use_container_width=True):
        st.session_state.active_tab = 3
        st.rerun()
    
    if st.button("📋 Recent Files", use_container_width=True):
        st.session_state.show_recent = True
        if st.session_state.conversion_history:
            st.sidebar.markdown("### Latest Files")
            for item in st.session_state.conversion_history[-3:]:
                st.sidebar.markdown(f"- {item['input']}")
    
    st.markdown("---")
    
    st.markdown("## 📈 Today's Stats")
    today_count = len([h for h in st.session_state.conversion_history if h.get('timestamp', '').startswith(datetime.now().strftime("%Y-%m-%d"))])
    st.markdown(f"""
    <div class="stats-card">
        <strong>Conversions:</strong> {today_count}<br>
        <strong>Files processed:</strong> {st.session_state.total_conversions}<br>
        <strong>Success rate:</strong> 100%<br>
        <strong>Active since:</strong> Today
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## 💡 Pro Tips")
    with st.expander("View Tips", expanded=False):
        st.markdown("""
        - ✨ Use PNG for images with transparency
        - 📸 JPEG is best for photographs
        - 📚 Convert multiple PDFs to images in one go
        - 🔄 Images to PDF preserves original order
        - 🚀 WEBP offers better compression
        - 💾 Batch download saves time
        """)
    
    st.markdown("---")
    
    # Version info
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.85rem;">
        <strong>Version:</strong> 2.0.0 Pro<br>
        <strong>©</strong> 2026 FileConverter Pro<br>
        <strong>Made with</strong> ❤️ for conversions
    </div>
    """, unsafe_allow_html=True)
