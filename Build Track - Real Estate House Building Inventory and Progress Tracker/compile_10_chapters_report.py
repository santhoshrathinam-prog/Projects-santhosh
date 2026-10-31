import os
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from report_helpers import (
    BLACK, PROJECT_NAME, FULL_PROJECT_TITLE, BASE_DIR, REPORTS_DIR, DIAGRAMS_DIR, TARGET_DEST_DIR,
    add_page_number_field, add_page_borders_to_section, set_section_margins_and_paper,
    set_section_numbering_type, add_body_paragraph
)
from chapters_1_to_3_new import add_chapters_1_to_3
from chapters_4_to_6_new import add_chapters_4_to_6
from chapters_7_to_10_new import add_chapters_7_to_10
from build_10_chapters_report import get_toc_entries, USER_DOCX_PATH

def build_document(page_dict=None):
    print("Loading base document from user upload...")
    doc = Document(USER_DOCX_PATH)

    # Keep paragraphs 0 to 28 (Title Page, Bonafide Certificate, Acknowledgements)
    # Remove paragraphs 29 onwards
    for p in doc.paragraphs[29:]:
        p._p.getparent().remove(p._p)

    # Remove all existing tables in body
    for t in doc.tables:
        t._tbl.getparent().remove(t._tbl)

    # Configure Section 0 (Title, Cert, Ack) -> lowerRoman starting at 1 (i, ii, iii)
    s0 = doc.sections[0]
    set_section_margins_and_paper(s0)
    set_section_numbering_type(s0, fmt="lowerRoman", start=1)
    p_f0 = s0.footer.paragraphs[0]
    p_f0.text = ""
    p_f0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f0 = p_f0.add_run()
    r_f0.font.name = 'Times New Roman'
    r_f0.font.size = Pt(12)
    r_f0.font.color.rgb = BLACK
    add_page_number_field(p_f0)

    # SECTION 1: PRELIMINARY PAGES (CONTENTS & ABSTRACT) -> lowerRoman starting at 4 (iv, v, vi)
    s1 = doc.sections[1]
    set_section_margins_and_paper(s1)
    s1.footer.is_linked_to_previous = False
    set_section_numbering_type(s1, fmt="lowerRoman", start=4)

    p_f1 = s1.footer.paragraphs[0]
    p_f1.text = ""
    p_f1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f1 = p_f1.add_run()
    r_f1.font.name = 'Times New Roman'
    r_f1.font.size = Pt(12)
    r_f1.font.color.rgb = BLACK
    add_page_number_field(p_f1)

    # TABLE OF CONTENTS / CONTENTS
    p_toc_h = doc.add_paragraph()
    p_toc_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_h.paragraph_format.space_before = Pt(12)
    p_toc_h.paragraph_format.space_after = Pt(18)
    r_toc_h = p_toc_h.add_run("CONTENTS")
    r_toc_h.font.name = 'Times New Roman'
    r_toc_h.font.size = Pt(14)
    r_toc_h.font.bold = True
    r_toc_h.font.color.rgb = BLACK

    tab_pos = Cm(16.0)
    entries = get_toc_entries(page_dict)

    for num, title, pg, ind in entries:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(ind)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.tab_stops.add_tab_stop(tab_pos, WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        
        text = f"{num} {title}" if num else title
        r1 = p.add_run(text)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(12)
        if ind == 0 or title == "PROGRAM LISTINGS":
            r1.font.bold = True
        r1.font.color.rgb = BLACK
        
        r_tab = p.add_run('\t')
        r_tab.font.name = 'Times New Roman'
        r_tab.font.size = Pt(12)
        r_tab.font.color.rgb = BLACK
        
        r2 = p.add_run(pg)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(12)
        if ind == 0 or title == "PROGRAM LISTINGS":
            r2.font.bold = True
        r2.font.color.rgb = BLACK

    doc.add_page_break()

    # ABSTRACT
    p_abs_h = doc.add_paragraph()
    p_abs_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_abs_h.paragraph_format.space_before = Pt(18)
    p_abs_h.paragraph_format.space_after = Pt(18)
    r_abs_h = p_abs_h.add_run("ABSTRACT")
    r_abs_h.font.name = 'Times New Roman'
    r_abs_h.font.size = Pt(14)
    r_abs_h.font.bold = True
    r_abs_h.font.color.rgb = BLACK

    abstract_text = (
        "In the residential real estate construction sector, tracking raw building materials and monitoring daily "
        "structural construction milestones represent one of the most critical operational challenges. Traditional house "
        "construction sites rely predominantly on manual paper registers, informal telephone updates, and fragmented messaging "
        "applications, leading to material misplacement, undocumented wastage, site theft, delayed reordering, and substantial "
        "cost overruns that jeopardize house handover timelines and builder profitability. This project develops 'Build Track - Real "
        "Estate House Building Inventory and Progress Tracker' (Build Track), a full-stack, web-based management information system "
        "specifically engineered for residential construction builders, site engineers, and project managers. The platform provides "
        "end-to-end digital tracking of building materials and physical milestone progress across multiple concurrent house construction "
        "projects. Core technical contributions include role-based access control (RBAC), multi-house stage tracking, a master building "
        "material catalog spanning eight standard categories with 95+ items, on-site consumption logging, an automated construction stage "
        "material estimator, and an administrative transaction verification queue. The system is built using Python 3.12 and Flask 3.0.3 "
        "as the backend server framework, MySQL 8.0 for ACID-compliant transactional persistence with pessimistic row-level concurrency "
        "locking (SELECT ... FOR UPDATE) to eliminate inventory overselling, and a responsive Bootstrap 5 frontend interface with client-side "
        "WebRTC camera hardware integration for live photographic site proof. Comprehensive unit, integration, role-based, and concurrency "
        "testing demonstrated 100% test pass rates across all verification suites. The system establishes complete operational transparency, "
        "eliminates manual administrative latency, and ensures high structural accountability between central management and physical construction job sites."
    )
    add_body_paragraph(doc, abstract_text, space_after=12)

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.line_spacing = 1.5
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.first_line_indent = Inches(0.5)
    r_kw_lbl = p_kw.add_run("Keywords: ")
    r_kw_lbl.font.name = 'Times New Roman'
    r_kw_lbl.font.size = Pt(12)
    r_kw_lbl.font.bold = True
    r_kw_lbl.font.color.rgb = BLACK

    r_kw_txt = p_kw.add_run("Real Estate House Building, Inventory Management, Progress Tracker, Material Estimation, Concurrency Control, Flask, MySQL, WebRTC.")
    r_kw_txt.font.name = 'Times New Roman'
    r_kw_txt.font.size = Pt(12)
    r_kw_txt.font.italic = True
    r_kw_txt.font.color.rgb = BLACK

    # SECTION 2: MAIN CHAPTERS (ARABIC 1, 2, 3...)
    s2 = doc.add_section()
    set_section_margins_and_paper(s2)
    s2.footer.is_linked_to_previous = False
    set_section_numbering_type(s2, fmt="decimal", start=1)

    p_f2 = s2.footer.paragraphs[0]
    p_f2.text = ""
    p_f2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f2 = p_f2.add_run()
    r_f2.font.name = 'Times New Roman'
    r_f2.font.size = Pt(12)
    r_f2.font.color.rgb = BLACK
    add_page_number_field(p_f2)

    print("Adding Chapters 1 to 3...")
    add_chapters_1_to_3(doc)

    print("Adding Chapters 4 to 6...")
    add_chapters_4_to_6(doc)

    print("Adding Chapters 7 to 10, Appendices, References...")
    add_chapters_7_to_10(doc)

    print("Enforcing strict Times New Roman and Pure Black...")
    for p in doc.paragraphs:
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.color.rgb = BLACK

    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        r.font.color.rgb = BLACK

    out_file = os.path.join(REPORTS_DIR, "Build_Track_Real_Estate_Final_Internship_Report.docx")
    doc.save(out_file)
    print(f"Document saved to: {out_file}")
    return out_file

if __name__ == "__main__":
    build_document()
