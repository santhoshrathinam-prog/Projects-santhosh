import os
import pathlib
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# ==============================================================================
# COLOR PALETTE (Modern Warm Architectural Theme - ZERO BLUE & BRIGHT NOT DARK)
# ==============================================================================
COLOR_PRIMARY         = RGBColor(194, 65, 12)     # #C2410C - Rich Burnt Terracotta / Construction Sienna
COLOR_PRIMARY_DARK    = RGBColor(154, 52, 10)     # #9A3412 - Deep Terracotta for bold main headers
COLOR_PRIMARY_LIGHT   = RGBColor(254, 237, 222)   # #FEedde - Warm Sandstone Tint for badge pills
COLOR_SECONDARY       = RGBColor(217, 119, 6)     # #D97706 - Warm Construction Amber / Ochre
COLOR_SECONDARY_LIGHT = RGBColor(254, 243, 199)   # #FEF3C7 - Warm Golden Cream
COLOR_BORDER_AMBER    = RGBColor(245, 158, 11)    # #F59E0B - Vibrant Amber Accent Border
COLOR_BG_CANVAS       = RGBColor(250, 247, 242)   # #FAF7F2 - Soft Luminous Architectural Ivory (NOT plain white, NOT dark)
COLOR_HDR_BAND        = RGBColor(245, 238, 227)   # #F5EEE3 - Warm Travertine Header Band
COLOR_CARD_BG         = RGBColor(255, 255, 255)   # #FFFFFF - Crisp Pure White Card
COLOR_CARD_BORDER     = RGBColor(243, 226, 203)   # #F3E2CB - Subtle Warm Sand Border
COLOR_TEXT_DARK       = RGBColor(28, 25, 23)      # #1C1917 - Warm High-Contrast Charcoal Black
COLOR_TEXT_MUTED      = RGBColor(87, 83, 78)      # #57534E - Stone Slate Gray for readable body text
COLOR_TEXT_LIGHT      = RGBColor(255, 255, 255)   # #FFFFFF - Pure White
COLOR_CODE_BG         = RGBColor(255, 251, 245)   # #FFFBF5 - Warm Parchment Code Background
COLOR_CODE_BORDER     = RGBColor(252, 211, 77)    # #FCD34D - Warm Amber Code Border
COLOR_SUCCESS         = RGBColor(22, 101, 52)     # #166534 - Forest Green Accent
COLOR_SUCCESS_LIGHT   = RGBColor(220, 252, 231)   # #DCFCE7 - Fresh Mint Tint

GITHUB_REPO_URL = "https://github.com/santhoshrathinam-prog/Projects-santhosh"
GITHUB_PROJECT_URL = "https://github.com/santhoshrathinam-prog/Projects-santhosh/tree/main/Build%20Track%20-%20Real%20Estate%20House%20Building%20Inventory%20and%20Progress%20Tracker"

SLIDE_WIDTH_INCHES  = 13.333
SLIDE_HEIGHT_INCHES = 7.5

DIAGRAMS_DIR = r"C:\Users\Santhosh Rathinam\.gemini\antigravity\scratch\real_estate_inventory\diagrams"

def init_presentation():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
    prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)
    return prs

# ==============================================================================
# UI HELPERS & MASTER BACKGROUND DESIGN
# ==============================================================================
def add_custom_textbox(slide, left, top, width, height, margin=0):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = margin
    return tb, tf

def apply_master_background(slide, is_cover=False, is_thankyou=False):
    # 1. Base Canvas (Warm Ivory/Sand Tint - bright, luminous, NOT plain white, NOT dark)
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SLIDE_WIDTH_INCHES), Inches(SLIDE_HEIGHT_INCHES))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = COLOR_BG_CANVAS
    bg_shape.line.fill.background()

    if is_cover or is_thankyou:
        c1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.5), Inches(-1.5), Inches(4.5), Inches(4.5))
        c1.fill.solid()
        c1.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
        c1.line.fill.background()

        c2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(-1.2), Inches(4.2), Inches(4.2))
        c2.fill.solid()
        c2.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
        c2.line.fill.background()

        c2_inner = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11.3), Inches(-0.4), Inches(2.3), Inches(2.3))
        c2_inner.fill.solid()
        c2_inner.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT
        c2_inner.line.color.rgb = COLOR_BORDER_AMBER
        c2_inner.line.width = Pt(1.5)

        c3 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.2), Inches(4.5), Inches(3.8), Inches(3.8))
        c3.fill.solid()
        c3.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
        c3.line.fill.background()

        c3_inner = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.4), Inches(5.4), Inches(2.2), Inches(2.2))
        c3_inner.fill.solid()
        c3_inner.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT
        c3_inner.line.color.rgb = COLOR_BORDER_AMBER
        c3_inner.line.width = Pt(1.5)

        frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.3), Inches(12.533), Inches(6.9))
        frame.fill.background()
        frame.line.color.rgb = COLOR_CARD_BORDER
        frame.line.width = Pt(1.5)
        return

    # Standard Content Slide Background Layout:
    strip_top = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.14), Inches(3.6))
    strip_top.fill.solid()
    strip_top.fill.fore_color.rgb = COLOR_PRIMARY
    strip_top.line.fill.background()

    strip_mid = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(3.6), Inches(0.14), Inches(0.8))
    strip_mid.fill.solid()
    strip_mid.fill.fore_color.rgb = COLOR_SECONDARY
    strip_mid.line.fill.background()

    strip_bot = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(4.4), Inches(0.14), Inches(3.1))
    strip_bot.fill.solid()
    strip_bot.fill.fore_color.rgb = COLOR_BORDER_AMBER
    strip_bot.line.fill.background()

    hdr_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.14), 0, Inches(13.193), Inches(1.62))
    hdr_bg.fill.solid()
    hdr_bg.fill.fore_color.rgb = COLOR_HDR_BAND
    hdr_bg.line.fill.background()

    acc1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11.6), Inches(-0.6), Inches(2.4), Inches(2.4))
    acc1.fill.solid()
    acc1.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    acc1.line.fill.background()

    acc2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.35), Inches(0.55), Inches(0.7), Inches(0.7))
    acc2.fill.solid()
    acc2.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT
    acc2.line.color.rgb = COLOR_BORDER_AMBER
    acc2.line.width = Pt(1.0)

    rule_g = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.62), Inches(8.5), Inches(0.04))
    rule_g.fill.solid()
    rule_g.fill.fore_color.rgb = COLOR_PRIMARY
    rule_g.line.fill.background()

    rule_a = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.3), Inches(1.62), Inches(3.233), Inches(0.04))
    rule_a.fill.solid()
    rule_a.fill.fore_color.rgb = COLOR_SECONDARY
    rule_a.line.fill.background()

    ftr_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.14), Inches(6.96), Inches(13.193), Inches(0.54))
    ftr_bg.fill.solid()
    ftr_bg.fill.fore_color.rgb = RGBColor(246, 240, 230)
    ftr_bg.line.fill.background()

    ftr_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.96), Inches(11.733), Inches(0.015))
    ftr_line.fill.solid()
    ftr_line.fill.fore_color.rgb = COLOR_CARD_BORDER
    ftr_line.line.fill.background()

    ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(12.1), Inches(5.3), Inches(1.8), Inches(1.8))
    ring.fill.background()
    ring.line.color.rgb = RGBColor(245, 230, 210)
    ring.line.width = Pt(1.0)

def create_base_slide(prs, is_cover=False, is_thankyou=False):
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_master_background(slide, is_cover=is_cover, is_thankyou=is_thankyou)
    return slide

