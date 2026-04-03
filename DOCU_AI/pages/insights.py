import reflex as rx
from DOCU_AI.components.navbar import navbar
from DOCU_AI.components.footer import footer
from DOCU_AI.backend.rag import extract_insights
import json
import io
import os
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

# Use the same DOCUMENT_PATH logic as regular backend
DOCUMENT_PATH = os.path.join(os.getcwd(), "documents")

class InsightRecord(rx.Base):
    """A single insight record in the history."""
    timestamp: str = ""
    chart_type: str = "bar"
    chart_title: str = ""
    explanation: str = ""
    executive_summary: str = ""
    comparison_analysis: str = ""
    key_takeaways: list[str] = []
    key_concepts: list[str] = []
    recharts_data: list[dict[str, str | float]] = []

class InsightsState(rx.State):
    """The state for the premium insights page with history support."""
    is_loading: bool = False
    is_downloading: bool = False
    error_message: str = ""
    
    # Selection Controls
    mode: str = "All Documents" # "All Documents" or "Single PDF"
    selected_file: str = ""
    available_files: list[str] = []
    
    # Historical tracking
    insights: list[InsightRecord] = []

    @rx.var
    def has_insights(self) -> bool:
        return len(self.insights) > 0

    @rx.var
    def is_single_mode(self) -> bool:
        return self.mode == "Single PDF"

    @rx.event
    def update_available_files(self):
        if os.path.exists(DOCUMENT_PATH):
            self.available_files = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith(('.pdf', '.txt'))]
            if not self.selected_file and self.available_files:
                self.selected_file = self.available_files[0]
        else:
            self.available_files = []

    @rx.event
    def handle_generate_insights(self):
        self.is_loading = True
        self.error_message = ""
        yield
        
        try:
            target_list = [self.selected_file] if self.mode == "Single PDF" else None
            data, _ = extract_insights(target_files=target_list)
            
            if "error" in data:
                self.error_message = data["error"]
            else:
                new_insight = InsightRecord(
                    timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    chart_type=data.get("chart_type", "bar"),
                    chart_title=data.get("title", "Document Strategic Analysis"),
                    explanation=data.get("explanation", "Data distribution overview."),
                    executive_summary=data.get("executive_summary", "Detailed strategic analysis."),
                    comparison_analysis=data.get("comparison_analysis", ""),
                    key_takeaways=data.get("key_takeaways", []),
                    key_concepts=data.get("key_concepts", [])
                )
                
                if "labels" in data and "values" in data:
                    new_insight.recharts_data = [
                        {"name": str(label), "value": float(value)} 
                        for label, value in zip(data["labels"], data["values"])
                    ]
                
                self.insights = [new_insight] + self.insights
                
        except Exception as e:
            self.error_message = f"Analysis error: {str(e)}"
        
        self.is_loading = False

    def clear_history(self):
        self.insights = []

    def download_report(self, insight: InsightRecord):
        """Generates and downloads a professional PDF report with a Matplotlib chart."""
        self.is_downloading = True
        yield

        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], spaceAfter=20, color=colors.HexColor("#1e293b"))
            sub_title_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], spaceAfter=12, color=colors.HexColor("#3b82f6"))
            body_style = styles['Normal']
            
            elements = []
            elements.append(Paragraph("DocuSearch AI - Strategic Insight Report", title_style))
            elements.append(Paragraph(f"Analysis: {insight.chart_title} ({insight.timestamp})", sub_title_style))
            elements.append(Spacer(1, 20))
            
            elements.append(Paragraph("Executive Summary", sub_title_style))
            elements.append(Paragraph(insight.executive_summary, body_style))
            elements.append(Spacer(1, 20))
            
            if insight.comparison_analysis:
                elements.append(Paragraph("Comparative Intelligence", sub_title_style))
                elements.append(Paragraph(insight.comparison_analysis, body_style))
                elements.append(Spacer(1, 20))

            if insight.recharts_data:
                chart_buffer = io.BytesIO()
                plt.figure(figsize=(6, 4))
                names = [d["name"] for d in insight.recharts_data]
                values = [d["value"] for d in insight.recharts_data]
                if insight.chart_type == "pie":
                    plt.pie(values, labels=names, autopct='%1.1f%%', colors=plt.cm.Paired.colors)
                elif insight.chart_type == "line":
                    plt.plot(names, values, marker='o', color='#6366f1', linewidth=2)
                else: plt.bar(names, values, color='#6366f1')
                plt.title(insight.chart_title)
                plt.tight_layout()
                plt.savefig(chart_buffer, format='png', dpi=150)
                plt.close()
                chart_buffer.seek(0)
                elements.append(Paragraph("Visual Analysis", sub_title_style))
                elements.append(Image(chart_buffer, width=400, height=250))
                elements.append(Spacer(1, 20))

            doc.build(elements)
            pdf_data = buffer.getvalue()
            buffer.close()
            self.is_downloading = False
            return rx.download(data=pdf_data, filename=f"Insight_{insight.timestamp.replace(' ', '_')}.pdf")
        except Exception as e:
            self.is_downloading = False

