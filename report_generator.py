import os
from datetime import datetime
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


def _pdf_text(text):
    """Escape user text for ReportLab Paragraph XML markup."""
    return escape(text or "")


def generate_pdf_report(student_name, topic, transcript, reference_concept, audio_features, scoring_results, waveform_path, output_path):
    """
    Generates a beautifully styled, professional PDF evaluation report for the student.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        primary_color = colors.HexColor("#1A365D")    # Dark Navy
        secondary_color = colors.HexColor("#2B6CB0")  # Blue
        accent_teal = colors.HexColor("#319795")      # Teal
        dark_neutral = colors.HexColor("#2D3748")     # Slate Grey
        light_bg = colors.HexColor("#F7FAFC")         # Off-white
        border_color = colors.HexColor("#E2E8F0")     # Light Grey
        
        classification = scoring_results.get("classification", "Poor Understanding")
        if classification == "Strong Understanding":
            class_color = colors.HexColor("#22543D")  # Dark Green
            class_bg = colors.HexColor("#C6F6D5")     # Light Green
        elif classification == "Moderate Understanding":
            class_color = colors.HexColor("#744210") # Dark Orange/Brown
            class_bg = colors.HexColor("#FEFCBF")     # Light Yellow
        else:
            class_color = colors.HexColor("#742A2A") # Dark Red
            class_bg = colors.HexColor("#FED7D7")     # Light Red
            
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=primary_color,
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=secondary_color,
            spaceAfter=20
        )
        
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=dark_neutral,
            spaceAfter=10
        )
        
        bold_label_style = ParagraphStyle(
            'BoldLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=12,
            textColor=primary_color
        )
        
        value_style = ParagraphStyle(
            'ValueText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=12,
            textColor=dark_neutral
        )
        
        class_pill_style = ParagraphStyle(
            'ClassPill',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=class_color,
            alignment=1 # Center
        )
        
        score_text_style = ParagraphStyle(
            'ScoreText',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=20,
            textColor=primary_color,
            alignment=1 # Center
        )
        
        feedback_item_style = ParagraphStyle(
            'FeedbackItem',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=dark_neutral,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=5
        )
        
        story.append(Paragraph("Voice-Based Concept Understanding Analyser", title_style))
        story.append(Paragraph(f"VBCUA Academic & Practical Evaluation Report • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        metadata_data = [
            [Paragraph("Student Name:", bold_label_style), Paragraph(_pdf_text(student_name if student_name else "Anonymous Learner"), value_style),
             Paragraph("Topic / Concept:", bold_label_style), Paragraph(_pdf_text(topic), value_style)],
            [Paragraph("Audio Duration:", bold_label_style), Paragraph(f"{audio_features.get('duration', 0.0):.2f} seconds", value_style),
             Paragraph("Speaking Pace:", bold_label_style), Paragraph(f"{int(audio_features.get('wpm', 0)):d} WPM", value_style)],
        ]
        
        metadata_table = Table(metadata_data, colWidths=[1.25*inch, 2.25*inch, 1.25*inch, 2.25*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 15))
        
        score_data = [
            [
                Paragraph("OVERALL SCORE", ParagraphStyle('HScore', parent=bold_label_style, alignment=1, fontSize=8, textColor=colors.HexColor("#718096"))),
                Paragraph("SEMANTIC SIMILARITY", ParagraphStyle('HSem', parent=bold_label_style, alignment=1, fontSize=8, textColor=colors.HexColor("#718096"))),
                Paragraph("SPEAKING QUALITY", ParagraphStyle('HAud', parent=bold_label_style, alignment=1, fontSize=8, textColor=colors.HexColor("#718096"))),
                Paragraph("EVALUATION CLASSIFICATION", ParagraphStyle('HClass', parent=bold_label_style, alignment=1, fontSize=8, textColor=colors.HexColor("#718096")))
            ],
            [
                Paragraph(f"{scoring_results.get('overall_score', 0.0):.1f}%", score_text_style),
                Paragraph(f"{scoring_results.get('semantic_score', 0.0):.1f}%", score_text_style),
                Paragraph(f"{scoring_results.get('audio_score', 0.0):.1f}%", score_text_style),
                Paragraph(classification, class_pill_style)
            ]
        ]
        
        score_table = Table(score_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 2.2*inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 10),
            ('BACKGROUND', (0,0), (2,1), light_bg),
            ('BACKGROUND', (3,0), (3,0), light_bg),
            ('BACKGROUND', (3,1), (3,1), class_bg),
            ('BOX', (0,0), (-1,-1), 1, primary_color),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("Acoustic Feature Breakdown", h2_style))
        confidence_pct = audio_features.get("speech_confidence", 0.0) * 100.0
        rms_val = audio_features.get("rms_energy", 0.0)
        acoustic_data = [
            [Paragraph("Metric", bold_label_style), Paragraph("Value", bold_label_style), Paragraph("Benchmark", bold_label_style), Paragraph("Acoustic Rating", bold_label_style)],
            [
                Paragraph("Pause Ratio", value_style),
                Paragraph(f"{audio_features.get('pause_ratio', 0.0)*100:.1f}%", value_style),
                Paragraph("10% - 25%", value_style),
                Paragraph(f"{scoring_results.get('pause_score', 0.0):.1f}/100", value_style)
            ],
            [
                Paragraph("Pause Count", value_style),
                Paragraph(f"{audio_features.get('num_pauses', 0)}", value_style),
                Paragraph("Natural breaks", value_style),
                Paragraph("Info", value_style)
            ],
            [
                Paragraph("Speech Confidence", value_style),
                Paragraph(f"{confidence_pct:.1f}%", value_style),
                Paragraph("> 65%", value_style),
                Paragraph(f"{confidence_pct:.1f}/100", value_style)
            ],
            [
                Paragraph("RMS Energy (Loudness)", value_style),
                Paragraph(f"{rms_val:.4f}", value_style),
                Paragraph("Clear signal", value_style),
                Paragraph("Info", value_style)
            ],
            [
                Paragraph("Filler Word Ratio", value_style),
                Paragraph(f"{scoring_results.get('filler_ratio', 0.0):.1f}%", value_style),
                Paragraph("< 2.0%", value_style),
                Paragraph(f"{scoring_results.get('filler_score', 0.0):.1f}/100", value_style)
            ],
            [
                Paragraph("Speaking Rate", value_style),
                Paragraph(f"{int(audio_features.get('wpm', 0))} WPM", value_style),
                Paragraph("110 - 150 WPM", value_style),
                Paragraph(f"{scoring_results.get('speech_rate_score', 0.0):.1f}/100", value_style)
            ]
        ]
        
        acoustic_table = Table(acoustic_data, colWidths=[1.85*inch, 1.4*inch, 1.75*inch, 2.0*inch])
        acoustic_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
            ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ]))
        for i in range(4):
            acoustic_data[0][i].style.textColor = colors.white
            
        story.append(acoustic_table)
        story.append(Spacer(1, 15))
        
        if waveform_path and os.path.exists(waveform_path):
            story.append(Paragraph("Acoustic Waveform Visualization", h2_style))
            img = Image(waveform_path, width=7.0*inch, height=2.8*inch)
            story.append(img)
            story.append(Spacer(1, 15))
            
        story.append(Paragraph("Conceptual Content Comparison", h2_style))
        
        story.append(Paragraph("Student's Transcribed Explanation:", bold_label_style))
        transcript_display = _pdf_text(transcript) if transcript else "[No speech detected or transcribed]"
        story.append(Paragraph(f'<i>"{transcript_display}"</i>', ParagraphStyle('TranscriptItalic', parent=body_style, fontSize=9, textColor=colors.HexColor("#4A5568"))))

        story.append(Spacer(1, 5))
        story.append(Paragraph("Target Reference Concept Definition:", bold_label_style))
        story.append(Paragraph(_pdf_text(reference_concept), ParagraphStyle('RefText', parent=body_style, fontSize=9, textColor=colors.HexColor("#718096"))))
        
        story.append(Spacer(1, 10))
        story.append(Paragraph("AI Recommendations & Key Suggestions", h2_style))
        
        suggestions = scoring_results.get("suggestions", [])
        if suggestions:
            for sugg in suggestions:
                story.append(Paragraph(f"• {_pdf_text(sugg)}", feedback_item_style))
        else:
            story.append(Paragraph("No major criticisms. Your delivery was effective and conceptually comprehensive.", body_style))
            
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