def add_header(slide, tag_text, title_text, subtitle_text=None):
    tag_w = Inches(4.3) if len(tag_text) > 22 else Inches(3.2)
    tag_box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.8), Inches(0.36), tag_w, Inches(0.36)
    )
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT
    tag_box.line.color.rgb = COLOR_SECONDARY
    tag_box.line.width = Pt(1.2)
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    tf_tag.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_tag = tf_tag.paragraphs[0]
    p_tag.alignment = PP_ALIGN.CENTER
    r_tag = p_tag.add_run()
    r_tag.text = tag_text.upper()
    r_tag.font.name = 'Calibri'
    r_tag.font.size = Pt(10.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = COLOR_SECONDARY

    tb_title, tf_title = add_custom_textbox(slide, Inches(0.8), Inches(0.78), Inches(11.0), Inches(0.82))
    p_title = tf_title.paragraphs[0]
    r_title = p_title.add_run()
    r_title.text = title_text
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(22.5)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY_DARK

    if subtitle_text:
        p_sub = tf_title.add_paragraph()
        p_sub.space_before = Pt(2)
        r_sub = p_sub.add_run()
        r_sub.text = subtitle_text
        r_sub.font.name = 'Calibri'
        r_sub.font.size = Pt(11.5)
        r_sub.font.color.rgb = COLOR_TEXT_MUTED

def add_footer(slide, current_slide, total_slides=18):
    tb_left, tf_left = add_custom_textbox(slide, Inches(0.8), Inches(7.05), Inches(9.5), Inches(0.35))
    p_left = tf_left.paragraphs[0]

    r_dot = p_left.add_run()
    r_dot.text = "◆  "
    r_dot.font.name = 'Calibri'; r_dot.font.size = Pt(10); r_dot.font.bold = True; r_dot.font.color.rgb = COLOR_PRIMARY

    r_proj = p_left.add_run()
    r_proj.text = "BuildTrack – Real Estate House Building Inventory & Progress Tracker  |  MCA III Sem Viva Voce"
    r_proj.font.name = 'Calibri'; r_proj.font.size = Pt(10); r_proj.font.color.rgb = COLOR_TEXT_MUTED

    tb_right, tf_right = add_custom_textbox(slide, Inches(10.5), Inches(7.05), Inches(2.0), Inches(0.35))
    p_right = tf_right.paragraphs[0]
    p_right.alignment = PP_ALIGN.RIGHT
    r_cnt = p_right.add_run()
    r_cnt.text = f"{current_slide} / {total_slides}"
    r_cnt.font.name = 'Calibri'; r_cnt.font.size = Pt(11); r_cnt.font.bold = True; r_cnt.font.color.rgb = COLOR_PRIMARY

def add_elevated_card(slide, left, top, width, height, bg_color=None, border_color=None, border_width=1.0):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color if bg_color else COLOR_CARD_BG
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
    else:
        card.line.color.rgb = COLOR_CARD_BORDER
        card.line.width = Pt(border_width)
    return card

def add_bullet_item(tf, title, desc, space_after=Pt(3), font_size=Pt(10), bullet_char="•  "):
    p = tf.add_paragraph()
    p.space_before = Pt(2)
    p.space_after = space_after
    
    r_bullet = p.add_run()
    r_bullet.text = bullet_char
    r_bullet.font.name = 'Calibri'; r_bullet.font.size = font_size; r_bullet.font.bold = True; r_bullet.font.color.rgb = COLOR_PRIMARY
    
    r_t = p.add_run()
    r_t.text = f"{title}: "
    r_t.font.name = 'Calibri'; r_t.font.size = font_size; r_t.font.bold = True; r_t.font.color.rgb = COLOR_TEXT_DARK
    
    r_d = p.add_run()
    r_d.text = desc
    r_d.font.name = 'Calibri'; r_d.font.size = font_size; r_d.font.color.rgb = COLOR_TEXT_MUTED

def add_github_card(slide, left, top, width, height, sub_desc="Direct link to official open-source capstone repository:"):
    add_elevated_card(slide, left, top, width, height, border_color=COLOR_PRIMARY, border_width=1.5)
    tb, tf = add_custom_textbox(slide, left + Inches(0.2), top + Inches(0.12), width - Inches(0.4), height - Inches(0.24))

    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "OFFICIAL GITHUB PROJECT REPOSITORY"
    r1.font.name = 'Calibri'; r1.font.size = Pt(11); r1.font.bold = True; r1.font.color.rgb = COLOR_PRIMARY_DARK

    p2 = tf.add_paragraph()
    p2.space_before = Pt(2)
    r2 = p2.add_run()
    r2.text = sub_desc
    r2.font.name = 'Calibri'; r2.font.size = Pt(9); r2.font.color.rgb = COLOR_TEXT_MUTED

    # Dedicated Project Folder Link
    p3 = tf.add_paragraph()
    p3.space_before = Pt(3)
    r3_lbl = p3.add_run()
    r3_lbl.text = "[Project Folder]  "
    r3_lbl.font.name = 'Calibri'; r3_lbl.font.size = Pt(9.5); r3_lbl.font.bold = True; r3_lbl.font.color.rgb = COLOR_TEXT_DARK

    r3 = p3.add_run()
    if width > Inches(6.5):
        r3.text = GITHUB_PROJECT_URL
        r3.font.size = Pt(8.5)
    else:
        r3.text = "github.com/.../Build Track - Real Estate Inventory Tracker"
        r3.font.size = Pt(9)
    r3.font.name = 'Consolas'; r3.font.bold = True; r3.font.color.rgb = COLOR_PRIMARY
    r3.font.underline = True
    r3.hyperlink.address = GITHUB_PROJECT_URL

    # Full Main Repository Link
    p4 = tf.add_paragraph()
    p4.space_before = Pt(2)
    r4_lbl = p4.add_run()
    r4_lbl.text = "[Main Repo]      "
    r4_lbl.font.name = 'Calibri'; r4_lbl.font.size = Pt(9); r4_lbl.font.bold = True; r4_lbl.font.color.rgb = COLOR_TEXT_DARK

    r4 = p4.add_run()
    r4.text = GITHUB_REPO_URL
    r4.font.name = 'Consolas'; r4.font.size = Pt(9); r4.font.bold = True; r4.font.color.rgb = COLOR_SECONDARY
    r4.font.underline = True
    r4.hyperlink.address = GITHUB_REPO_URL

    p5 = tf.add_paragraph()
    p5.space_before = Pt(2)
    r5 = p5.add_run()
    r5.text = "* Complete Repository: Live Source Code, MySQL Schema, WebRTC Camera and Reports."
    r5.font.name = 'Calibri'; r5.font.size = Pt(8.5); r5.font.color.rgb = COLOR_TEXT_MUTED

def create_table_card(slide, left, top, width, height, headers, col_widths, rows_data):
    add_elevated_card(slide, left, top, width, height)
    tbl_shape = slide.shapes.add_table(len(rows_data) + 1, len(headers), left + Inches(0.12), top + Inches(0.12), width - Inches(0.24), height - Inches(0.24))
    tbl = tbl_shape.table
    
    for idx, w in enumerate(col_widths):
        tbl.columns[idx].width = w
        
    for idx, h_text in enumerate(headers):
        cell = tbl.cell(0, idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_PRIMARY_DARK
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = h_text
        r.font.name = 'Calibri'; r.font.size = Pt(10.5); r.font.bold = True; r.font.color.rgb = COLOR_TEXT_LIGHT
        
    for r_idx, row in enumerate(rows_data):
        row_bg = RGBColor(255, 255, 255) if r_idx % 2 == 0 else RGBColor(250, 246, 239)
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = row_bg
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            r = p.add_run()
            r.text = val
            r.font.name = 'Calibri'; r.font.size = Pt(9.5)
            if c_idx == 0:
                r.font.bold = True
                r.font.color.rgb = COLOR_TEXT_DARK
            else:
                r.font.color.rgb = COLOR_TEXT_MUTED
    return tbl_shape

# ==============================================================================
# SLIDE BUILDERS (1 TO 18)
# ==============================================================================

def build_slide_1(prs):
    """Slide 1: Cover Page (As per SRM Format with Blank Reserved Logo)"""
    slide = create_base_slide(prs, is_cover=True)

    # Master Elevated White Hero Card in Center
    add_elevated_card(slide, Inches(1.8), Inches(0.45), Inches(9.733), Inches(6.6),
                      bg_color=RGBColor(255, 255, 255), border_color=COLOR_PRIMARY, border_width=1.5)

    # Top Reserved Area for SRM Logo (User will paste official logo)
    logo_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.366), Inches(0.7), Inches(6.6), Inches(1.2))
    logo_card.fill.solid()
    logo_card.fill.fore_color.rgb = RGBColor(253, 248, 242)
    logo_card.line.color.rgb = COLOR_PRIMARY
    logo_card.line.width = Pt(1.2)
    
    tb_logo, tf_logo = add_custom_textbox(slide, Inches(3.366), Inches(0.8), Inches(6.6), Inches(1.0))
    p1 = tf_logo.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = "[ SPACE RESERVED FOR SRM ONLINE LOGO ]"
    r1.font.name = 'Calibri'; r1.font.size = Pt(13); r1.font.bold = True; r1.font.color.rgb = COLOR_PRIMARY
    
    p2 = tf_logo.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = "Candidate will paste the official SRM Online insignia here"
    r2.font.name = 'Calibri'; r2.font.size = Pt(10); r2.font.color.rgb = COLOR_TEXT_MUTED

    # Directorate & University Heading
    tb_univ, tf_univ = add_custom_textbox(slide, Inches(2.0), Inches(2.05), Inches(9.333), Inches(1.2))
    
    pu1 = tf_univ.paragraphs[0]
    pu1.alignment = PP_ALIGN.CENTER
    ru1 = pu1.add_run()
    ru1.text = "DIRECTORATE OF ONLINE EDUCATION"
    ru1.font.name = 'Calibri'; ru1.font.size = Pt(15.5); ru1.font.bold = True; ru1.font.color.rgb = COLOR_PRIMARY_DARK

    pu2 = tf_univ.add_paragraph()
    pu2.alignment = PP_ALIGN.CENTER
    ru2 = pu2.add_run()
    ru2.text = "SRM INSTITUTE OF SCIENCE AND TECHNOLOGY"
    ru2.font.name = 'Calibri'; ru2.font.size = Pt(21); ru2.font.bold = True; ru2.font.color.rgb = COLOR_PRIMARY_DARK

    pu3 = tf_univ.add_paragraph()
    pu3.alignment = PP_ALIGN.CENTER
    ru3 = pu3.add_run()
    ru3.text = "KATTANKULATHUR - 603 203"
    ru3.font.name = 'Calibri'; ru3.font.size = Pt(12.5); ru3.font.bold = True; ru3.font.color.rgb = COLOR_TEXT_MUTED

    # Decorative Accent Bar
    dec_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.666), Inches(3.35), Inches(4.0), Inches(0.04))
    dec_line.fill.solid()
    dec_line.fill.fore_color.rgb = COLOR_SECONDARY
    dec_line.line.fill.background()

    # Viva Voce Details
    tb_viva, tf_viva = add_custom_textbox(slide, Inches(2.0), Inches(3.55), Inches(9.333), Inches(1.5))

    pv1 = tf_viva.paragraphs[0]
    pv1.alignment = PP_ALIGN.CENTER
    rv1 = pv1.add_run()
    rv1.text = "MCA III SEMESTER"
    rv1.font.name = 'Calibri'; rv1.font.size = Pt(14); rv1.font.bold = True; rv1.font.color.rgb = COLOR_SECONDARY

    pv2 = tf_viva.add_paragraph()
    pv2.alignment = PP_ALIGN.CENTER
    rv2 = pv2.add_run()
    rv2.text = "INTERNSHIP VIVA VOCE"
    rv2.font.name = 'Calibri'; rv2.font.size = Pt(25); rv2.font.bold = True; rv2.font.color.rgb = COLOR_PRIMARY_DARK

    pv3 = tf_viva.add_paragraph()
    pv3.alignment = PP_ALIGN.CENTER
    rv3 = pv3.add_run()
    rv3.text = "NOV 2026"
    rv3.font.name = 'Calibri'; rv3.font.size = Pt(14); rv3.font.bold = True; rv3.font.color.rgb = COLOR_TEXT_DARK

    # Student Identification Card with GitHub Project Link
    card_stu = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.2), Inches(5.15), Inches(8.933), Inches(1.65))
    card_stu.fill.solid()
    card_stu.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    card_stu.line.color.rgb = COLOR_PRIMARY
    card_stu.line.width = Pt(1.5)

    tb_stu, tf_stu = add_custom_textbox(slide, Inches(2.2), Inches(5.22), Inches(8.933), Inches(1.5))

    ps1 = tf_stu.paragraphs[0]
    ps1.alignment = PP_ALIGN.CENTER
    rs1 = ps1.add_run()
    rs1.text = "NAME OF STUDENT :  SANTHOSH RATHINAM M"
    rs1.font.name = 'Calibri'; rs1.font.size = Pt(15); rs1.font.bold = True; rs1.font.color.rgb = COLOR_TEXT_DARK

    ps2 = tf_stu.add_paragraph()
    ps2.alignment = PP_ALIGN.CENTER
    rs2 = ps2.add_run()
    rs2.text = "ENROLMENT NUMBER :  EA2532251010685"
    rs2.font.name = 'Calibri'; rs2.font.size = Pt(14); rs2.font.bold = True; rs2.font.color.rgb = COLOR_PRIMARY_DARK

    ps3 = tf_stu.add_paragraph()
    ps3.space_before = Pt(3)
    ps3.alignment = PP_ALIGN.CENTER
    rs3_lbl = ps3.add_run()
    rs3_lbl.text = "OFFICIAL GITHUB REPOSITORY :  "
    rs3_lbl.font.name = 'Calibri'; rs3_lbl.font.size = Pt(10.5); rs3_lbl.font.bold = True; rs3_lbl.font.color.rgb = COLOR_PRIMARY_DARK
    rs3 = ps3.add_run()
    rs3.text = GITHUB_REPO_URL
    rs3.font.name = 'Consolas'; rs3.font.size = Pt(11); rs3.font.bold = True; rs3.font.color.rgb = COLOR_PRIMARY
    rs3.font.underline = True
    rs3.hyperlink.address = GITHUB_PROJECT_URL

