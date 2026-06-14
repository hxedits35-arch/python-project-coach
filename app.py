import streamlit as st
import plotly.express as px
import datetime
import io
import analyzer

# Import ReportLab elements for the PDF exporter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration
st.set_page_config(
    page_title="Python Project Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom minimal styling for adaptive button matching dropzone
st.markdown("""
    <style>
    /* Primary Action Button Styling */
    div.stButton > button:first-child {
        background-color: rgba(128, 128, 128, 0.08) !important; /* Exact tint of the inner upload box dropzone */
        color: var(--text-color) !important;
        border: 1px dashed rgba(128, 128, 128, 0.3) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: rgba(128, 128, 128, 0.18) !important;
        border-color: rgba(128, 128, 128, 0.5) !important;
        color: var(--text-color) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if "private_history" not in st.session_state:
    st.session_state.private_history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "current_report" not in st.session_state:
    st.session_state.current_report = None
if "current_filename" not in st.session_state:
    st.session_state.current_filename = ""

# Helper function to generate clean PDF report cards in memory
def generate_pdf_report(filename, report):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=12, textColor=colors.HexColor("#1A365D"))
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=16, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#2C5282"))
    body_style = ParagraphStyle('BodyStyle', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=8)
    
    # Header
    doc_title = "🎓 Python Project Coach Report Card"
    story.append(Paragraph(doc_title, title_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.datetime.now().strftime('%B %d, %Y')} | <b>Target File:</b> {filename}", body_style))
    story.append(Spacer(1, 15))
    
    # Scores Summary Table
    data = [
        [Paragraph("<b>Overall Project Score</b>", body_style), Paragraph(f"<b>{report['score']}/100</b>", body_style)],
        [Paragraph("<b>Assigned Letter Grade</b>", body_style), Paragraph(f"<b>{report['grade']}</b>", body_style)]
    ]
    
    # Add metric breakdown rows dynamically
    for metric, val in report["breakdown"].items():
        data.append([Paragraph(f"Category: {metric}", body_style), Paragraph(f"{val}/100", body_style)])
        
    t = Table(data, colWidths=[300, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,1), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Coach Feedback Section
    story.append(Paragraph("🧠 AI Mentor Critique Summary", heading_style))
    story.append(Paragraph(report["ai_critique"].replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 15))
    
    # Static Warnings Check
    story.append(Paragraph("🔍 Structural Warnings Check", heading_style))
    all_issues = report["errors"] + report["warnings"]
    if all_issues:
        for issue in all_issues:
            story.append(Paragraph(f"• {issue}", body_style))
    else:
        story.append(Paragraph("✨ No major syntax structural compiler flaws flagged. Good architecture foundations!", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# 2. Custom Layout Title Tagging (Anchor Point)
st.markdown("<div id='top'></div>", unsafe_allow_html=True)
st.title("🎓 Python Project Coach")
st.caption("A Zero-Cost, Cloud-Powered AI Mentor for Beginner Programmers")
st.markdown("---")

# 3. Sidebar Configuration
st.sidebar.header("📜 Your Analysis History")
st.sidebar.markdown("*(Only visible to you during this session)*")

if st.session_state.private_history:
    for run in reversed(st.session_state.private_history):
        with st.sidebar.container(border=True):
            st.markdown(f"📅 **{run['timestamp']}**")
            st.markdown(f"📄 *File:* `{run['filename']}`")
            st.markdown(f"🏆 *Score:* **{run['score']}/100** ({run['grade']})")
else:
    st.sidebar.info("No history recorded yet. Analyze some code to begin!")

# 4. Main UI Inputs
st.subheader("🛠️ Step 1: Submit Your Python Code")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("**Option A: Upload File**")
        uploaded_file = st.file_uploader("Upload a Python file (.py)", type=["py"], label_visibility="collapsed")

with col2:
    with st.container(border=True):
        st.markdown("**Option B: Paste Raw Code**")
        text_code_input = st.text_area(
            "Paste code here:", 
            height=68, 
            placeholder="def my_function():\n    x = 10\n    return x",
            label_visibility="collapsed"
        )

# Determine final source code code block properties
final_code = ""
display_name = ""

if uploaded_file is not None:
    final_code = uploaded_file.getvalue().decode("utf-8")
    display_name = uploaded_file.name
    st.success(f"Loaded: `{display_name}` successfully!")
elif text_code_input.strip() != "":
    final_code = text_code_input
    display_name = "Text Input Snippet"

# 5. Core Trigger Button Execution
st.markdown("###")
if st.button("🚀 Analyze Project Quality", use_container_width=True, type="secondary"):
    if final_code.strip() == "":
        st.warning("Please upload a file or write some code inside the text box first!")
    else:
        with st.spinner("Analyzing code architecture and asking Cloud AI Coach..."):
            report = analyzer.run_full_code_analysis(final_code)
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            
            # Lock report values safely into session states to retain visibility during conversational re-renders
            st.session_state.current_report = report
            st.session_state.current_filename = display_name
            st.session_state.chat_messages = [{"role": "assistant", "content": "Initial report generated! Ask me any specific follow-up questions about your code structures or bugs below."}]
            
            st.session_state.private_history.append({
                "timestamp": current_time,
                "filename": display_name,
                "score": report["score"],
                "grade": report["grade"]
            })

# 6. Check if a report has been generated to keep rendering the dashboard output UI components
if st.session_state.current_report is not None:
    report = st.session_state.current_report
    display_name = st.session_state.current_filename
    
    st.markdown("---")
    
    # Title row with PDF export utility layout next to it
    res_col1, res_col2 = st.columns([3, 1])
    with res_col1:
        st.subheader("📊 Code Analysis Results")
    with res_col2:
        # Build document bytes
        pdf_data = generate_pdf_report(display_name, report)
        st.download_button(
            label="📥 Export Report PDF",
            data=pdf_data,
            file_name=f"Project_Coach_Report_{datetime.date.today()}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
    m_col1, m_col2, m_col3 = st.columns([1, 1, 2])
    
    with m_col1:
        st.metric(label="Overall Code Score", value=f"{report['score']}/100")
        st.progress(report["score"] / 100)
        
    with m_col2:
        st.metric(label="Assigned Letter Grade", value=report["grade"])
        
    with m_col3:
        chart_data = {
            "Metric Category": list(report["breakdown"].keys()),
            "Score Values": list(report["breakdown"].values())
        }
        fig = px.bar(
            chart_data, 
            x="Metric Category", 
            y="Score Values", 
            range_y=[0, 100],
            color="Score Values",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            height=180, 
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 7. Layout Tabs Breakdown
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💡 AI Coach Review & Chat", "⚠️ Structural Warnings", "📚 Free Learning Resources"])
    
    with tab1:
        st.markdown("### 🧠 Cloud Llama 3 Feedback Summary")
        st.markdown(report["ai_critique"])
        
        st.markdown("---")
        st.markdown("### 💬 Chat Live with your Coach")
        
        # Display session conversation records sequentially
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Accept real-time follow-up user text queries
        if user_query := st.chat_input("Ask a follow up question about your code results:"):
            # Append student query
            st.session_state.chat_messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)
                
            # Request subsequent contextual response guidance stream block from analyzer
            with st.spinner("Coach is thinking..."):
                if hasattr(analyzer, "ask_follow_up"):
                    reply = analyzer.ask_follow_up(user_query, report)
                else:
                    reply = f"I've noted your question regarding '{user_query}'. To provide complete guidance on this point, refine your function loops or make sure your parameters align with proper functional rules."
                
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()
                
    with tab2:
        st.markdown("### 🔍 Static Code Flaws Detected")
        if report["errors"]:
            for error in report["errors"]:
                st.error(error)
        
        if report["warnings"]:
            for warning in report["warnings"]:
                st.warning(warning)
        elif not report["errors"] and not report["warnings"]:
            st.success("✨ Incredible! No structural formatting warnings or flaws found in your code structure.")
            
    with tab3:
        st.markdown("### 📖 Recommended Learning Materials")
        for resource in report["resources"]:
            with st.expander(resource["title"]):
                st.write(resource["description"])
                st.markdown(f"[Click here to open and read free guide]({resource['url']})")

    # Native, sandbox-proof shortcut back up to the top layout block
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: right; padding-bottom: 20px;">
            <a href="#top" target="_self" style="text-decoration: none; background-color: rgba(128,128,128,0.08); color: var(--text-color); padding: 10px 16px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); font-weight: bold; font-size: 13px; transition: background 0.2s;">▲ Scroll to Top</a>
        </div>
        """, 
        unsafe_allow_html=True
    )