# --- UI Components ---

def premium_card(title, content, full_width=False, gradient=False):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(title, color="#1e293b", font_weight="700"),
                rx.spacer(),
                rx.icon(tag="info", color="#94a3b8"),
                width="100%",
                margin_bottom="15px"
            ),
            content,
        ),
        padding="24px",
        background="rgba(255, 255, 255, 0.8)" if not gradient else "linear-gradient(135deg, #eff6ff 0%, #ffffff 100%)",
        backdrop_filter="blur(10px)",
        border="1px solid rgba(226, 232, 240, 0.8)",
        border_radius="20px",
        box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02)",
        width="100%",
        grid_column="span 2" if full_width else "span 1",
        style={"_hover": {"transform": "translateY(-2px)", "box_shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"}, "transition": "all 0.3s"}
    )

def insight_session(insight: InsightRecord):
    return rx.vstack(
        rx.hstack(
            rx.icon(tag="calendar", color="#3b82f6"),
            rx.text(f"Session: {insight.timestamp}", font_weight="600", color="#3b82f6"),
            rx.spacer(),
            rx.button(
                rx.icon(tag="download"),
                "Download PDF Report",
                on_click=InsightsState.download_report(insight),
                variant="soft", color_scheme="blue"
            ),
            width="100%",
            margin_bottom="15px",
            background="rgba(59, 130, 246, 0.05)",
            padding="10px 20px",
            border_radius="10px"
        ),
        rx.box(
            premium_card("Executive Summary", rx.text(insight.executive_summary, color="#475569", font_size="17px", line_height="1.7"), full_width=True, gradient=True),
            
            rx.cond(
                insight.comparison_analysis != "",
                premium_card("Comparative Intelligence", 
                    rx.vstack(
                        rx.text(insight.comparison_analysis, color="#334155", font_weight="500", line_height="1.6"),
                        rx.badge("Cross-File Synthesis Active", color_scheme="green")
                    ),
                    full_width=True
                )
            ),

            premium_card(
                insight.chart_title,
                rx.vstack(
                    rx.match(
                        insight.chart_type,
                        ("pie", rx.recharts.pie_chart(
                            rx.recharts.pie(data=insight.recharts_data, data_key="value", name_key="name", label=True, fill="#6366f1"),
                            rx.recharts.legend(), rx.recharts.graphing_tooltip(), width="100%", height=300
                        )),
                        ("line", rx.recharts.line_chart(
                            rx.recharts.line(data_key="value", stroke="#6366f1", stroke_width=3),
                            rx.recharts.x_axis(data_key="name"), rx.recharts.y_axis(), rx.recharts.graphing_tooltip(),
                            data=insight.recharts_data, width="100%", height=300
                        )),
                        rx.recharts.bar_chart(
                            rx.recharts.bar(data_key="value", fill="#6366f1"),
                            rx.recharts.x_axis(data_key="name"), rx.recharts.y_axis(), rx.recharts.graphing_tooltip(),
                            data=insight.recharts_data, width="100%", height=300
                        )
                    ),
                    rx.text(insight.explanation, color="#94a3b8", font_size="14px", font_style="italic"),
                )
            ),

            premium_card("Strategic Takeaways",
                rx.vstack(
                    rx.foreach(insight.key_takeaways, lambda t: rx.hstack(
                        rx.icon(tag="check", color="#10b981"),
                        rx.text(t, color="#334155", font_weight="500"),
                        align="start", spacing="3"
                    )),
                    spacing="4", align="start"
                )
            ),

            premium_card("Semantic Concept Cloud",
                rx.flex(
                    rx.foreach(insight.key_concepts, lambda c: rx.badge(
                        c, color_scheme="blue"
                    )),
                    wrap="wrap", justify="center"
                ),
                full_width=True
            ),

            display="grid", grid_template_columns="repeat(2, 1fr)", gap="24px", width="100%",
        ),
        padding_y="40px", border_bottom="2px dashed #e2e8f0", width="100%"
    )