def build_slide_2(prs):
    """Slide 2: Project Overview & Scope"""
    slide = create_base_slide(prs)
    add_header(slide, "PROJECT OVERVIEW", "Title of the Internship Project",
               "Digital residential house building inventory and physical milestone management platform")
    add_footer(slide, 2)

    # Hero Title Banner Card
    add_elevated_card(slide, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.2),
                      bg_color=RGBColor(255, 255, 255), border_color=COLOR_PRIMARY, border_width=1.5)
    
    tb_hero, tf_hero = add_custom_textbox(slide, Inches(1.1), Inches(1.95), Inches(11.133), Inches(1.9))
    
    p_badge = tf_hero.paragraphs[0]
    r_b = p_badge.add_run()
    r_b.text = "FULL-STACK RESIDENTIAL CONSTRUCTION MANAGEMENT PLATFORM"
    r_b.font.name = 'Calibri'; r_b.font.size = Pt(11); r_b.font.bold = True; r_b.font.color.rgb = COLOR_SECONDARY

    p_t = tf_hero.add_paragraph()
    p_t.space_before = Pt(3)
    r_t = p_t.add_run()
    r_t.text = "BUILD TRACK"
    r_t.font.name = 'Calibri'; r_t.font.size = Pt(28); r_t.font.bold = True; r_t.font.color.rgb = COLOR_PRIMARY_DARK

    p_st = tf_hero.add_paragraph()
    r_st = p_st.add_run()
    r_st.text = "Real Estate House Building Inventory and Progress Tracker"
    r_st.font.name = 'Calibri'; r_st.font.size = Pt(15); r_st.font.bold = True; r_st.font.color.rgb = COLOR_TEXT_DARK

    p_desc = tf_hero.add_paragraph()
    p_desc.space_before = Pt(4)
    r_d = p_desc.add_run()
    r_d.text = (
        "An enterprise-grade web application engineered for residential builders, site engineers, and project contractors "
        "to track raw building materials, enforce atomic database row locking, verify physical milestone progress, "
        "and validate job-site events via live camera photo proof."
    )
    r_d.font.name = 'Calibri'; r_d.font.size = Pt(11); r_d.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Grid: 4 Scope & Intended Deliverables Cards
    w_card = Inches(2.78)
    h_card = Inches(2.65)
    gap_x  = Inches(0.204)
    y_top  = Inches(4.15)

    deliverables = [
        ("Multi-Plot Housing Portfolio",
         "Tracks concurrent residential plots and villas through an 8-stage civil engineering lifecycle (Excavation to Finishing) with dynamic percentage recalculation.",
         "01", COLOR_PRIMARY),
        ("Materials Catalog & Alerts",
         "Centralized catalog of 95+ construction commodities across 8 categories with automated minimum threshold warnings and inward delivery logs.",
         "02", COLOR_SECONDARY),
        ("ACID Concurrency Protection",
         "MySQL InnoDB pessimistic row locking (SELECT ... FOR UPDATE) preventing stock overselling and race conditions during simultaneous material requisitions.",
         "03", COLOR_BORDER_AMBER),
        ("Field Camera Verification",
         "HTML5 WebRTC in-browser camera hardware access enabling site engineers to capture authentic, live photo proof before milestone sign-off.",
         "04", COLOR_PRIMARY_DARK)
    ]

    for idx, (title, desc, num_str, accent_color) in enumerate(deliverables):
        x_pos = Inches(0.8) + idx * (w_card + gap_x)
        add_elevated_card(slide, x_pos, y_top, w_card, h_card)

        # Top Accent Header Bar inside card
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.12), y_top + Inches(0.12), w_card - Inches(0.24), Inches(0.38))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
        top_bar.line.fill.background()
        tf_tb = top_bar.text_frame
        p_tb = tf_tb.paragraphs[0]
        p_tb.alignment = PP_ALIGN.LEFT
        r_tb = p_tb.add_run()
        r_tb.text = f"SCOPE DELIVERABLE {num_str}"
        r_tb.font.name = 'Calibri'; r_tb.font.size = Pt(9.5); r_tb.font.bold = True; r_tb.font.color.rgb = accent_color

        tb_c, tf_c = add_custom_textbox(slide, x_pos + Inches(0.15), y_top + Inches(0.58), w_card - Inches(0.3), h_card - Inches(0.7))
        p_ct = tf_c.paragraphs[0]
        r_ct = p_ct.add_run()
        r_ct.text = title
        r_ct.font.name = 'Calibri'; r_ct.font.size = Pt(13); r_ct.font.bold = True; r_ct.font.color.rgb = COLOR_TEXT_DARK

        p_cd = tf_c.add_paragraph()
        p_cd.space_before = Pt(4)
        r_cd = p_cd.add_run()
        r_cd.text = desc
        r_cd.font.name = 'Calibri'; r_cd.font.size = Pt(10.5); r_cd.font.color.rgb = COLOR_TEXT_MUTED

def build_slide_3(prs):
    """Slide 3: Abstract (What the Project Solves and Delivers)"""
    slide = create_base_slide(prs)
    add_header(slide, "ABSTRACT", "What the Project Solves and Delivers",
               "Modernizing residential construction management with digital inventory tracking and verified milestone execution")
    add_footer(slide, 3)

    w_card = Inches(3.75)
    h_card = Inches(4.25)
    gap_x  = Inches(0.24)
    y_top  = Inches(1.85)

    # 1. The Problem Card
    c1 = add_elevated_card(slide, Inches(0.8), y_top, w_card, h_card, border_color=COLOR_PRIMARY, border_width=1.5)
    tb1, tf1 = add_custom_textbox(slide, Inches(1.0), y_top + Inches(0.2), w_card - Inches(0.4), h_card - Inches(0.4))
    p1 = tf1.paragraphs[0]; r1 = p1.add_run(); r1.text = "1. THE PROBLEM"; r1.font.name = 'Calibri'; r1.font.size = Pt(14); r1.font.bold = True; r1.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf1, "Manual Paper Registers", "Fragile paper logbooks kept in dusty site sheds cause missing entries and month-end discrepancies.")
    add_bullet_item(tf1, "Costly Material Theft & Spoilage", "Unmonitored theft of steel rebar, cement hardening, and untracked wastage waste 6% to 8% of project budget.")
    add_bullet_item(tf1, "Information Vacuum", "Head office executives learn of material shortages or project stalls days after they occur.")
    add_bullet_item(tf1, "Unverified Stage Claims", "Contractors verbally claim phase completions without timestamped visual proof.")

    # 2. The Solution Card
    x2 = Inches(0.8) + w_card + gap_x
    c2 = add_elevated_card(slide, x2, y_top, w_card, h_card, border_color=COLOR_SECONDARY, border_width=1.5)
    tb2, tf2 = add_custom_textbox(slide, x2 + Inches(0.2), y_top + Inches(0.2), w_card - Inches(0.4), h_card - Inches(0.4))
    p2 = tf2.paragraphs[0]; r2 = p2.add_run(); r2.text = "2. THE SOLUTION"; r2.font.name = 'Calibri'; r2.font.size = Pt(14); r2.font.bold = True; r2.font.color.rgb = COLOR_SECONDARY
    add_bullet_item(tf2, "Centralized Web Platform", "Role-based portals for Project Administrators, Builders, and Site Engineers.")
    add_bullet_item(tf2, "Pessimistic Row Locking", "Database-level concurrency control (SELECT ... FOR UPDATE) guarantees zero negative stock.")
    add_bullet_item(tf2, "WebRTC Live Photo Capture", "Browser-driven camera streaming captures authentic on-site milestone progress proof.")
    add_bullet_item(tf2, "Empirical Civil Estimator", "Mathematical algorithms calculate theoretical material requirements based on built-up square footage.")

    # 3. Expected Value Card
    x3 = x2 + w_card + gap_x
    c3 = add_elevated_card(slide, x3, y_top, w_card, h_card, border_color=COLOR_BORDER_AMBER, border_width=1.5)
    tb3, tf3 = add_custom_textbox(slide, x3 + Inches(0.2), y_top + Inches(0.2), w_card - Inches(0.4), h_card - Inches(0.4))
    p3 = tf3.paragraphs[0]; r3 = p3.add_run(); r3.text = "3. EXPECTED VALUE"; r3.font.name = 'Calibri'; r3.font.size = Pt(14); r3.font.bold = True; r3.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf3, "-15% Material Wastage", "Eliminates over-ordering and undetected job-site pilferage.")
    add_bullet_item(tf3, "100% Data Accuracy", "Complete elimination of double-allocation race conditions during rapid dispatches.")
    add_bullet_item(tf3, "Real-Time Site Telemetry", "Instant transparency across all active residential housing plots.")
    add_bullet_item(tf3, "Single Source of Truth", "Automated PDF progress summaries, material balance sheets, and audit ledgers.")

    # Bottom Scope & Deliverable Ribbon
    ribbon = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.55))
    ribbon.fill.solid()
    ribbon.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    ribbon.line.color.rgb = COLOR_PRIMARY
    ribbon.line.width = Pt(1.0)
    tf_r = ribbon.text_frame
    p_r = tf_r.paragraphs[0]
    p_r.alignment = PP_ALIGN.CENTER
    r_r1 = p_r.add_run()
    r_r1.text = "Main Deliverable & Project Boundary: "
    r_r1.font.name = 'Calibri'; r_r1.font.size = Pt(11); r_r1.font.bold = True; r_r1.font.color.rgb = COLOR_PRIMARY_DARK
    r_r2 = p_r.add_run()
    r_r2.text = "Full-stack responsive web management information system built with Python 3.12, Flask 3.0.3, MySQL 8.0 InnoDB, HTML5 WebRTC, and Bootstrap 5.3."
    r_r2.font.name = 'Calibri'; r_r2.font.size = Pt(11); r_r2.font.color.rgb = COLOR_TEXT_DARK

def build_slide_4(prs):
    """Slide 4: Introduction (Why This Problem Matters)"""
    slide = create_base_slide(prs)
    add_header(slide, "INTRODUCTION", "Why This Problem Matters",
               "Eliminating costly inventory shrinkage and milestone blind spots in residential real estate")
    add_footer(slide, 4)

    w_col = Inches(5.72)
    h_col = Inches(4.85)
    gap_x = Inches(0.293)
    y_top = Inches(1.85)

    # Left: Background & Industry Context
    c_left = add_elevated_card(slide, Inches(0.8), y_top, w_col, h_col)
    top_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_top, w_col, Inches(0.42))
    top_l.fill.solid(); top_l.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; top_l.line.fill.background()
    p_tl = top_l.text_frame.paragraphs[0]; r_tl = p_tl.add_run(); r_tl.text = "BACKGROUND & REAL ESTATE CONTEXT"
    r_tl.font.name = 'Calibri'; r_tl.font.size = Pt(11); r_tl.font.bold = True; r_tl.font.color.rgb = COLOR_PRIMARY_DARK

    tb_l, tf_l = add_custom_textbox(slide, Inches(1.0), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    add_bullet_item(tf_l, "Massive Capital Investment",
                    "Raw building materials constitute 55% to 65% of the total residential house construction expenditure, making material control vital to builder survival.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Highly Perishable Commodities",
                    "Ordinary Portland Cement (OPC) hardens and spoils in humid weather within weeks, while steel rebar corrodes if stored without cover.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Geographically Scattered Sites",
                    "Residential housing projects, villas, and row plots are physically dispersed across suburban layouts, making direct central supervision impractical.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Manual Communication Delays",
                    "Traditional sites rely on paper registers, informal phone calls, and WhatsApp groups, causing severe information lag between job sites and management.",
                    space_after=Pt(8), font_size=Pt(10.5))

    # Right: Current Limitations & Project Objectives
    x_r = Inches(0.8) + w_col + gap_x
    c_right = add_elevated_card(slide, x_r, y_top, w_col, h_col)
    top_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_r, y_top, w_col, Inches(0.42))
    top_r.fill.solid(); top_r.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT; top_r.line.fill.background()
    p_tr = top_r.text_frame.paragraphs[0]; r_tr = p_tr.add_run(); r_tr.text = "CURRENT LIMITATIONS & PROJECT OBJECTIVES"
    r_tr.font.name = 'Calibri'; r_tr.font.size = Pt(11); r_tr.font.bold = True; r_tr.font.color.rgb = COLOR_SECONDARY

    tb_r, tf_r = add_custom_textbox(slide, x_r + Inches(0.2), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    add_bullet_item(tf_r, "Legacy Limitations",
                    "Zero automated audit trails, manual estimation guesswork, and lack of visual proof allow undetected pilferage and delayed project handovers.",
                    space_after=Pt(6), font_size=Pt(10))
    add_bullet_item(tf_r, "Project Objective 1 (Centralized Ledger)",
                    "Build a unified web-based material registry tracking 95+ construction commodities across 8 categories with automated low-stock warnings.",
                    space_after=Pt(6), font_size=Pt(10))
    add_bullet_item(tf_r, "Project Objective 2 (Milestone Tracker)",
                    "Digitize the 8-stage civil engineering lifecycle with dynamic percentage recalculation and multi-plot portfolio oversight.",
                    space_after=Pt(6), font_size=Pt(10))
    add_bullet_item(tf_r, "Project Objective 3 (Live Camera Proof)",
                    "Integrate HTML5 WebRTC browser camera APIs requiring site supervisors to submit genuine live photographs before milestone approval.",
                    space_after=Pt(6), font_size=Pt(10))
    add_bullet_item(tf_r, "Project Objective 4 (Pessimistic Concurrency)",
                    "Implement MySQL InnoDB row-level locking (SELECT ... FOR UPDATE) to eliminate race conditions and prevent negative stock balances.",
                    space_after=Pt(6), font_size=Pt(10))

def build_slide_5(prs):
    """Slide 5: System Capabilities / Key Features"""
    slide = create_base_slide(prs)
    add_header(slide, "CAPABILITIES", "Key Features of BuildTrack",
               "Tailored operational portals for Administrators, Builders, Site Engineers, and Auditors")
    add_footer(slide, 5)

    w_card = Inches(5.72)
    h_card = Inches(2.32)
    gap_x  = Inches(0.293)
    gap_y  = Inches(0.20)
    y1     = Inches(1.85)
    y2     = y1 + h_card + gap_y

    features = [
        # Card 1: Admin
        ("1. PROJECT ADMINISTRATOR PORTAL", Inches(0.8), y1, [
            ("Master Materials Catalog", "Full CRUD management of 95+ construction items, standard rates, and safety thresholds."),
            ("Project Provisioning", "Register new residential housing plots, configure built-up square footage, and assign site engineers."),
            ("Administrative Approval Queue", "Dual-checkpoint verification queue to review and approve site material consumption and stage progress.")
        ], COLOR_PRIMARY),
        # Card 2: Builder
        ("2. BUILDER & CONTRACTOR DASHBOARD", Inches(0.8) + w_card + gap_x, y1, [
            ("Multi-Plot Milestone Tracking", "Real-time visibility into active housing plots with dynamic cumulative completion percentage bars."),
            ("Civil Stage Lifecycle", "Track 8 chronological stages: Excavation -> Foundation -> Plinth -> Masonry -> Slab -> Finishing."),
            ("Budget & Variance Monitoring", "Continuously compare allocated material expenditures against approved architectural budgets.")
        ], COLOR_SECONDARY),
        # Card 3: Site Engineer
        ("3. SITE ENGINEER FIELD OPERATIONS", Inches(0.8), y2, [
            ("Mobile-Responsive Site Portal", "Touch-friendly interface optimized for low-bandwidth 4G field conditions and smartphones."),
            ("Daily Consumption Logging", "Record exact quantities of cement, steel, and sand utilized on specific structural tasks."),
            ("Inward Delivery Challans", "Log supplier name, delivery vehicle number (e.g. TN-38-BZ-4412), challan number, and delivery photo.")
        ], COLOR_BORDER_AMBER),
        # Card 4: Civil Estimator & Audit
        ("4. CIVIL ESTIMATOR & AUDIT ENGINE", Inches(0.8) + w_card + gap_x, y2, [
            ("Empirical Civil Calculators", "Dynamically estimate required cement bags, steel rebar, and aggregate based on built-up square feet."),
            ("WebRTC Camera Proof", "Direct browser camera access to snapshot live, tamper-proof job-site milestone photos."),
            ("Executive Export & Audit", "Compile publication-grade PDF progress reports and CSV transaction ledgers for external audit.")
        ], COLOR_PRIMARY_DARK)
    ]

    for title, x_pos, y_pos, bullets, accent_col in features:
        add_elevated_card(slide, x_pos, y_pos, w_card, h_card)
        
        # Header strip
        h_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.12), y_pos + Inches(0.12), w_card - Inches(0.24), Inches(0.35))
        h_strip.fill.solid(); h_strip.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; h_strip.line.fill.background()
        p_hs = h_strip.text_frame.paragraphs[0]; r_hs = p_hs.add_run(); r_hs.text = title
        r_hs.font.name = 'Calibri'; r_hs.font.size = Pt(10.5); r_hs.font.bold = True; r_hs.font.color.rgb = accent_col

        tb, tf = add_custom_textbox(slide, x_pos + Inches(0.2), y_pos + Inches(0.52), w_card - Inches(0.4), h_card - Inches(0.6))
        for b_title, b_desc in bullets:
            add_bullet_item(tf, b_title, b_desc, space_after=Pt(2), font_size=Pt(9.5))

