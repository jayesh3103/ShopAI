import streamlit as st
import requests
import base64

# --- Page Config ---
st.set_page_config(
    page_title="ShopAI - Premium Shopping Assistant",
    page_icon="backend/static/logo.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants & State ---
API_URL = "https://shopai-backend-i1za.onrender.com/api" # Remote Backend

if "messages" not in st.session_state:
    st.session_state.messages = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []

# --- Custom CSS ---
def load_css():
    import os
    css_file = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# --- Components ---

def render_product_card(product):
    # Normalize product data for both internal and external sources
    p_name = product.get('name') or product.get('title', 'Product')
    p_img = product.get('image_url') or product.get('image', '')
    raw_price = product.get('price', 0)
    
    # Handle price parsing (could be string or float)
    if isinstance(raw_price, str):
        try: p_price = float(raw_price.replace('₹', '').replace(',', '').strip())
        except: p_price = 0.0
    else:
        p_price = float(raw_price)
        
    p_desc = product.get('description') or product.get('source', '')
    p_link = product.get('link', '#')
    # Generate unique key for buttons
    p_id = product.get('id') or str(abs(hash(p_link)))[:10]

    st.markdown(f"""
    <div class="product-card">
        <img src="{p_img}" class="product-img">
        <div class="card-body">
            <div class="card-title">{p_name}</div>
            <div class="card-price">₹{p_price:,.2f}</div>
            <div class="card-desc" style="height: 40px; overflow: hidden;">{p_desc}</div>
            """, unsafe_allow_html=True)

    # --- Action Buttons ---
    st.markdown('<div class="product-actions">', unsafe_allow_html=True)
    m1, m2, m3 = st.columns([1.2, 1.0, 0.8])
    
    with m1:
        st.markdown(f'<a href="{p_link}" target="_blank" class="buy-btn">Buy Now</a>', unsafe_allow_html=True)
        
    with m2:
        if st.button("📉", key=f"trend_{p_id}", help="AI Price Prediction"):
             with st.spinner("Analyzing Market..."):
                 try:
                     payload = {
                         "product_name": p_name,
                         "current_price": p_price,
                         "category": product.get("category", "General")
                     }
                     resp = requests.post(f"{API_URL}/predict-price", json=payload)
                     if resp.status_code == 200:
                         data = resp.json()
                         rec = data.get("recommendation")
                         confidence = data.get("confidence")
                         reason = data.get("reason")
                         drop = data.get("predicted_drop")
                         
                         icon = "🟢" if rec == "BUY_NOW" else "🔴"
                         st.toast(f"{icon} AI Advice: {rec} ({confidence}% Conf)\n\n{reason}\n\nPrediction: {drop}", icon="📉")
                     else: st.error("Prediction failed.")
                 except Exception as e: st.error(f"Error: {e}")

    with m3:
         if st.button("🌱", key=f"eco_{p_id}", help="View Eco-Score & Audit"):
             temp_p = {"name": p_name, "category": product.get("category", "General"), "description": p_desc, "image_url": p_img}
             get_eco_score(temp_p)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

@st.dialog("🌍 Sustainability Report")
def get_eco_score(product):
    st.caption(f"Analyzing {product['name']}...")
    with st.spinner("Auditing Materials & Lifecycle..."):
        try:
             payload = {
                 "product_name": product['name'],
                 "category": product.get("category", "General"),
                 "description": product.get("description", ""),
                 "image_url": product.get("image_url") 
             }
             resp = requests.post(f"{API_URL}/eco-score", json=payload)
             if resp.status_code == 200:
                 data = resp.json()
                 
                 # Visualization
                 score = data['score']
                 color = data['color'] # red, yellow, green
                 label = data['label']
                 
                 # Meter Header
                 st.markdown(f"""
                 <div style="text-align:center; padding:10px;">
                     <h1 style="color:{color}; font-size:3.5rem; margin:0; text-shadow: 0 0 20px {color}44;">{score}/100</h1>
                     <h3 style="margin-top:0; color:{color};">{label}</h3>
                 </div>
                 """, unsafe_allow_html=True)

                 # Ensure score is numeric for progress bar (Safety against string output from Gemini)
                 try:
                     numeric_score = float(score)
                 except (ValueError, TypeError):
                     numeric_score = 0.0
                     
                 st.progress(numeric_score / 100)
                 
                 # Greenwashing Alert
                 if data.get("greenwashing_flag"):
                     st.warning("🚨 **Greenwashing Alert:** This product's marketing claims may contradict its visual reality.")

                 # Advanced Metrics Grid
                 m1, m2, m3 = st.columns(3)
                 metrics = data.get("metrics", {})
                 with m1: st.metric("Carbon Footprint", metrics.get("carbon_footprint", "N/A"))
                 with m2: st.metric("Water Usage", metrics.get("water_usage", "N/A"))
                 with m3: st.metric("Recyclability", metrics.get("recyclability", "Unknown"))
                 
                 st.markdown("---")
                 
                 # Visual & Text Audit
                 st.caption("👁️ **Visual Audit (AI Vision):**")
                 st.info(data.get("visual_audit", "No visual issues detected."))
                 
                 st.caption(f"📝 **Reasoning:** {data['reason']}")
                 
                 c1, c2 = st.columns(2)
                 with c1:
                     st.markdown("**✅ Pros**")
                     for p in data['pros']: st.markdown(f"- {p}")
                 with c2:
                     st.markdown("**⚠️ Cons**")
                     for c in data['cons']: st.markdown(f"- {c}")
                     
                 st.caption(f"💡 **Tip:** {data['tips']}")
                 
             else:
                 st.error("Could not calculate score.")
        except Exception as e:
             st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    # Branding
    # Combine Logo and Text
    import base64
    import os
    
    logo_path = os.path.join(os.getcwd(), "backend/static/logo.svg")
    try:
        with open(logo_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        logo_src = f"data:image/svg+xml;base64,{encoded_string}"
    except Exception as e:
        logo_src = ""

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <img src="{logo_src}" width="50" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(to right, #fff, #a855f7); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;">ShopAI</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    # st.title("ShopAI") # Removed plain title
    st.markdown("---")
    
    # Navigation
    app_mode = st.radio("Navigate", ["🛍️ User App", "🔐 Admin Panel"])
    st.markdown("---")
    
    if app_mode == "🛍️ User App":
        st.header("User Settings")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.success("History cleared!")
    
    st.markdown("---")
    st.caption("Powered by Google Gemini 1.5 Flash")


# --- Main Layout ---
# --- Main Layout ---
if app_mode == "🔐 Admin Panel":
    st.title("🔐 Admin Dashboard")
    st.markdown("Upload a raw product image, and **ShopAI Vision** will automatically generate the catalog entry.")
    
    uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        from PIL import Image
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", width=300)
        
        if st.button("✨ Analyze & Auto-Fill"):
            with st.spinner("Gemini Vision is analyzing the product..."):
                # Helper to convert image to base64
                import io
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode()
                
                try:
                    response = requests.post(f"{API_URL}/admin/analyze", json={"image_data": img_b64})
                    if response.status_code == 200:
                        st.session_state['admin_data'] = response.json()
                        st.success("Analysis Complete!")
                    else:
                        st.error(f"Analysis failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'admin_data' in st.session_state:
        data = st.session_state['admin_data']
        with st.form("product_form"):
            st.subheader("Edit & Save Product")
            
            # Row 1: Core Info
            col1, col2 = st.columns(2)
            name = col1.text_input("Name", value=data.get('name', ''))
            category = col2.text_input("Category", value=data.get('category', ''))
            
            # Row 2: Pricing & Eco
            col3, col4 = st.columns(2)
            price = col3.number_input("Price (₹)", value=float(data.get('estimated_price_inr', 999.0)))
            rating = col4.slider("Sustainability Rating (1-10)", 1, 10, int(data.get('sustainability_rating', 5)))
            
            # Row 3: Rich Text
            desc = st.text_area("Marketing Description", value=data.get('description', ''), height=100)
            
            # Row 4: Advanced Meta
            col5, col6 = st.columns(2)
            material = col5.text_input("Material", value=data.get('material', 'Unknown'))
            seo_raw = data.get('seo_tags', [])
            seo_str = ", ".join(seo_raw) if isinstance(seo_raw, list) else str(seo_raw)
            seo_tags = col6.text_input("SEO Tags (comma separated)", value=seo_str)
            
            if st.form_submit_button("💾 Save to Catalog"):
                import random
                
                # Reconstruct tags
                final_tags = [t.strip() for t in seo_tags.split(",") if t.strip()]
                
                new_product = {
                    "id": f"new_{random.randint(1000,9999)}",
                    "name": name, 
                    "price": price, 
                    "description": desc,
                    "category": category,
                    "material": material,
                    "sustainability_rating": rating,
                    "seo_tags": final_tags,
                    "image_url": "http://127.0.0.1:8000/static/images/placeholder.jpg",
                    "manual_text": f"Manual for {name}. Material: {material}."
                }
                try:
                    save_resp = requests.post(f"{API_URL}/admin/add-product", json=new_product)
                    if save_resp.status_code == 200:
                        st.success("Saved & Indexed Successfully!")
                        del st.session_state['admin_data']
                        st.rerun()
                    else:
                        st.error(f"Save failed: {save_resp.text}")
                except Exception as e: st.error(f"Error: {e}")

elif app_mode == "🛍️ User App":
    st.title("🛍️ ShopAI")
    tab1, tab2 = st.tabs(["🔍 Product Search", "💬 AI Support Agent"])

    # --- TAB 1: PRODUCT SEARCH ---
    with tab1:
        st.markdown("### Find your perfect product")
        
        # Search Layout: Text Input | Voice Mic | Image Upload
        with st.container():
            st.markdown('<div class="search-row">', unsafe_allow_html=True)
            col_search, col_upload = st.columns([11, 1], gap="small")
            
            with col_search:
                query = st.text_input("Search", key='search_query_input', placeholder="Describe what you want...", label_visibility="collapsed")

            with col_upload:
                # Use Popover for a cleaner "Ultra Modern" look
                # The label will be the button itself
                with st.popover("📷", help="Search by Image"):
                     st.markdown("### Visual Search")
                     uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'png'], label_visibility='collapsed')
                     st.caption("Upload a product photo to find matches.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Auto-trigger search if voice was just recognized?
        # For now, let user click search or we can do it automatically if query is populated... behavior choice.
        # Let's keep the manual button for clarity unless user wants "Search by simply speaking". 
        # "Search product by simply speaking" implies auto-search. 
        # Let's keep the manual button for clarity unless user wants "Search by simply speaking". 
        # "Search product by simply speaking" implies auto-search. 
        
        # Determine if we should search: Button Click OR Voice Input OR Image Uploaded (Optional auto-search for image?)
        # Let's stick to button for consistency, but if voice is there we can hint it.
        
        should_search = st.button("Search Products", key="main_search_btn", type="primary", use_container_width=True)

        if should_search:
            # Use query from state which might have been updated by voice
            final_query = query
            
            with st.spinner("Searching catalog..."):
                payload = {}
                if uploaded_file:
                     bytes_data = uploaded_file.getvalue()
                     b64 = base64.b64encode(bytes_data).decode('utf-8')
                     payload["image_data"] = b64
                if final_query:
                    payload["query"] = final_query
                
                try:
                    # 1. Internal Catalog Search
                    response = requests.post(f"{API_URL}/search", json=payload)
                    internal_products = []
                    if response.status_code == 200:
                        data = response.json()
                        internal_products = data.get("products", [])
                        
                        # Show AI Analysis for Visual Search
                        if data.get("ai_description"):
                            st.info(f"**👁️ AI Vision Detected:** {data['ai_description']}")
                    else:
                        st.error("Internal search failed.")

                    # 2. External Google Shopping Search (SerpApi)
                    external_products = []
                    if final_query and not uploaded_file: # Only text search for now for external
                        try:
                            ext_resp = requests.post(f"{API_URL}/external-search", json={"query": final_query})
                            if ext_resp.status_code == 200:
                                external_products = ext_resp.json()
                        except Exception as e:
                            print(f"External search error: {e}")
                            
                    # Merge Results
                    st.session_state.search_results = internal_products + external_products
                    
                    if not st.session_state.search_results:
                         st.warning("No products found.")
                         
                except Exception as e:
                    st.error(f"Connection error: {e}")

        st.markdown("---")
        
        # Compare Feature Section
        if "compare_list" not in st.session_state:
            st.session_state.compare_list = []
        
        if len(st.session_state.compare_list) > 0:
            st.info(f"Selected {len(st.session_state.compare_list)} items for comparison.")
            if st.button("⚖️ Compare Now", type="primary"):
                 with st.spinner("Generating Comparison Table..."):
                     try:
                         # Send list directly
                         resp = requests.post(f"{API_URL}/compare", json=st.session_state.compare_list)
                         if resp.status_code == 200:
                             st.markdown("### Comparison Result")
                             st.markdown(resp.json()['markdown'])
                         else: st.error("Comparison failed.")
                     except Exception as e: st.error(f"Error: {e}")
            if st.button("Clear Selection"):
                st.session_state.compare_list = []
                st.rerun()

        # Grid Layout for Results
        results = st.session_state.search_results
        if results:
            cols = st.columns(3) # 3 Card Grid
            for i, product in enumerate(results):
                with cols[i % 3]:
                    render_product_card(product)
                    
                    # Add Checkbox for Comparison
                    # Unique key based on product ID
                    is_selected = product in st.session_state.compare_list
                    if st.checkbox("Select to Compare", key=f"chk_{product['id']}", value=is_selected):
                        if product not in st.session_state.compare_list:
                            st.session_state.compare_list.append(product)
                            st.rerun()
                    else:
                        if product in st.session_state.compare_list:
                             st.session_state.compare_list.remove(product)
                             st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True) # Check spacing
        elif final_query if 'final_query' in locals() else query or uploaded_file:
             st.info("No products found yet. Try searching!")
    # --- TAB 2: AI SUPPORT AGENT ---
    with tab2:
        st.markdown("### Expert Product Support")
        st.caption("Ask me anything about how to use, setup, or fix your products.")
        
        # --- VIDEO DIAGNOSTICS (Deep Seek) ---
        with st.expander("📹 Video Diagnostics (Deep Seek)", expanded=False):
            st.markdown('<div class="diag-card">', unsafe_allow_html=True)
            
            st.markdown("""
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="font-size: 1.5rem; color: #f3f4f6; margin-bottom: 5px;">🧬 AI Symptom Analysis</h2>
                    <p style="font-size: 0.9rem; color: #9ca3af;">Upload a video of the broken product. The AI will analyze the visual and audio symptoms.</p>
                </div>
            """, unsafe_allow_html=True)
            
            video_file_input = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'], key='video_diag', label_visibility="collapsed")
            context_input = st.text_input("Additional Context (Optional)", placeholder="Describe what you see or hear (e.g., 'grinding noise when turning on')...")
            
            if video_file_input and st.button("🔍 Run Diagnostic Analysis"):
                with st.spinner("Uploading & Analyzing Video (this may take a moment)..."):
                    try:
                        # Prepare file for API
                        files = {"file": (video_file_input.name, video_file_input, video_file_input.type)}
                        data = {"context": context_input}
                        
                        resp = requests.post(f"{API_URL}/analyze-video", files=files, data=data)
                        
                        if resp.status_code == 200:
                            report_md = resp.json().get("analysis", "No analysis returned.")
                            st.success("Analysis Complete!")
                            st.markdown("### 🧬 Deep Seek Diagnostic Report")
                            st.markdown(report_md)
                            
                            # Add to chat history context simply
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": f"**Video Analysis Report:**\n\n{report_md}"
                            })
                        else:
                            st.error(f"Analysis failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Chat container
        chat_container = st.container()
        
        # --- RENDER HISTORY ---
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message.get("html_content"):
                         st.markdown(message["html_content"], unsafe_allow_html=True)
                    
                    if message.get("external_products"):
                        p_list = message["external_products"]
                        hist_cols = st.columns(min(len(p_list), 2))
                        for i, p in enumerate(p_list):
                            with hist_cols[i % 2]:
                                render_product_card(p)
                    if message.get("visual_aid_url"):
                         st.markdown("---")
                         st.caption("🎬 **Virtual Technician Guide**")
                         st.video(message["visual_aid_url"])
                    if message.get("audio"):
                        st.audio(message["audio"], format="audio/mp3")

        # --- INPUT ---
        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun() # Force rerun to show user message immediately at bottom
            
            
        # Handle new user message (The last message is user and we need a reply)
        # Check if last message is user to trigger AI response
        last_msg = st.session_state.messages[-1] if st.session_state.messages else None
        
        if last_msg and last_msg["role"] == "user":
             prompt = last_msg["content"]
             
             # Check Intent for External Search
             intent_keywords = ["buy", "price", "shop", "find", "search", "looking for"]
             is_shopping_intent = any(keyword in prompt.lower() for keyword in intent_keywords)
             
             with chat_container: 
                 with st.chat_message("assistant"):
                     with st.spinner("Thinking..."):
                         
                        # 2. External Search (if intent detected)
                        if is_shopping_intent:
                            st.markdown(f"Searching online for '{prompt}'...")
                            try:
                                search_resp = requests.post(f"{API_URL}/external-search", json={"query": prompt})
                                if search_resp.status_code == 200:
                                    products = search_resp.json()
                                    if products:
                                        st.write("I found these options online:")
                                        # Use native columns for external products too
                                        chat_cols = st.columns(min(len(products), 2))
                                        for i, p in enumerate(products):
                                            with chat_cols[i % 2]:
                                                render_product_card(p)
                                        
                                        # Append a static marker to history since we render live in loop above
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": "I found those tailored options online for you.",
                                            "external_products": products # Custom key to re-render in history loop
                                        })
                                    else:
                                        st.session_state.messages.append({"role": "assistant", "content": "I looked online but couldn't find any specific products."})
                            except Exception as e:
                                st.error(f"Online search error: {e}")

                        # 3. RAG Chat Response (Always confirm with manuals too)
                        # Get response
                        api_history = []
                        for msg in st.session_state.messages[:-1]:
                            role = "user" if msg["role"] == "user" else "model"
                            api_history.append({"role": role, "parts": [msg["content"]]})
                            
                        try:
                            response = requests.post(f"{API_URL}/chat", json={
                                "message": prompt,
                                "history": api_history
                            })
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Generate TTS Audio
                                from gtts import gTTS
                                import io
                                tts = gTTS(text=data["response"], lang='en', tld='co.in') # Indian English accent
                                audio_fp = io.BytesIO()
                                tts.write_to_fp(audio_fp)
                                audio_bytes = audio_fp.getvalue()
                                
                                # Build final message dict
                                final_msg = {
                                    "role": "assistant", 
                                    "content": data["response"],
                                    "sources": data.get("sources", []),
                                    "audio": audio_bytes
                                }
                                if data.get("visual_aid_url"):
                                    final_msg["visual_aid_url"] = data["visual_aid_url"]
                                
                                st.session_state.messages.append(final_msg)
                                st.rerun() # Rerun to show the new assistant message
                            else:
                                st.error("Support agent is currently unavailable.")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
             # Force Rerun to update chat history cleanly
             st.rerun()

    # Render Chat
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("html_content"):
                    st.markdown(msg["html_content"], unsafe_allow_html=True)
                if msg.get("audio"):
                    st.audio(msg["audio"], format="audio/mp3")
                if msg.get("sources"):
                     with st.expander("Sources"):
                         for s in msg["sources"]:
                             st.markdown(f"- **{s.get('product_name')}**: Chunk {s.get('chunk_id')}")