def skeleton_card():
    return rx.box(
        width="100%", height="300px", background="linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%)",
        background_size="200% 100%", animation="shimmer 2s infinite linear", border_radius="20px",
        style={"@keyframes shimmer": {"0%": {"background_position": "200% 0"}, "100%": {"background_position": "-200% 0"}}}
    )

def insights():
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.vstack(
                    rx.badge("Intelligence Suite", color_scheme="blue", variant="surface"),
                    rx.heading("Visual Insight Intelligence", color="#0f172a", font_weight="900"),
                    rx.text("Transform complex documents into actionable visual strategy.", color="#64748b", font_size="20px", max_width="600px", text_align="center"),
                    align_items="center", padding_y="60px", spacing="4", width="100%"
                ),
                
                # SELECTION PANEL - Centered explicitly
                rx.center(
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon(tag="settings_2", color="#6366f1"),
                                rx.heading("Analysis Parameters", color="#1e293b"),
                                spacing="2", align="center", margin_bottom="10px"
                            ),
                            # RESET to stable SELECT for mode choice
                            rx.select(
                                ["All Documents", "Single PDF"],
                                value=InsightsState.mode,
                                on_change=InsightsState.set_mode,
                                width="100%"
                            ),
                            rx.cond(
                                InsightsState.is_single_mode,
                                rx.vstack(
                                    rx.text("Select Target Document:", font_size="13px", font_weight="600", color="#64748b", margin_top="15px"),
                                    rx.select(
                                        InsightsState.available_files,
                                        value=InsightsState.selected_file,
                                        on_change=InsightsState.set_selected_file,
                                        width="100%"
                                    ),
                                    width="100%", align="start"
                                )
                            ),
                            rx.button(
                                rx.cond(InsightsState.is_loading, rx.spinner(), rx.icon(tag="bolt")),
                                rx.text("Generate Intelligence Report"),
                                on_click=InsightsState.handle_generate_insights,
                                color_scheme="blue", width="100%", margin_top="20px",
                                disabled=InsightsState.is_loading
                            ),
                            width="100%"
                        ),
                        padding="30px", background="white", border="1px solid #e2e8f0", border_radius="24px",
                        box_shadow="0 10px 40px -10px rgba(0,0,0,0.08)", width="100%", max_width="500px"
                    ),
                    width="100%",
                ),

                rx.cond(
                    InsightsState.has_insights,
                    rx.button(rx.icon(tag="trash"), "Clear History", on_click=InsightsState.clear_history, variant="soft", color_scheme="red", margin_top="20px")
                ),

                rx.cond(InsightsState.error_message != "",
                    rx.box(rx.hstack(rx.icon(tag="alert_triangle", color="#b45309"), rx.text(InsightsState.error_message, color="#92400e", font_weight="600")),
                        background="#fffbeb", border="1px solid #fef3c7", padding="16px 24px", border_radius="10px", margin_top="30px", width="100%")
                ),

                rx.cond(InsightsState.is_loading,
                    rx.grid(skeleton_card(), skeleton_card(), columns="2", spacing="6", width="100%", margin_top="40px")
                ),

                rx.vstack(rx.foreach(InsightsState.insights, insight_session), width="100%", margin_top="20px", margin_bottom="100px"),
                
                width="100%", max_width="1200px", align_items="center",
            )
        ),
        footer(), background="#f8fafc", min_height="100vh",
        on_mount=InsightsState.update_available_files
    )