def build_slide_6(prs):
    """Slide 6: Implementation Environment (System Requirements)"""
    slide = create_base_slide(prs)
    add_header(slide, "IMPLEMENTATION ENVIRONMENT", "System Hardware & Software Requirements",
               "Workstation specifications and software stack used for development and evaluation")
    add_footer(slide, 6)

    w_tbl = Inches(5.72)
    h_tbl = Inches(4.85)
    gap_x = Inches(0.293)
    y_top = Inches(1.85)

    hw_headers = ["Hardware Component", "Requirement / Specification"]
    hw_widths = [Inches(2.3), Inches(3.18)]
    hw_data = [
        ["Processor", "Intel Core i3 / AMD Ryzen 3 or higher (2.4 GHz Dual-Core)"],
        ["Primary RAM", "4 GB RAM minimum (8 GB recommended for multi-user tests)"],
        ["Hard Disk", "20 GB free storage for relational database and image assets"],
        ["Webcam / Camera", "Integrated laptop webcam or mobile 720p/1080p camera peripheral"],
        ["Display Monitor", "1366 x 768 resolution or higher (1080p Full HD optimal)"],
        ["Input Devices", "Standard keyboard and mouse / responsive mobile touchscreen"],
        ["Network Adapter", "Standard 100/1000 Mbps Ethernet / 4G cellular connection"]
    ]
    create_table_card(slide, Inches(0.8), y_top, w_tbl, h_tbl, hw_headers, hw_widths, hw_data)

    sw_headers = ["Software Component", "Selection & Engineering Version"]
    sw_widths = [Inches(2.3), Inches(3.18)]
    sw_data = [
        ["Operating System", "Microsoft Windows 10 / Windows 11 (64-bit) / Ubuntu Linux"],
        ["Backend Language", "Python 3.12 (64-bit CPython with strict type hints)"],
        ["Web Framework", "Flask 3.0.3 (WSGI architecture, Werkzeug security, Jinja2)"],
        ["Relational Database", "MySQL Community Server 8.0 (InnoDB ACID Engine, Row Locking)"],
        ["Frontend Stack", "HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4"],
        ["PDF Generation Engine", "ReportLab 5.0.1 (Automated multi-page document compiler)"],
        ["Development Tools", "Visual Studio Code 1.88+, MySQL Workbench 8.0, Windows PowerShell"]
    ]
    create_table_card(slide, Inches(0.8) + w_tbl + gap_x, y_top, w_tbl, h_tbl, sw_headers, sw_widths, sw_data)

def build_slide_7(prs):
    """Slide 7: Critical Analysis (Existing System and Gaps)"""
    slide = create_base_slide(prs)
    add_header(slide, "CURRENT APPROACH", "Existing System and Its Structural Gaps",
               "Why traditional construction site practices cause massive delays and financial leakage")
    add_footer(slide, 7)

    # 3 Sequential Stages of Existing Workflow
    w_step = Inches(3.75)
    h_step = Inches(1.8)
    gap_x  = Inches(0.24)
    y_step = Inches(1.85)

    steps = [
        ("01", "CURRENT INPUT: PAPER REGISTERS",
         "Incoming material deliveries are recorded on loose paper challans and physical logbooks in temporary on-site sheds, vulnerable to damage and loss.",
         COLOR_PRIMARY),
        ("02", "CURRENT PROCESSING: MANUAL CALLS",
         "Daily site usage is communicated via verbal phone calls and ad-hoc messaging; head office records are updated days later through static spreadsheets.",
         COLOR_SECONDARY),
        ("03", "CURRENT OUTPUT: DELAYED RECONCILIATION",
         "Project directors discover material overruns, theft, and stage delays only during end-of-month accounting reconciliations, after costs are irreversible.",
         COLOR_BORDER_AMBER)
    ]

    for idx, (num, title, desc, col) in enumerate(steps):
        x_pos = Inches(0.8) + idx * (w_step + gap_x)
        add_elevated_card(slide, x_pos, y_step, w_step, h_step)
        
        # Step number circle badge
        c_num = slide.shapes.add_shape(MSO_SHAPE.OVAL, x_pos + Inches(0.18), y_step + Inches(0.18), Inches(0.42), Inches(0.42))
        c_num.fill.solid(); c_num.fill.fore_color.rgb = col; c_num.line.fill.background()
        tf_cn = c_num.text_frame; p_cn = tf_cn.paragraphs[0]; p_cn.alignment = PP_ALIGN.CENTER
        r_cn = p_cn.add_run(); r_cn.text = num; r_cn.font.name = 'Calibri'; r_cn.font.size = Pt(11); r_cn.font.bold = True; r_cn.font.color.rgb = COLOR_TEXT_LIGHT

        tb_s, tf_s = add_custom_textbox(slide, x_pos + Inches(0.68), y_step + Inches(0.15), w_step - Inches(0.8), h_step - Inches(0.3))
        p_st = tf_s.paragraphs[0]; r_st = p_st.add_run(); r_st.text = title; r_st.font.name = 'Calibri'; r_st.font.size = Pt(10.5); r_st.font.bold = True; r_st.font.color.rgb = COLOR_TEXT_DARK
        p_sd = tf_s.add_paragraph(); p_sd.space_before = Pt(3); r_sd = p_sd.add_run(); r_sd.text = desc; r_sd.font.name = 'Calibri'; r_sd.font.size = Pt(9.5); r_sd.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom: 4 Structural Gaps Cards
    w_gap = Inches(5.72)
    h_gap = Inches(1.35)
    gap_y = Inches(0.18)
    y_gap = Inches(3.85)

    gaps = [
        ("Gap 1: Disproportionate Material Wastage & Theft",
         "Unmonitored theft of high-value steel rebar, electrical wiring, and cement bags eats 6% to 8% of total contractor margins with zero forensic audit trails.",
         Inches(0.8), y_gap, COLOR_PRIMARY),
        ("Gap 2: Absence of Scientific Estimation",
         "Field supervisors order raw materials based on rough guesses rather than empirical mathematical civil engineering norms, causing emergency stockouts.",
         Inches(0.8) + w_gap + Inches(0.293), y_gap, COLOR_SECONDARY),
        ("Gap 3: Concurrency Race Conditions in Spreadsheets",
         "Multiple site supervisors requesting stock simultaneously leads to double-allocation and negative warehouse balances across active plots.",
         Inches(0.8), y_gap + h_gap + gap_y, COLOR_BORDER_AMBER),
        ("Gap 4: Zero Live Photographic Verification",
         "Milestone handovers are certified without tamper-proof visual evidence, leading to subcontractor disputes, structural defects, and client distrust.",
         Inches(0.8) + w_gap + Inches(0.293), y_gap + h_gap + gap_y, COLOR_PRIMARY_DARK)
    ]

    for title, desc, gx, gy, gcol in gaps:
        add_elevated_card(slide, gx, gy, w_gap, h_gap, border_color=gcol, border_width=1.2)
        tb_g, tf_g = add_custom_textbox(slide, gx + Inches(0.2), gy + Inches(0.15), w_gap - Inches(0.4), h_gap - Inches(0.3))
        p_gt = tf_g.paragraphs[0]; r_gt = p_gt.add_run(); r_gt.text = title; r_gt.font.name = 'Calibri'; r_gt.font.size = Pt(11.5); r_gt.font.bold = True; r_gt.font.color.rgb = gcol
        p_gd = tf_g.add_paragraph(); p_gd.space_before = Pt(3); r_gd = p_gd.add_run(); r_gd.text = desc; r_gd.font.name = 'Calibri'; r_gd.font.size = Pt(10); r_gd.font.color.rgb = COLOR_TEXT_MUTED

def build_slide_8(prs):
    """Slide 8: Proposed Approach (How the Proposed System Improves the Process)"""
    slide = create_base_slide(prs)
    add_header(slide, "PROPOSED APPROACH", "How the Proposed System Improves the Process",
               "A synchronized, verified, and automated digital pipeline between sites and management")
    add_footer(slide, 8)

    w_step = Inches(3.75)
    h_step = Inches(2.2)
    gap_x  = Inches(0.24)
    y_step = Inches(1.85)

    stages = [
        ("STAGE 1: INPUT STAGE", "Mobile Field Logging",
         "Site engineer logs daily material consumption on mobile device; inputs inward supplier challan with vehicle number; captures live camera photo proof.",
         COLOR_PRIMARY),
        ("STAGE 2: PROCESSING STAGE", "Automated Validation",
         "Flask backend validates user session, coordinates MySQL connection pool, and executes pessimistic row locks (SELECT ... FOR UPDATE) to prevent overselling.",
         COLOR_SECONDARY),
        ("STAGE 3: OUTPUT STAGE", "Instant Transparency",
         "Warehouse inventory deducted in real time; cumulative stage progress recalculated; dynamic low-stock alerts triggered; executive PDF reports compiled.",
         COLOR_SUCCESS)
    ]

    for idx, (stage_lbl, title, desc, col) in enumerate(stages):
        x_pos = Inches(0.8) + idx * (w_step + gap_x)
        add_elevated_card(slide, x_pos, y_step, w_step, h_step, border_color=col, border_width=1.5)

        h_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.12), y_step + Inches(0.12), w_step - Inches(0.24), Inches(0.35))
        h_bar.fill.solid(); h_bar.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; h_bar.line.fill.background()
        p_hb = h_bar.text_frame.paragraphs[0]; r_hb = p_hb.add_run(); r_hb.text = stage_lbl
        r_hb.font.name = 'Calibri'; r_hb.font.size = Pt(10); r_hb.font.bold = True; r_hb.font.color.rgb = col

        tb, tf = add_custom_textbox(slide, x_pos + Inches(0.2), y_step + Inches(0.55), w_step - Inches(0.4), h_step - Inches(0.65))
        p_t = tf.paragraphs[0]; r_t = p_t.add_run(); r_t.text = title; r_t.font.name = 'Calibri'; r_t.font.size = Pt(13); r_t.font.bold = True; r_t.font.color.rgb = COLOR_TEXT_DARK
        p_d = tf.add_paragraph(); p_d.space_before = Pt(4); r_d = p_d.add_run(); r_d.text = desc; r_d.font.name = 'Calibri'; r_d.font.size = Pt(10.5); r_d.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom: 4 Key Transformation Advantages
    w_adv = Inches(11.733)
    h_adv = Inches(2.45)
    y_adv = Inches(4.3)
    add_elevated_card(slide, Inches(0.8), y_adv, w_adv, h_adv)

    tb_adv, tf_adv = add_custom_textbox(slide, Inches(1.0), y_adv + Inches(0.18), w_adv - Inches(0.4), h_adv - Inches(0.3))
    p_ah = tf_adv.paragraphs[0]; r_ah = p_ah.add_run(); r_ah.text = "KEY TRANSFORMATION ADVANTAGES & VALUE ADDITION"; r_ah.font.name = 'Calibri'; r_ah.font.size = Pt(12.5); r_ah.font.bold = True; r_ah.font.color.rgb = COLOR_PRIMARY_DARK

    add_bullet_item(tf_adv, "100% Real-Time Transparency",
                    "Eliminates communication delays; head office directors and on-site engineers share an identical, synchronized inventory ledger.",
                    space_after=Pt(4), font_size=Pt(10))
    add_bullet_item(tf_adv, "Photographic Integrity via WebRTC",
                    "Direct in-browser camera streaming guarantees genuine, timestamped visual evidence of completed physical milestones before sign-off.",
                    space_after=Pt(4), font_size=Pt(10))
    add_bullet_item(tf_adv, "Zero Inventory Corruption",
                    "Pessimistic database row locking completely eliminates double-allocation race conditions during rapid concurrent material checkouts.",
                    space_after=Pt(4), font_size=Pt(10))
    add_bullet_item(tf_adv, "Cross-Platform Mobile Usability",
                    "Lightweight, mobile-responsive Bootstrap 5 interface functions seamlessly across smartphones, tablets, and laptops without app store installs.",
                    space_after=Pt(4), font_size=Pt(10))

def build_slide_9(prs):
    """Slide 9: System Design – Data Flow Architecture (DFD Level 0 & Level 1)"""
    slide = create_base_slide(prs)
    add_header(slide, "SYSTEM DESIGN", "Data Flow Architecture (DFD Level 0 & Level 1)",
               "Visualizing data movement across external actors, core processes, and database stores")
    add_footer(slide, 9)

    dfd_w = Inches(6.5)
    dfd_h = Inches(4.85)
    add_elevated_card(slide, Inches(0.8), Inches(1.85), dfd_w, dfd_h)
    
    dfd_img = os.path.join(DIAGRAMS_DIR, "dfd_1_clean.png")
    if os.path.exists(dfd_img):
        slide.shapes.add_picture(dfd_img, Inches(0.95), Inches(2.2), Inches(6.2), Inches(4.1))

    # Right: Specifications Card
    x_r = Inches(0.8) + dfd_w + Inches(0.24)
    w_r = Inches(4.993)
    add_elevated_card(slide, x_r, Inches(1.85), w_r, dfd_h)
    tb_spec, tf_spec = add_custom_textbox(slide, x_r + Inches(0.25), Inches(2.0), w_r - Inches(0.5), dfd_h - Inches(0.4))
    
    p_sp = tf_spec.paragraphs[0]; r_sp = p_sp.add_run(); r_sp.text = "CORE DATA FLOW SPECIFICATIONS"; r_sp.font.name = 'Calibri'; r_sp.font.size = Pt(12.5); r_sp.font.bold = True; r_sp.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf_spec, "External Entities", "Four primary system actors: Project Administrator, Builder/Contractor, Site Engineer, and Material Supplier.")
    add_bullet_item(tf_spec, "Process 1.0 (Auth & RBAC)", "Verifies user login credentials, generates encrypted session cookies, and enforces route authorization.")
    add_bullet_item(tf_spec, "Process 2.0 (House Projects)", "Manages residential plot allocations, tracks 8-stage civil milestones, and computes progress percentages.")
    add_bullet_item(tf_spec, "Process 3.0 (Materials Catalog)", "Maintains central catalog of 95+ construction commodities with standard units, rates, and buffer levels.")
    add_bullet_item(tf_spec, "Process 4.0 (Daily Stock Engine)", "Processes inward supplier shipments and outward site allocations with pessimistic row locking.")
    add_bullet_item(tf_spec, "Process 5.0 (Verification & Reports)", "Admin queue verifies field logs, commits audit trails, and compiles multi-page PDF progress reports.")
    add_bullet_item(tf_spec, "Persistent Stores", "MySQL 8.0 InnoDB tables: D1 Users, D2 Projects, D3 Materials, D4 Inventory Ledger, D5 Stages.")

def build_slide_10(prs):
    """Slide 10: System Interactions – UML Use Case Model"""
    slide = create_base_slide(prs)
    add_header(slide, "SYSTEM INTERACTIONS", "UML Use Case Model & Actor Capabilities",
               "Mapping user personas to operational functional capabilities across the system boundary")
    add_footer(slide, 10)

    uml_w = Inches(6.5)
    uml_h = Inches(4.85)
    add_elevated_card(slide, Inches(0.8), Inches(1.85), uml_w, uml_h)
    
    uml_img = os.path.join(DIAGRAMS_DIR, "uml_use_case_clean.png")
    if os.path.exists(uml_img):
        slide.shapes.add_picture(uml_img, Inches(0.95), Inches(2.2), Inches(6.2), Inches(4.1))

    # Right: Specifications Card
    x_r = Inches(0.8) + uml_w + Inches(0.24)
    w_r = Inches(4.993)
    add_elevated_card(slide, x_r, Inches(1.85), w_r, uml_h)
    tb_act, tf_act = add_custom_textbox(slide, x_r + Inches(0.25), Inches(2.0), w_r - Inches(0.5), uml_h - Inches(0.4))
    
    p_ac = tf_act.paragraphs[0]; r_ac = p_ac.add_run(); r_ac.text = "ACTOR OPERATIONAL CAPABILITIES"; r_ac.font.name = 'Calibri'; r_ac.font.size = Pt(12.5); r_ac.font.bold = True; r_ac.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf_act, "Project Administrator", "UC-01 Login & Role Security, UC-02 Manage Materials & Pricing, UC-03 Assign House Plots, UC-04 Approve Milestones, UC-05 Review Stock & Audit Reports.")
    add_bullet_item(tf_act, "Site Engineer / Supervisor", "UC-06 View Assigned Plots, UC-07 Update Construction Stage %, UC-08 Log Daily Usage, UC-09 Record Inward Delivery, UC-10 Civil Stage Estimator.")
    add_bullet_item(tf_act, "Building Contractor / Owner", "Monitors project progress percentage bars, reviews budget variances, inspects submitted milestone photographs, and tracks material consumption.")
    add_bullet_item(tf_act, "Material Supplier", "Submits delivery consignments, provides vehicle transit numbers, and receives digital receiving confirmations.")
    add_bullet_item(tf_act, "UML Boundary & Relationships", "Enforces <<include>> relationships for user session authentication and <<extend>> for optional WebRTC webcam snapshot capture.")

def build_slide_11(prs):
    """Slide 11: Architectural Structure & Functional Breakdown"""
    slide = create_base_slide(prs)
    add_header(slide, "FUNCTIONAL BREAKDOWN", "Architectural Structure & 3-Tier Layering",
               "Enterprise 3-tier architecture ensuring separation of concerns, scalability, and security")
    add_footer(slide, 11)

    w_card = Inches(11.733)
    h_card = Inches(1.48)
    gap_y  = Inches(0.18)
    y_top  = Inches(1.85)

    layers = [
        ("PRESENTATION LAYER (Frontend & Responsive Client Views)",
         [("Responsive UI Grid", "Mobile-first 12-column Bootstrap 5 grid system adapting smoothly from 360px mobile viewports to desktop monitors."),
          ("Jinja2 Dynamic Views", "Server-rendered HTML views with auto-escaping, completely preventing Cross-Site Scripting (XSS) attacks."),
          ("WebRTC MediaDevices API", "Client-side JavaScript streaming live camera video and drawing frames to HTML5 canvas elements for JPEG compression."),
          ("Interactive Visualizations", "Chart.js hardware-accelerated canvas charts for cumulative stage progress and material consumption rates.")],
         COLOR_PRIMARY),
        ("APPLICATION LAYER (Flask WSGI Framework & Business Logic)",
         [("WSGI Routing Controllers", "Lightweight, high-throughput Python application handling HTTP endpoints, URL parameters, and session tokens."),
          ("RBAC Security Decorators", "Custom Python decorators (@login_required, @role_required) enforcing strict role segregation at the WSGI boundary."),
          ("ACID Concurrency Controller", "Coordinates database transactions and enforces pessimistic row-level locking during simultaneous material checkouts."),
          ("Civil Estimation Engine", "Mathematical civil engineering formulas dynamically computing theoretical cement, steel, and sand quantities.")],
         COLOR_SECONDARY),
        ("DATA PERSISTENCE LAYER (MySQL 8.0 InnoDB Engine & Storage)",
         [("InnoDB Transactional Engine", "Full ACID compliance with foreign key referential integrity constraints, write-ahead logging, and crash recovery."),
          ("Connection Pooling", "mysql.connector.pooling maintains a thread-safe pool of reusable connections, eliminating per-request connection overhead."),
          ("Pessimistic Row Locking", "SELECT ... FOR UPDATE locks specific rows during multi-step updates, eliminating race conditions and negative balances."),
          ("Cryptographic Password Hashing", "Werkzeug PBKDF2:SHA256 salted hashes guarantee that plaintext user passwords are never stored in the database.")],
         COLOR_BORDER_AMBER)
    ]

    for idx, (title, bullets, accent_col) in enumerate(layers):
        y_pos = y_top + idx * (h_card + gap_y)
        add_elevated_card(slide, Inches(0.8), y_pos, w_card, h_card, border_color=accent_col, border_width=1.2)
        
        # Header strip
        h_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.92), y_pos + Inches(0.1), w_card - Inches(0.24), Inches(0.3))
        h_strip.fill.solid(); h_strip.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; h_strip.line.fill.background()
        p_hs = h_strip.text_frame.paragraphs[0]; r_hs = p_hs.add_run(); r_hs.text = title
        r_hs.font.name = 'Calibri'; r_hs.font.size = Pt(10.5); r_hs.font.bold = True; r_hs.font.color.rgb = accent_col

        tb, tf = add_custom_textbox(slide, Inches(0.95), y_pos + Inches(0.42), w_card - Inches(0.3), h_card - Inches(0.5))
        for b_title, b_desc in bullets:
            add_bullet_item(tf, b_title, b_desc, space_after=Pt(1.5), font_size=Pt(9.2))

def build_slide_12(prs):
    """Slide 12: Module Architecture / Description"""
    slide = create_base_slide(prs)
    add_header(slide, "MODULE ARCHITECTURE", "Functional Module Description & Technical Role",
               "Detailed technical specifications for the core application subsystems")
    add_footer(slide, 12)

    w_card = Inches(5.72)
    h_card = Inches(2.32)
    gap_x  = Inches(0.293)
    gap_y  = Inches(0.20)
    y1     = Inches(1.85)
    y2     = y1 + h_card + gap_y

    modules = [
        ("MODULE 1: USER AUTHENTICATION & RBAC", Inches(0.8), y1, [
            ("Role Segregation", "Restricts endpoints strictly across Administrator, Builder, and Site Engineer personas."),
            ("Cryptographic Hashing", "Hashes credentials with PBKDF2:SHA256 and salt; zero plaintext storage."),
            ("Session Integrity", "Issues cryptographically signed HTTP-only cookies preventing session tampering."),
            ("Security Interception", "Intercepts unauthorized access attempts and returns HTTP 403 Forbidden redirects.")
        ], COLOR_PRIMARY),
        ("MODULE 2: HOUSING PORTFOLIO & MILESTONE TRACKER", Inches(0.8) + w_card + gap_x, y1, [
            ("Multi-Plot Provisioning", "Registers residential plots with built-up square footage and allocated engineer."),
            ("8-Stage Civil Lifecycle", "Structures building phases: Excavation -> Substructure -> Plinth -> Masonry -> Slab -> Finishing."),
            ("Dynamic Recalculation", "Recalculates plot completion percentage dynamically as physical milestones complete."),
            ("Visual Progress Archive", "Maintains chronological history of stage notes and live captured site photographs.")
        ], COLOR_SECONDARY),
        ("MODULE 3: MASTER MATERIALS & THRESHOLD ALERTS", Inches(0.8), y2, [
            ("95+ Material Registry", "Categorized into Cement, Steel, Bricks, Aggregates, Plumbing, Electrical, and Paints."),
            ("Dynamic Warning Badges", "Compares available stock against minimum threshold; triggers visual amber & red alerts."),
            ("Inward Consignment Logging", "Records vendor name, challan number, vehicle registration number, and photo proof."),
            ("Unit Rate & Cost Accounting", "Tracks procurement rates and computes total consignment monetary expenditures.")
        ], COLOR_BORDER_AMBER),
        ("MODULE 4: CONCURRENCY-SAFE ALLOCATION & WEBRTC", Inches(0.8) + w_card + gap_x, y2, [
            ("Pessimistic Concurrency", "Acquires SELECT ... FOR UPDATE row locks to serialize concurrent material drawdowns."),
            ("Zero Decimal Drift", "Employs Python's Decimal fixed-point arithmetic to prevent floating-point balance errors."),
            ("WebRTC Viewfinder Capture", "Integrates live device camera feed into browser canvas to snapshot site proof."),
            ("Verification Queue", "Holds site requests in 'PENDING' status until verified by administrative review.")
        ], COLOR_PRIMARY_DARK)
    ]

    for title, x_pos, y_pos, bullets, accent_col in modules:
        add_elevated_card(slide, x_pos, y_pos, w_card, h_card)
        
        h_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.12), y_pos + Inches(0.12), w_card - Inches(0.24), Inches(0.35))
        h_strip.fill.solid(); h_strip.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; h_strip.line.fill.background()
        p_hs = h_strip.text_frame.paragraphs[0]; r_hs = p_hs.add_run(); r_hs.text = title
        r_hs.font.name = 'Calibri'; r_hs.font.size = Pt(10.5); r_hs.font.bold = True; r_hs.font.color.rgb = accent_col

        tb, tf = add_custom_textbox(slide, x_pos + Inches(0.2), y_pos + Inches(0.52), w_card - Inches(0.4), h_card - Inches(0.6))
        for b_title, b_desc in bullets:
            add_bullet_item(tf, b_title, b_desc, space_after=Pt(1.5), font_size=Pt(9.2))

def build_slide_13(prs):
    """Slide 13: Core Source Code (Part 1: ACID Concurrency Controller)"""
    slide = create_base_slide(prs)
    add_header(slide, "SOURCE CODE & IMPLEMENTATION (PART 1 OF 2)",
               "Core Source Code – ACID Concurrency Controller",
               "MySQL InnoDB row-level locking (SELECT ... FOR UPDATE) preventing inventory overselling in app.py")
    add_footer(slide, 13)

    # Left: Code Card
    w_code = Inches(6.6)
    h_code = Inches(4.9)
    add_elevated_card(slide, Inches(0.8), Inches(1.8), w_code, h_code, bg_color=COLOR_CODE_BG, border_color=COLOR_CODE_BORDER)
    
    b_tag = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), w_code, Inches(0.36))
    b_tag.fill.solid(); b_tag.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; b_tag.line.fill.background()
    tf_tag = b_tag.text_frame; p_t = tf_tag.paragraphs[0]; r_t = p_t.add_run()
    r_t.text = "Python 3.12 / Flask – Atomic Concurrency-Safe Material Allocation (app.py)"
    r_t.font.name = 'Calibri'; r_t.font.size = Pt(10); r_t.font.bold = True; r_t.font.color.rgb = COLOR_PRIMARY_DARK

    tb_code, tf_code = add_custom_textbox(slide, Inches(0.95), Inches(2.25), w_code - Inches(0.3), h_code - Inches(0.55))

    code_lines = [
        ("@app.route('/materials/outward', methods=['POST'])", COLOR_SECONDARY),
        ("@role_required('admin')", COLOR_SECONDARY),
        ("def outward_allocation():", COLOR_PRIMARY_DARK),
        ("    conn = get_db_connection()", COLOR_TEXT_DARK),
        ("    cursor = conn.cursor(dictionary=True)", COLOR_TEXT_DARK),
        ("    try:", COLOR_TEXT_DARK),
        ("        mat_id = int(request.form.get('material_id'))", COLOR_TEXT_DARK),
        ("        qty_requested = Decimal(request.form.get('quantity'))", COLOR_TEXT_DARK),
        ("        # 1. Acquire pessimistic row-level lock on material", COLOR_SUCCESS),
        ("        cursor.execute('''", COLOR_TEXT_MUTED),
        ("            SELECT material_id, available_quantity", COLOR_PRIMARY_DARK),
        ("            FROM materials WHERE material_id = %s FOR UPDATE;", COLOR_PRIMARY),
        ("        ''', (mat_id,))", COLOR_TEXT_MUTED),
        ("        mat = cursor.fetchone()", COLOR_TEXT_DARK),
        ("        # 2. Strict concurrency check against overselling", COLOR_SUCCESS),
        ("        if not mat or Decimal(str(mat['available_quantity'])) < qty_requested:", COLOR_PRIMARY_DARK),
        ("            conn.rollback()  # Abort safely if stock is insufficient", COLOR_PRIMARY),
        ("            flash('Allocation failed: Insufficient warehouse stock.', 'danger')", COLOR_TEXT_MUTED),
        ("            return redirect(url_for('materials'))", COLOR_TEXT_DARK),
        ("        # 3. Deduct stock atomically within locked scope", COLOR_SUCCESS),
        ("        cursor.execute('''UPDATE materials", COLOR_TEXT_DARK),
        ("            SET available_quantity = available_quantity - %s", COLOR_PRIMARY_DARK),
        ("            WHERE material_id = %s;''', (qty_requested, mat_id))", COLOR_TEXT_DARK),
        ("        conn.commit()  # Multi-table atomic success commit", COLOR_SUCCESS),
        ("        flash('Material successfully issued to site.', 'success')", COLOR_TEXT_MUTED),
        ("    finally:", COLOR_TEXT_DARK),
        ("        cursor.close(); conn.close()  # Connection returned to pool", COLOR_TEXT_MUTED)
    ]

    for idx, (line_text, line_color) in enumerate(code_lines):
        p_c = tf_code.paragraphs[0] if idx == 0 else tf_code.add_paragraph()
        p_c.space_before = Pt(0)
        p_c.space_after = Pt(0.5)
        r_c = p_c.add_run()
        r_c.text = line_text
        r_c.font.name = 'Consolas'
        r_c.font.size = Pt(8.5)
        r_c.font.color.rgb = line_color

    # Right Top: Concurrency Control Architecture Card
    x_r = Inches(7.6)
    w_r = Inches(4.933)
    add_elevated_card(slide, x_r, Inches(1.8), w_r, Inches(2.35))
    tb_exp, tf_exp = add_custom_textbox(slide, x_r + Inches(0.2), Inches(1.95), w_r - Inches(0.4), Inches(2.05))
    p_eh = tf_exp.paragraphs[0]; r_eh = p_eh.add_run(); r_eh.text = "CONCURRENCY CONTROL ARCHITECTURE"; r_eh.font.name = 'Calibri'; r_eh.font.size = Pt(11.5); r_eh.font.bold = True; r_eh.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf_exp, "Pessimistic Row Locking", "SELECT ... FOR UPDATE locks specific material rows during the transaction, preventing parallel read-modify-write collisions.", space_after=Pt(3), font_size=Pt(9.2))
    add_bullet_item(tf_exp, "Zero Overselling Guarantee", "Strict available_quantity validation with immediate rollback() eliminates overselling race conditions.", space_after=Pt(3), font_size=Pt(9.2))
    add_bullet_item(tf_exp, "ACID Persistence", "MySQL InnoDB ensures that inventory deductions and project allocation records commit atomically.", space_after=Pt(3), font_size=Pt(9.2))

    # Right Bottom: GitHub Link Card
    add_github_card(slide, x_r, Inches(4.35), w_r, Inches(2.35), sub_desc="Material allocation controller source code (app.py):")

def build_slide_14(prs):
    """Slide 14: Core Source Code (Part 2: WebRTC Camera & Role Security)"""
    slide = create_base_slide(prs)
    add_header(slide, "SOURCE CODE & IMPLEMENTATION (PART 2 OF 2)",
               "Core Source Code – WebRTC Camera & Security Decorator",
               "Hardware-accelerated camera video streaming (script.js) and role authorization (decorators.py)")
    add_footer(slide, 14)

    # Left Top: WebRTC JavaScript Code
    w_code = Inches(6.4)
    h_c1   = Inches(2.35)
    add_elevated_card(slide, Inches(0.8), Inches(1.8), w_code, h_c1, bg_color=COLOR_CODE_BG, border_color=COLOR_CODE_BORDER)
    
    b_tag1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), w_code, Inches(0.32))
    b_tag1.fill.solid(); b_tag1.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; b_tag1.line.fill.background()
    p_t1 = b_tag1.text_frame.paragraphs[0]; r_t1 = p_t1.add_run(); r_t1.text = "JavaScript (ES6) – WebRTC Hardware Viewfinder & Capture (script.js)"
    r_t1.font.name = 'Calibri'; r_t1.font.size = Pt(9.5); r_t1.font.bold = True; r_t1.font.color.rgb = COLOR_PRIMARY_DARK

    tb_c1, tf_c1 = add_custom_textbox(slide, Inches(0.95), Inches(2.18), w_code - Inches(0.3), h_c1 - Inches(0.42))
    js_lines = [
        ("// 1. Access in-browser camera hardware stream", COLOR_SUCCESS),
        ("async function startSiteCamera(viewfinderId) {", COLOR_PRIMARY_DARK),
        ("    const stream = await navigator.mediaDevices.getUserMedia({", COLOR_TEXT_DARK),
        ("        video: { width: 1280, height: 720 }, audio: false", COLOR_PRIMARY),
        ("    });", COLOR_TEXT_DARK),
        ("    document.getElementById(viewfinderId).srcObject = stream;", COLOR_TEXT_DARK),
        ("}", COLOR_PRIMARY_DARK),
        ("// 2. Snapshot current viewfinder frame to HTML5 Canvas", COLOR_SUCCESS),
        ("function captureSitePhoto(videoId, canvasId, inputId) {", COLOR_PRIMARY_DARK),
        ("    const video = document.getElementById(videoId);", COLOR_TEXT_DARK),
        ("    const canvas = document.getElementById(canvasId);", COLOR_TEXT_DARK),
        ("    canvas.width = video.videoWidth || 1280; canvas.height = video.videoHeight || 720;", COLOR_TEXT_MUTED),
        ("    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);", COLOR_TEXT_DARK),
        ("    // 3. Export as JPEG blob and attach to form", COLOR_SUCCESS),
        ("    canvas.toBlob((blob) => {", COLOR_TEXT_DARK),
        ("        const file = new File([blob], 'site_proof.jpg', { type: 'image/jpeg' });", COLOR_PRIMARY),
        ("        const dt = new DataTransfer(); dt.items.add(file);", COLOR_TEXT_DARK),
        ("        document.getElementById(inputId).files = dt.files;", COLOR_PRIMARY_DARK),
        ("    }, 'image/jpeg', 0.92);", COLOR_TEXT_MUTED),
        ("}", COLOR_PRIMARY_DARK)
    ]
    for idx, (lt, lc) in enumerate(js_lines):
        p = tf_c1.paragraphs[0] if idx == 0 else tf_c1.add_paragraph()
        p.space_before = Pt(0); p.space_after = Pt(0.5)
        r = p.add_run(); r.text = lt; r.font.name = 'Consolas'; r.font.size = Pt(8.0); r.font.color.rgb = lc

    # Left Bottom: Python Role Security Code
    h_c2 = Inches(2.35)
    y_c2 = Inches(4.35)
    add_elevated_card(slide, Inches(0.8), y_c2, w_code, h_c2, bg_color=COLOR_CODE_BG, border_color=COLOR_CODE_BORDER)
    
    b_tag2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_c2, w_code, Inches(0.32))
    b_tag2.fill.solid(); b_tag2.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT; b_tag2.line.fill.background()
    p_t2 = b_tag2.text_frame.paragraphs[0]; r_t2 = p_t2.add_run(); r_t2.text = "Python / Flask – Role-Based Access Control Decorator (utils/decorators.py)"
    r_t2.font.name = 'Calibri'; r_t2.font.size = Pt(9.5); r_t2.font.bold = True; r_t2.font.color.rgb = COLOR_SECONDARY

    tb_c2, tf_c2 = add_custom_textbox(slide, Inches(0.95), y_c2 + Inches(0.38), w_code - Inches(0.3), h_c2 - Inches(0.42))
    py_lines = [
        ("def role_required(*allowed_roles):", COLOR_PRIMARY_DARK),
        ("    def decorator(f):", COLOR_TEXT_DARK),
        ("        @wraps(f)", COLOR_SECONDARY),
        ("        def decorated_function(*args, **kwargs):", COLOR_PRIMARY_DARK),
        ("            if 'user_id' not in session:", COLOR_PRIMARY),
        ("                return redirect(url_for('login'))", COLOR_TEXT_DARK),
        ("            user_role = session.get('role')", COLOR_TEXT_DARK),
        ("            if user_role not in allowed_roles:", COLOR_PRIMARY),
        ("                flash('Access Denied: Unauthorized route!', 'danger')", COLOR_TEXT_MUTED),
        ("                return redirect(url_for(f'{user_role}_dashboard'))", COLOR_TEXT_DARK),
        ("            return f(*args, **kwargs)", COLOR_SUCCESS),
        ("        return decorated_function", COLOR_TEXT_DARK),
        ("    return decorator", COLOR_PRIMARY_DARK)
    ]
    for idx, (lt, lc) in enumerate(py_lines):
        p = tf_c2.paragraphs[0] if idx == 0 else tf_c2.add_paragraph()
        p.space_before = Pt(0); p.space_after = Pt(0.5)
        r = p.add_run(); r.text = lt; r.font.name = 'Consolas'; r.font.size = Pt(8.2); r.font.color.rgb = lc

    # Right Top: Technical Explanation Card
    x_r = Inches(7.4)
    w_r = Inches(5.133)
    add_elevated_card(slide, x_r, Inches(1.8), w_r, Inches(2.35))
    tb_exp, tf_exp = add_custom_textbox(slide, x_r + Inches(0.2), Inches(1.95), w_r - Inches(0.4), Inches(2.05))
    p_eh = tf_exp.paragraphs[0]; r_eh = p_eh.add_run(); r_eh.text = "CLIENT HARDWARE INTEGRATION & SECURITY"; r_eh.font.name = 'Calibri'; r_eh.font.size = Pt(11.5); r_eh.font.bold = True; r_eh.font.color.rgb = COLOR_PRIMARY_DARK
    add_bullet_item(tf_exp, "Hardware Camera Streaming", "Direct access to device cameras ensures site engineers upload authentic real-time field photos rather than pre-stored gallery images.", space_after=Pt(3), font_size=Pt(9.2))
    add_bullet_item(tf_exp, "Declarative Route Security", "Python function decorators intercept requests at the WSGI boundary, guaranteeing role separation between Admins, Builders, and Site Engineers.", space_after=Pt(3), font_size=Pt(9.2))
    add_bullet_item(tf_exp, "Zero Third-Party Plugins", "Native WebRTC MediaDevices API and HTML5 canvas operate universally without requiring native mobile application downloads.", space_after=Pt(3), font_size=Pt(9.2))

    # Right Bottom: GitHub Link Card
    add_github_card(slide, x_r, Inches(4.35), w_r, Inches(2.35), sub_desc="Hardware camera & security source code:")

def build_slide_15(prs):
    """Slide 15: Demonstration Evidence (Results and Screen Output)"""
    slide = create_base_slide(prs)
    add_header(slide, "DEMONSTRATION EVIDENCE", "Results and Live Screen Output",
               "Actual user interfaces captured during operational system execution")
    add_footer(slide, 15)

    w_card = Inches(3.75)
    h_card = Inches(4.35)
    gap_x  = Inches(0.24)
    y_top  = Inches(1.8)

    screens = [
        ("Screen 1: Administrator Dashboard",
         os.path.join(DIAGRAMS_DIR, "admin_dashboard_test.png"),
         "Executive KPI statistics, active housing plot counts, low-stock alerts, and pending builder verification queues.",
         COLOR_PRIMARY),
        ("Screen 2: House Progress Tracker",
         os.path.join(DIAGRAMS_DIR, "houses_progress_test.png"),
         "Multi-plot construction portfolio, current structural milestone, percentage progress bars, and assigned engineers.",
         COLOR_SECONDARY),
        ("Screen 3: Material Inward Receiving",
         os.path.join(DIAGRAMS_DIR, "inward_dispatch_test.png"),
         "Supplier consignment receiving interface with challan logging, vehicle registration numbers, and photo proof.",
         COLOR_BORDER_AMBER)
    ]

    for idx, (title, img_path, caption, col) in enumerate(screens):
        x_pos = Inches(0.8) + idx * (w_card + gap_x)
        add_elevated_card(slide, x_pos, y_top, w_card, h_card)

        # Title bar
        t_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_pos + Inches(0.12), y_top + Inches(0.12), w_card - Inches(0.24), Inches(0.35))
        t_bar.fill.solid(); t_bar.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; t_bar.line.fill.background()
        p_tb = t_bar.text_frame.paragraphs[0]; r_tb = p_tb.add_run(); r_tb.text = title
        r_tb.font.name = 'Calibri'; r_tb.font.size = Pt(10.5); r_tb.font.bold = True; r_tb.font.color.rgb = col

        # Image Container
        img_h = Inches(2.7)
        if os.path.exists(img_path):
            slide.shapes.add_picture(img_path, x_pos + Inches(0.15), y_top + Inches(0.55), w_card - Inches(0.3), img_h)

        # Caption
        tb_c, tf_c = add_custom_textbox(slide, x_pos + Inches(0.15), y_top + Inches(3.35), w_card - Inches(0.3), Inches(0.9))
        p_c = tf_c.paragraphs[0]; r_c = p_c.add_run(); r_c.text = caption
        r_c.font.name = 'Calibri'; r_c.font.size = Pt(9.5); r_c.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Objective Banner
    banner = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.28), Inches(11.733), Inches(0.55))
    banner.fill.solid(); banner.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    banner.line.color.rgb = COLOR_PRIMARY; banner.line.width = Pt(1.0)
    tf_b = banner.text_frame; p_b = tf_b.paragraphs[0]; p_b.alignment = PP_ALIGN.CENTER
    r_b1 = p_b.add_run(); r_b1.text = "Result Against Project Objective: "
    r_b1.font.name = 'Calibri'; r_b1.font.size = Pt(11); r_b1.font.bold = True; r_b1.font.color.rgb = COLOR_PRIMARY_DARK
    r_b2 = p_b.add_run()
    r_b2.text = "Successfully verified complete end-to-end user journeys from material delivery challan intake to on-site consumption logging and photographic milestone sign-off with 100% data integrity."
    r_b2.font.name = 'Calibri'; r_b2.font.size = Pt(10.5); r_b2.font.color.rgb = COLOR_TEXT_DARK

def build_slide_16(prs):
    """Slide 16: Project Assessment (Conclusion and Future Scope)"""
    slide = create_base_slide(prs)
    add_header(slide, "PROJECT ASSESSMENT", "Conclusion and Future Scope",
               "Project delivery summary, engineering lessons learnt, and future scalability roadmap")
    add_footer(slide, 16)

    w_col = Inches(5.72)
    h_col = Inches(4.85)
    gap_x = Inches(0.293)
    y_top = Inches(1.85)

    # Left: What Was Achieved & Lessons Learnt
    c_left = add_elevated_card(slide, Inches(0.8), y_top, w_col, h_col)
    top_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_top, w_col, Inches(0.42))
    top_l.fill.solid(); top_l.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; top_l.line.fill.background()
    p_tl = top_l.text_frame.paragraphs[0]; r_tl = p_tl.add_run(); r_tl.text = "PROJECT SUMMARY & LESSONS LEARNT"
    r_tl.font.name = 'Calibri'; r_tl.font.size = Pt(11); r_tl.font.bold = True; r_tl.font.color.rgb = COLOR_PRIMARY_DARK

    tb_l, tf_l = add_custom_textbox(slide, Inches(1.0), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    add_bullet_item(tf_l, "Centralized Inventory Governance",
                    "Successfully eliminated manual paper registers, unifying 95+ construction commodities into a single real-time ledger.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Concurrency Resilience",
                    "Pessimistic row locking (SELECT ... FOR UPDATE) proved crucial in guaranteeing 100% stock accuracy under simulated concurrent allocations.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Verifiable Milestone Progress",
                    "Hardware WebRTC camera integration successfully bridged site distrust by providing live, timestamped photographic evidence before stage certification.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_l, "Practical Engineering Mastery",
                    "Gained deep practical mastery of full-stack Python Flask architecture, relational schema normalization (3NF), session security, and mobile UX.",
                    space_after=Pt(8), font_size=Pt(10.5))

    # Right: Recommended Future Enhancements
    x_r = Inches(0.8) + w_col + gap_x
    c_right = add_elevated_card(slide, x_r, y_top, w_col, h_col)
    top_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_r, y_top, w_col, Inches(0.42))
    top_r.fill.solid(); top_r.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT; top_r.line.fill.background()
    p_tr = top_r.text_frame.paragraphs[0]; r_tr = p_tr.add_run(); r_tr.text = "RECOMMENDED FUTURE ENHANCEMENTS"
    r_tr.font.name = 'Calibri'; r_tr.font.size = Pt(11); r_tr.font.bold = True; r_tr.font.color.rgb = COLOR_SECONDARY

    tb_r, tf_r = add_custom_textbox(slide, x_r + Inches(0.2), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    add_bullet_item(tf_r, "Offline Progressive Web App (PWA)",
                    "Implement Service Workers and IndexedDB local caching, enabling site engineers to log material usage and photos even without cellular connectivity.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_r, "Automated Barcode & RFID Gate Intake",
                    "Incorporate handheld Bluetooth or camera-based 1D/2D barcode and RFID tag scanners at warehouse gates for instantaneous check-in of palletized materials.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_r, "AI Construction Defect Detection",
                    "Deploy lightweight computer vision models (YOLOv8) on submitted webcam photographs to automatically detect concrete honeycombing and structural cracks.",
                    space_after=Pt(8), font_size=Pt(10.5))
    add_bullet_item(tf_r, "Native Mobile App with GPS Geofencing",
                    "Develop native mobile companion apps featuring cryptographic GPS geofencing to verify that site progress photos are taken strictly within physical plot bounds.",
                    space_after=Pt(8), font_size=Pt(10.5))

def build_slide_17(prs):
    """Slide 17: References / Bibliography"""
    slide = create_base_slide(prs)
    add_header(slide, "REFERENCES", "Books, Specifications & Technology References",
               "Authoritative textbooks and official documentation utilized in project development")
    add_footer(slide, 17)

    w_col = Inches(5.72)
    h_col = Inches(4.85)
    gap_x = Inches(0.293)
    y_top = Inches(1.85)

    # Left: Books and Academic Publications
    c_left = add_elevated_card(slide, Inches(0.8), y_top, w_col, h_col)
    top_l = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y_top, w_col, Inches(0.42))
    top_l.fill.solid(); top_l.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT; top_l.line.fill.background()
    p_tl = top_l.text_frame.paragraphs[0]; r_tl = p_tl.add_run(); r_tl.text = "BOOKS AND ACADEMIC PUBLICATIONS"
    r_tl.font.name = 'Calibri'; r_tl.font.size = Pt(11); r_tl.font.bold = True; r_tl.font.color.rgb = COLOR_PRIMARY_DARK

    tb_l, tf_l = add_custom_textbox(slide, Inches(1.0), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    books = [
        ("[1] Sommerville, Ian", "Software Engineering. 10th ed., Pearson, 2015. Comprehensive textbook on software engineering lifecycle models, architectural patterns, and quality assurance."),
        ("[2] Elmasri, Ramez, and Shamkant B. Navathe", "Fundamentals of Database Systems. 7th ed., Pearson, 2016. In-depth reference on relational database normalization to 3NF and concurrency control."),
        ("[3] Grinberg, Miguel", "Flask Web Development: Developing Web Applications with Python. 2nd ed., O'Reilly Media, 2018. Essential guide for modular routing, Jinja2 templating, and user authentication."),
        ("[4] Pressman, Roger S., and Bruce R. Maxim", "Software Engineering: A Practitioner's Approach. 9th ed., McGraw-Hill, 2020. Methodological guidelines for V-Model testing and system requirements analysis."),
        ("[5] Chacon, Scott, and Ben Straub", "Pro Git: Everything You Need to Know About Git. 2nd ed., Apress, 2014. Standard guide for version control, atomic commits, and team collaboration workflows.")
    ]
    for b_auth, b_desc in books:
        add_bullet_item(tf_l, b_auth, b_desc, space_after=Pt(5), font_size=Pt(9.2))

    # Right: Technology Documentation & Standards
    x_r = Inches(0.8) + w_col + gap_x
    c_right = add_elevated_card(slide, x_r, y_top, w_col, h_col)
    top_r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x_r, y_top, w_col, Inches(0.42))
    top_r.fill.solid(); top_r.fill.fore_color.rgb = COLOR_SECONDARY_LIGHT; top_r.line.fill.background()
    p_tr = top_r.text_frame.paragraphs[0]; r_tr = p_tr.add_run(); r_tr.text = "TECHNOLOGY DOCUMENTATION & STANDARDS"
    r_tr.font.name = 'Calibri'; r_tr.font.size = Pt(11); r_tr.font.bold = True; r_tr.font.color.rgb = COLOR_SECONDARY

    tb_r, tf_r = add_custom_textbox(slide, x_r + Inches(0.2), y_top + Inches(0.55), w_col - Inches(0.4), h_col - Inches(0.7))
    techs = [
        ("Python 3.12 Official Documentation", "https://docs.python.org/3.12/\nStandard library, decimal arithmetic, threading, and WSGI compliance."),
        ("Flask 3.0 API Documentation", "https://flask.palletsprojects.com/\nApplication routing, session security, Jinja2 templating, and request handling."),
        ("MySQL 8.0 Reference Manual", "https://dev.mysql.com/doc/refman/8.0/en/\nInnoDB storage engine, connection pooling, and row-level locking architecture."),
        ("W3C Media Capture Streams API", "https://www.w3.org/TR/mediacapture-streams/\nHTML5 WebRTC standard for client-side webcam streaming and photo capture."),
        ("Bootstrap 5.3 Responsive Framework", "https://getbootstrap.com/docs/5.3/\nResponsive 12-column mobile-first grid system and UI component architecture.")
    ]
    for t_auth, t_desc in techs:
        add_bullet_item(tf_r, t_auth, t_desc, space_after=Pt(6), font_size=Pt(9.2))

def build_slide_18(prs):
    """Slide 18: Thank You / Closing Discussion"""
    slide = create_base_slide(prs, is_thankyou=True)

    # Master Elevated White Card in Center
    add_elevated_card(slide, Inches(1.8), Inches(0.45), Inches(9.733), Inches(6.6),
                      bg_color=RGBColor(255, 255, 255), border_color=COLOR_PRIMARY, border_width=1.5)

    # Top Category Pill
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.666), Inches(0.8), Inches(8.0), Inches(0.42))
    pill.fill.solid(); pill.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    pill.line.color.rgb = COLOR_PRIMARY; pill.line.width = Pt(1.2)
    p_p = pill.text_frame.paragraphs[0]; p_p.alignment = PP_ALIGN.CENTER
    r_p = p_p.add_run(); r_p.text = "BUILD TRACK – REAL ESTATE HOUSE BUILDING INVENTORY & PROGRESS TRACKER"
    r_p.font.name = 'Calibri'; r_p.font.size = Pt(10.5); r_p.font.bold = True; r_p.font.color.rgb = COLOR_PRIMARY_DARK

    # Centered Thank You Heading
    tb_ty, tf_ty = add_custom_textbox(slide, Inches(2.0), Inches(1.35), Inches(9.333), Inches(1.8))
    
    pty1 = tf_ty.paragraphs[0]
    pty1.alignment = PP_ALIGN.CENTER
    rty1 = pty1.add_run()
    rty1.text = "THANK YOU"
    rty1.font.name = 'Calibri'; rty1.font.size = Pt(36); rty1.font.bold = True; rty1.font.color.rgb = COLOR_PRIMARY_DARK

    pty2 = tf_ty.add_paragraph()
    pty2.alignment = PP_ALIGN.CENTER
    rty2 = pty2.add_run()
    rty2.text = "QUESTIONS & VIVA VOCE DISCUSSION"
    rty2.font.name = 'Calibri'; rty2.font.size = Pt(17); rty2.font.bold = True; rty2.font.color.rgb = COLOR_SECONDARY

    pty3 = tf_ty.add_paragraph()
    pty3.space_before = Pt(4)
    pty3.alignment = PP_ALIGN.CENTER
    rty3 = pty3.add_run()
    rty3.text = "We welcome questions, suggestions, and feedback on the project architecture,\nconcurrency control models, and software engineering implementation."
    rty3.font.name = 'Calibri'; rty3.font.size = Pt(11); rty3.font.color.rgb = COLOR_TEXT_MUTED

    # Student Identification Card
    card_stu = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.666), Inches(3.15), Inches(8.0), Inches(1.65))
    card_stu.fill.solid(); card_stu.fill.fore_color.rgb = COLOR_PRIMARY_LIGHT
    card_stu.line.color.rgb = COLOR_PRIMARY; card_stu.line.width = Pt(1.5)

    tb_stu, tf_stu = add_custom_textbox(slide, Inches(2.666), Inches(3.22), Inches(8.0), Inches(1.5))

    ps1 = tf_stu.paragraphs[0]; ps1.alignment = PP_ALIGN.CENTER
    rs1 = ps1.add_run(); rs1.text = "NAME OF STUDENT :  SANTHOSH RATHINAM M"
    rs1.font.name = 'Calibri'; rs1.font.size = Pt(15); rs1.font.bold = True; rs1.font.color.rgb = COLOR_TEXT_DARK

    ps2 = tf_stu.add_paragraph(); ps2.alignment = PP_ALIGN.CENTER
    rs2 = ps2.add_run(); rs2.text = "ENROLMENT NUMBER :  EA2532251010685"
    rs2.font.name = 'Calibri'; rs2.font.size = Pt(14); rs2.font.bold = True; rs2.font.color.rgb = COLOR_PRIMARY_DARK

    ps3 = tf_stu.add_paragraph(); ps3.alignment = PP_ALIGN.CENTER
    rs3 = ps3.add_run(); rs3.text = "MASTER OF COMPUTER APPLICATIONS (MCA - III SEMESTER)"
    rs3.font.name = 'Calibri'; rs3.font.size = Pt(12); rs3.font.bold = True; rs3.font.color.rgb = COLOR_SECONDARY

    ps4 = tf_stu.add_paragraph(); ps4.alignment = PP_ALIGN.CENTER
    rs4 = ps4.add_run(); rs4.text = "Directorate of Online Education, SRM Institute of Science and Technology"
    rs4.font.name = 'Calibri'; rs4.font.size = Pt(10.5); rs4.font.color.rgb = COLOR_TEXT_MUTED

    # GitHub Project Link Card at Bottom (Prominent with Direct Folder Link)
    add_github_card(slide, Inches(2.2), Inches(4.95), Inches(8.933), Inches(1.85),
                    sub_desc="Direct links to official repository and project source folder on GitHub:")

def main():
    print("Initializing PowerPoint Presentation (16:9 Widescreen)...")
    prs = init_presentation()

    print("Building Slide 1: Cover Page...")
    build_slide_1(prs)

    print("Building Slide 2: Project Overview & Scope...")
    build_slide_2(prs)

    print("Building Slide 3: Abstract (What the Project Solves and Delivers)...")
    build_slide_3(prs)

    print("Building Slide 4: Introduction (Why This Problem Matters)...")
    build_slide_4(prs)

    print("Building Slide 5: System Capabilities / Key Features...")
    build_slide_5(prs)

    print("Building Slide 6: System Hardware & Software Requirements...")
    build_slide_6(prs)

    print("Building Slide 7: Critical Analysis / Existing System and Gaps...")
    build_slide_7(prs)

    print("Building Slide 8: Proposed Approach...")
    build_slide_8(prs)

    print("Building Slide 9: System Design – Data Flow Architecture...")
    build_slide_9(prs)

    print("Building Slide 10: System Interactions – UML Use Case Model...")
    build_slide_10(prs)

    print("Building Slide 11: Architectural Structure & Functional Breakdown...")
    build_slide_11(prs)

    print("Building Slide 12: Module Architecture / Description...")
    build_slide_12(prs)

    print("Building Slide 13: Core Source Code (Part 1: ACID Concurrency Controller)...")
    build_slide_13(prs)

    print("Building Slide 14: Core Source Code (Part 2: WebRTC Camera & Security)...")
    build_slide_14(prs)

    print("Building Slide 15: Demonstration Evidence (Results and Screen Output)...")
    build_slide_15(prs)

    print("Building Slide 16: Project Assessment (Conclusion and Future Scope)...")
    build_slide_16(prs)

    print("Building Slide 17: References / Bibliography...")
    build_slide_17(prs)

    print("Building Slide 18: Thank You / Closing Discussion...")
    build_slide_18(prs)

    # Save to primary scratch directory
    scratch_out = r"C:\Users\Santhosh Rathinam\.gemini\antigravity\scratch\real_estate_inventory\reports\Build_Track_Real_Estate_Internship_Viva_Presentation.pptx"
    prs.save(scratch_out)
    print(f"Presentation saved successfully to: {scratch_out}")

    # Copy to D: Drive Project Documentation if accessible
    d_dir = r"D:\Santhosh Rathinam\Build Track - Real Estate House Building Inventory and Progress TrackerDocumentation"
    try:
        if os.path.exists(d_dir):
            d_out = os.path.join(d_dir, "Build_Track_Real_Estate_Internship_Viva_Presentation.pptx")
            import shutil
            shutil.copy2(scratch_out, d_out)
            print(f"Presentation also copied to: {d_out}")
    except Exception as e:
        print(f"Note: Copy to D: drive can be executed via BypassSandbox command ({e})")

if __name__ == "__main__":
    main()
