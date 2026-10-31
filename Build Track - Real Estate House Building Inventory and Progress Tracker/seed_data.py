import os
from werkzeug.security import generate_password_hash
from db import get_db, query_db, init_db

def seed_database():
    print("Ensuring database tables exist...")
    init_db()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) AS cnt FROM admins;")
        if cursor.fetchone()['cnt'] > 0:
            print("Database already contains records. Clearing existing records for clean seeding...")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            for table in [
                'stock_updates', 'construction_updates', 'inventory_transactions',
                'material_requirements', 'builder_house_assignments', 'houses',
                'materials', 'suppliers', 'builders', 'admins'
            ]:
                cursor.execute(f"TRUNCATE TABLE `{table}`;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.commit()

        print("1. Seeding Admins...")
        admin_pass = generate_password_hash("Admin@123")
        cursor.execute("""
            INSERT INTO admins (username, full_name, email, password_hash)
            VALUES (%s, %s, %s, %s);
        """, ("admin", "System Administrator", "admin@buildtrack.com", admin_pass))
        admin_id = cursor.lastrowid

        print("2. Seeding Builders / Site Engineers...")
        builder_pass = generate_password_hash("Builder@123")
        builders_data = [
            ("Kumar Site Engineer", "kumar@buildtrack.com", "+91 98765 43210", builder_pass, "Active"),
            ("Rajesh Civil Engineer", "rajesh@buildtrack.com", "+91 98765 43211", builder_pass, "Active"),
            ("Suresh Project Engineer", "suresh@buildtrack.com", "+91 98765 43212", builder_pass, "Inactive"),
            ("Manoj Site Supervisor", "manoj@buildtrack.com", "+91 98765 43213", builder_pass, "Active"),
        ]
        builder_ids = {}
        for name, email, phone, pwd, status in builders_data:
            cursor.execute("""
                INSERT INTO builders (builder_name, email, phone, password_hash, status)
                VALUES (%s, %s, %s, %s, %s);
            """, (name, email, phone, pwd, status))
            builder_ids[email] = cursor.lastrowid

        print("3. Seeding Suppliers...")
        suppliers_data = [
            ("UltraTech Cement Depot", "R. Ramesh", "+91 94441 12233", "sales@ultratechdepot.com", "Industrial Estate, Sector 4", "Cement, Ready-Mix Concrete, PCC Concrete"),
            ("Tata Tiscon Steel Traders", "V. Sundar", "+91 94442 23344", "orders@tatatiscon.com", "Steel Yard, Ring Road", "TMT Steel Rods, Binding Wire, Reinforcement Steel"),
            ("Supreme Pipes & Sanitations", "K. Karthik", "+91 94443 34455", "supply@supremepipes.com", "Pipe Market, Main Bazaar", "PVC Pipes, CPVC Pipes, Valves, Pipe Fittings, Sanitary Fixtures"),
            ("Kajaria & Somany Tiles Hub", "M. Dinesh", "+91 94444 45566", "contact@kajariahub.com", "Tile Arcade, Highway Bypass", "Floor Tiles, Wall Tiles, Granite, Marble, Tile Adhesive"),
            ("Asian Paints & Chemicals", "S. Vijay", "+91 94445 56677", "dealer@asianpaintsdealer.com", "Paint Nagar, Cross Street", "Wall Putty, Primer, Emulsion Paint, Waterproofing Chemical"),
            ("L&T Electricals & Hardware", "P. Mohan", "+91 94446 67788", "info@ltelectricals.com", "Electrical Complex, City Centre", "Wires, Cables, Switches, MCB, Conduit Pipes, Hardware")
        ]
        supplier_ids = {}
        for sname, contact, phone, email, addr, mats in suppliers_data:
            cursor.execute("""
                INSERT INTO suppliers (supplier_name, contact_person, phone, email, address, materials_supplied)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (sname, contact, phone, email, addr, mats))
            supplier_ids[sname] = cursor.lastrowid

        print("4. Seeding Materials Master Catalog...")
        materials_data = [
            # Foundation & Civil
            ("Cement", "Foundation", "Bags", 80.00, 100.00, 380.00, supplier_ids["UltraTech Cement Depot"], "Main Shed A1"),
            ("M-Sand", "Foundation", "Tons", 45.00, 20.00, 1200.00, supplier_ids["UltraTech Cement Depot"], "Sand Yard Bay 1"),
            ("River Sand", "Foundation", "Tons", 10.00, 15.00, 2500.00, supplier_ids["UltraTech Cement Depot"], "Sand Yard Bay 2"),
            ("20mm Aggregate / Blue Metal", "Foundation", "Tons", 60.00, 25.00, 950.00, supplier_ids["UltraTech Cement Depot"], "Aggregate Yard A"),
            ("40mm Aggregate", "Foundation", "Tons", 35.00, 20.00, 850.00, supplier_ids["UltraTech Cement Depot"], "Aggregate Yard B"),
            ("Red Bricks", "Brickwork", "Nos", 18000.00, 5000.00, 9.50, supplier_ids["UltraTech Cement Depot"], "Open Yard Lot 1"),
            ("AAC Blocks", "Brickwork", "Nos", 1200.00, 500.00, 65.00, supplier_ids["UltraTech Cement Depot"], "Open Yard Lot 2"),
            ("Cement Blocks", "Brickwork", "Nos", 900.00, 500.00, 42.00, supplier_ids["UltraTech Cement Depot"], "Open Yard Lot 3"),
            ("Rubble Stone", "Foundation", "Tons", 25.00, 10.00, 600.00, supplier_ids["UltraTech Cement Depot"], "Quarry Yard"),
            ("PCC Concrete", "Foundation", "Cu.m", 15.00, 10.00, 3800.00, supplier_ids["UltraTech Cement Depot"], "Batching Area"),
            ("Ready-Mix Concrete", "RCC / Structure", "Cu.m", 0.00, 15.00, 4200.00, supplier_ids["UltraTech Cement Depot"], "Batching Plant"),
            ("Cover Blocks", "RCC / Structure", "Nos", 850.00, 200.00, 3.50, supplier_ids["UltraTech Cement Depot"], "Store Rack S1"),
            ("Shuttering Plywood", "RCC / Structure", "Sheets", 75.00, 30.00, 1400.00, supplier_ids["UltraTech Cement Depot"], "Timber Shed"),
            ("Scaffolding Materials", "RCC / Structure", "Sets", 18.00, 10.00, 5000.00, supplier_ids["Tata Tiscon Steel Traders"], "Metal Shed M1"),
            
            # Steel & Binding
            ("TMT Steel Rods", "RCC / Structure", "Kg", 5500.00, 2000.00, 68.00, supplier_ids["Tata Tiscon Steel Traders"], "Steel Yard Bay 1"),
            ("Binding Wire", "RCC / Structure", "Kg", 150.00, 50.00, 85.00, supplier_ids["Tata Tiscon Steel Traders"], "Store Rack S2"),
            ("Wall Ties", "Brickwork", "Nos", 450.00, 200.00, 12.00, supplier_ids["Tata Tiscon Steel Traders"], "Store Rack S2"),
            ("Lintel Materials", "Brickwork", "Meters", 40.00, 20.00, 220.00, supplier_ids["Tata Tiscon Steel Traders"], "Precast Yard"),
            
            # Roofing
            ("Roofing Tiles", "Roofing / Slab", "Nos", 600.00, 200.00, 45.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T1"),
            
            # Chemicals & Waterproofing
            ("Waterproofing Chemical", "Waterproofing", "Litres", 120.00, 50.00, 280.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C1"),
            ("Anti-Termite Chemical", "Foundation", "Litres", 30.00, 20.00, 450.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C1"),
            ("Waterproofing Membrane", "Waterproofing", "Rolls", 22.00, 10.00, 1800.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C2"),
            ("Protective Coating", "Waterproofing", "Litres", 40.00, 30.00, 340.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C2"),
            ("Polymer", "Waterproofing", "Litres", 50.00, 25.00, 310.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C2"),
            
            # Plastering
            ("Plastering Sand", "Plastering", "Tons", 28.00, 15.00, 1300.00, supplier_ids["UltraTech Cement Depot"], "Sand Yard Bay 3"),
            ("Plaster Mesh", "Plastering", "Rolls", 25.00, 10.00, 650.00, supplier_ids["Asian Paints & Chemicals"], "Store Rack S3"),
            ("Corner Beads", "Plastering", "Nos", 120.00, 50.00, 45.00, supplier_ids["Asian Paints & Chemicals"], "Store Rack S3"),
            
            # Plumbing
            ("PVC Pipes 4 inch", "Plumbing", "Meters", 180.00, 50.00, 110.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P1"),
            ("CPVC Pipes 1 inch", "Plumbing", "Meters", 220.00, 60.00, 145.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P2"),
            ("UPVC Pipes 1.5 inch", "Plumbing", "Meters", 110.00, 40.00, 130.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P2"),
            ("SWR Pipes", "Plumbing", "Meters", 0.00, 30.00, 160.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P3"),
            ("HDPE Pipes", "Plumbing", "Meters", 80.00, 30.00, 95.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P3"),
            ("Pipe Elbows & Tees", "Plumbing", "Nos", 350.00, 100.00, 28.00, supplier_ids["Supreme Pipes & Sanitations"], "Fitting Bins F1"),
            ("Pipe Couplers & Reducers", "Plumbing", "Nos", 240.00, 80.00, 32.00, supplier_ids["Supreme Pipes & Sanitations"], "Fitting Bins F2"),
            ("Brass Valves & Unions", "Plumbing", "Nos", 65.00, 25.00, 180.00, supplier_ids["Supreme Pipes & Sanitations"], "Fitting Bins F3"),
            ("Pipe Clamps", "Plumbing", "Nos", 400.00, 150.00, 15.00, supplier_ids["Supreme Pipes & Sanitations"], "Hardware Bin H1"),
            ("Western Toilet / WC", "Bathroom", "Nos", 14.00, 5.00, 4500.00, supplier_ids["Supreme Pipes & Sanitations"], "Sanitary Store S1"),
            ("Indian Toilet", "Bathroom", "Nos", 8.00, 3.00, 1800.00, supplier_ids["Supreme Pipes & Sanitations"], "Sanitary Store S1"),
            ("Wash Basin", "Bathroom", "Nos", 18.00, 8.00, 1600.00, supplier_ids["Supreme Pipes & Sanitations"], "Sanitary Store S2"),
            ("Health Faucet", "Bathroom", "Nos", 25.00, 10.00, 650.00, supplier_ids["Supreme Pipes & Sanitations"], "Sanitary Store S2"),
            ("Shower Set", "Bathroom", "Nos", 16.00, 8.00, 1200.00, supplier_ids["Supreme Pipes & Sanitations"], "Sanitary Store S2"),
            ("Water Taps", "Plumbing", "Nos", 70.00, 30.00, 450.00, supplier_ids["Supreme Pipes & Sanitations"], "Fitting Bins F4"),
            ("Floor Trap & Drain Cover", "Plumbing", "Nos", 55.00, 20.00, 120.00, supplier_ids["Supreme Pipes & Sanitations"], "Fitting Bins F4"),
            ("Water Tank 1000L", "Plumbing", "Nos", 7.00, 3.00, 6500.00, supplier_ids["Supreme Pipes & Sanitations"], "Tank Yard"),
            ("Geyser 25L", "Plumbing", "Nos", 6.00, 4.00, 7200.00, supplier_ids["Supreme Pipes & Sanitations"], "Appliance Store A1"),
            ("Kitchen Sink Stainless Steel", "Kitchen", "Nos", 9.00, 5.00, 3200.00, supplier_ids["Supreme Pipes & Sanitations"], "Kitchen Store K1"),
            ("Kitchen Sink Tap", "Kitchen", "Nos", 12.00, 5.00, 950.00, supplier_ids["Supreme Pipes & Sanitations"], "Kitchen Store K1"),
            
            # Electrical
            ("House Wiring Cable 1.5 sq.mm", "Electrical", "Coils", 35.00, 15.00, 1850.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E1"),
            ("House Wiring Cable 2.5 sq.mm", "Electrical", "Coils", 30.00, 15.00, 2650.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E1"),
            ("Main Cable 4 sq.mm", "Electrical", "Coils", 12.00, 8.00, 4200.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E1"),
            ("Earthing Wire", "Electrical", "Kg", 45.00, 20.00, 320.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E2"),
            ("PVC Conduit Pipes", "Electrical", "Meters", 320.00, 100.00, 25.00, supplier_ids["L&T Electricals & Hardware"], "Conduit Bay C1"),
            ("Flexible Conduit", "Electrical", "Meters", 120.00, 50.00, 18.00, supplier_ids["L&T Electricals & Hardware"], "Conduit Bay C1"),
            ("Junction Boxes", "Electrical", "Nos", 180.00, 60.00, 22.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E2"),
            ("Modular Switches", "Electrical", "Nos", 300.00, 100.00, 65.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E3"),
            ("Modular Sockets", "Electrical", "Nos", 210.00, 80.00, 95.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E3"),
            ("Modular Plates", "Electrical", "Nos", 130.00, 50.00, 110.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E3"),
            ("MCB 16A/32A", "Electrical", "Nos", 50.00, 20.00, 220.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E4"),
            ("Distribution Board 8-Way", "Electrical", "Nos", 11.00, 5.00, 1450.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E4"),
            ("RCCB / ELCB", "Electrical", "Nos", 8.00, 5.00, 1850.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E4"),
            ("Ceiling Fans", "Electrical", "Nos", 22.00, 10.00, 2100.00, supplier_ids["L&T Electricals & Hardware"], "Appliance Store A2"),
            ("LED Lights", "Electrical", "Nos", 110.00, 50.00, 180.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E5"),
            ("Exhaust Fans", "Electrical", "Nos", 12.00, 6.00, 1150.00, supplier_ids["L&T Electricals & Hardware"], "Appliance Store A2"),
            ("Earthing Rod & Compound", "Electrical", "Sets", 9.00, 5.00, 1250.00, supplier_ids["L&T Electricals & Hardware"], "Electrical Store E2"),
            
            # Doors & Windows
            ("Main Teak Wood Door", "Doors and Windows", "Nos", 5.00, 3.00, 18500.00, supplier_ids["L&T Electricals & Hardware"], "Carpentry Store W1"),
            ("Internal Flush Doors", "Doors and Windows", "Nos", 18.00, 10.00, 3800.00, supplier_ids["L&T Electricals & Hardware"], "Carpentry Store W1"),
            ("Bathroom PVC Doors", "Doors and Windows", "Nos", 12.00, 8.00, 2400.00, supplier_ids["L&T Electricals & Hardware"], "Carpentry Store W2"),
            ("UPVC Window Frames & Glass", "Doors and Windows", "Sets", 15.00, 8.00, 5500.00, supplier_ids["L&T Electricals & Hardware"], "Window Yard"),
            ("Window Safety Grills", "Doors and Windows", "Sets", 16.00, 8.00, 2200.00, supplier_ids["Tata Tiscon Steel Traders"], "Window Yard"),
            ("Stainless Steel Hinges", "Doors and Windows", "Pairs", 120.00, 50.00, 90.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H2"),
            ("Door Mortise Locks", "Doors and Windows", "Nos", 22.00, 10.00, 1250.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H2"),
            ("Tower Bolts & Door Closers", "Doors and Windows", "Nos", 65.00, 30.00, 160.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H2"),
            ("Mosquito Mesh", "Doors and Windows", "sq.ft", 250.00, 100.00, 25.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H3"),
            
            # Flooring & Tiling
            ("Vitrified Floor Tiles 2x2", "Flooring", "Boxes", 180.00, 60.00, 750.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T1"),
            ("Glazed Wall Tiles", "Flooring", "Boxes", 95.00, 40.00, 550.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T2"),
            ("Anti-Skid Bathroom Tiles", "Flooring", "Boxes", 70.00, 30.00, 480.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T2"),
            ("Granite Countertop Slab", "Flooring", "sq.ft", 110.00, 50.00, 160.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Stone Yard S1"),
            ("Italian Marble", "Flooring", "sq.ft", 90.00, 50.00, 280.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Stone Yard S2"),
            ("Tile Adhesive", "Flooring", "Bags", 45.00, 20.00, 420.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T3"),
            ("Tile Grout", "Flooring", "Kg", 60.00, 25.00, 85.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T3"),
            
            # Painting & Finishing
            ("Acrylic Wall Putty", "Painting", "Bags", 65.00, 30.00, 820.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P1"),
            ("Interior Primer", "Painting", "Litres", 85.00, 40.00, 180.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P1"),
            ("Interior Emulsion Paint", "Painting", "Litres", 110.00, 50.00, 340.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P2"),
            ("Exterior Primer", "Painting", "Litres", 55.00, 30.00, 195.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P2"),
            ("Exterior Weatherproof Paint", "Painting", "Litres", 80.00, 40.00, 420.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P2"),
            ("Paint Thinner", "Painting", "Litres", 35.00, 20.00, 110.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P3"),
            ("Sandpaper & Crack Filler", "Painting", "Packs", 40.00, 20.00, 150.00, supplier_ids["Asian Paints & Chemicals"], "Paint Store P3"),
            
            # External Works
            ("Compound Wall Bricks", "External Works", "Nos", 4500.00, 2000.00, 8.50, supplier_ids["UltraTech Cement Depot"], "Open Yard Lot 4"),
            ("Main MS Gate", "External Works", "Sets", 3.00, 2.00, 22000.00, supplier_ids["Tata Tiscon Steel Traders"], "Fabrication Yard"),
            ("Interlocking Paving Blocks", "External Works", "Nos", 1500.00, 500.00, 18.00, supplier_ids["Kajaria & Somany Tiles Hub"], "Tile Bay T4"),
            ("Drainage & Rainwater Pipes", "External Works", "Meters", 75.00, 40.00, 140.00, supplier_ids["Supreme Pipes & Sanitations"], "Pipe Rack P4"),
            
            # Hardware & Miscellaneous
            ("Steel Nails & Screws", "Hardware / Miscellaneous", "Kg", 60.00, 25.00, 110.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H4"),
            ("Nuts, Bolts & Washers", "Hardware / Miscellaneous", "Kg", 45.00, 20.00, 130.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H4"),
            ("Silicone Sealant & Adhesives", "Hardware / Miscellaneous", "Tubes", 35.00, 15.00, 240.00, supplier_ids["Asian Paints & Chemicals"], "Chemical Store C3"),
            ("Cutting & Grinding Discs", "Hardware / Miscellaneous", "Nos", 75.00, 30.00, 65.00, supplier_ids["L&T Electricals & Hardware"], "Hardware Bin H5"),
        ]

        material_ids = {}
        for mname, cat, unit, avail, min_lvl, price, sup_id, loc in materials_data:
            cursor.execute("""
                INSERT INTO materials (material_name, category, unit, available_quantity, minimum_stock_level, unit_price, supplier_id, storage_location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (mname, cat, unit, avail, min_lvl, price, sup_id, loc))
            material_ids[mname] = cursor.lastrowid

        print("5. Seeding Houses...")
        houses_data = [
            ("H-001", "Villa Green", "2 BHK", 1200.00, "Palm Meadows, Plot 14", "Foundation", 15.00, "Under Construction", "2026-06-01", "2027-02-28", "Corner plot villa with east-facing entrance."),
            ("H-002", "Sunrise Court", "2 BHK", 1250.00, "Royal Gardens, Phase 1", "Brickwork", 45.00, "Under Construction", "2026-04-15", "2026-12-15", "Standard residential 2 BHK with covered car porch."),
            ("H-003", "Grand Horizon", "3 BHK", 1600.00, "Metro City Phase 2", "Electrical", 65.00, "Under Construction", "2026-02-10", "2026-10-31", "Premium 3 BHK duplex layout with terrace garden."),
            ("H-004", "Skyline Heights", "3 BHK", 1700.00, "Lake View Township", "Flooring", 78.00, "Under Construction", "2025-11-01", "2026-09-30", "Spacious 3 BHK independent house near lake promenade."),
            ("H-005", "Classic Residency", "2 BHK", 1200.00, "Green Valley Avenue", "Completed", 100.00, "Completed", "2025-05-15", "2026-05-30", "Fully finished house handed over to quality inspection."),
        ]
        house_ids = {}
        for hnum, htype, bhk, area, loc, stage, prog, status, sdate, edate, notes in houses_data:
            cursor.execute("""
                INSERT INTO houses (house_number, house_type, bhk, area_sqft, location, construction_stage, progress_pct, status, start_date, expected_completion_date, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (hnum, htype, bhk, area, loc, stage, prog, status, sdate, edate, notes))
            house_ids[hnum] = cursor.lastrowid

        print("6. Assigning Builders to Houses...")
        assignments = [
            (builder_ids["kumar@buildtrack.com"], house_ids["H-001"], "Primary site engineer for foundation phase"),
            (builder_ids["kumar@buildtrack.com"], house_ids["H-002"], "Managing brickwork and masonry execution"),
            (builder_ids["kumar@buildtrack.com"], house_ids["H-005"], "Supervised full construction until completion"),
            (builder_ids["rajesh@buildtrack.com"], house_ids["H-003"], "Civil lead handling electrical and plumbing fit-outs"),
            (builder_ids["rajesh@buildtrack.com"], house_ids["H-004"], "Supervising flooring, tile installation, and finishes"),
            (builder_ids["manoj@buildtrack.com"], house_ids["H-001"], "Assisting with site material stock inspections"),
        ]
        for b_id, h_id, notes in assignments:
            cursor.execute("""
                INSERT INTO builder_house_assignments (builder_id, house_id, status, notes)
                VALUES (%s, %s, 'Active', %s);
            """, (b_id, h_id, notes))

        print("7. Defining Material Requirements...")
        requirements_templates = {
            "H-001": [
                ("Cement", 500.00), ("TMT Steel Rods", 2000.00), ("Red Bricks", 10000.00),
                ("M-Sand", 25.00), ("Vitrified Floor Tiles 2x2", 100.00), ("Interior Emulsion Paint", 50.00)
            ],
            "H-002": [
                ("Cement", 550.00), ("TMT Steel Rods", 2200.00), ("Red Bricks", 12000.00),
                ("M-Sand", 30.00), ("Vitrified Floor Tiles 2x2", 110.00), ("Interior Emulsion Paint", 55.00)
            ],
            "H-003": [
                ("Cement", 700.00), ("TMT Steel Rods", 3000.00), ("Red Bricks", 15000.00),
                ("M-Sand", 40.00), ("Vitrified Floor Tiles 2x2", 150.00), ("Interior Emulsion Paint", 75.00)
            ],
            "H-004": [
                ("Cement", 750.00), ("TMT Steel Rods", 3200.00), ("Red Bricks", 16000.00),
                ("M-Sand", 42.00), ("Vitrified Floor Tiles 2x2", 160.00), ("Interior Emulsion Paint", 80.00)
            ],
            "H-005": [
                ("Cement", 500.00), ("TMT Steel Rods", 2000.00), ("Red Bricks", 10000.00),
                ("M-Sand", 25.00), ("Vitrified Floor Tiles 2x2", 100.00), ("Interior Emulsion Paint", 50.00)
            ]
        }

        for hnum, reqs in requirements_templates.items():
            hid = house_ids[hnum]
            for mname, qty in reqs:
                mid = material_ids[mname]
                cursor.execute("""
                    INSERT INTO material_requirements (house_id, material_id, required_quantity, notes)
                    VALUES (%s, %s, %s, %s);
                """, (hid, mid, qty, f"Initial structural estimate for {hnum}"))

        print("8. Seeding Material Inward Transactions (Stock IN)...")
        inward_records = [
            ("Cement", supplier_ids["UltraTech Cement Depot"], 200.00, 380.00, "2026-08-20", "INV-UTC-9821", house_ids["H-001"], "Batch inward for foundation work"),
            ("TMT Steel Rods", supplier_ids["Tata Tiscon Steel Traders"], 3000.00, 68.00, "2026-08-22", "INV-TAT-4412", house_ids["H-001"], "Reinforcement steel inward"),
            ("Red Bricks", supplier_ids["UltraTech Cement Depot"], 10000.00, 9.50, "2026-08-25", "INV-BRK-1099", house_ids["H-002"], "First truckload for wall construction"),
            ("Vitrified Floor Tiles 2x2", supplier_ids["Kajaria & Somany Tiles Hub"], 150.00, 750.00, "2026-08-28", "INV-KAJ-6523", house_ids["H-004"], "Vitrified tiles for living & bedroom"),
            ("Interior Emulsion Paint", supplier_ids["Asian Paints & Chemicals"], 100.00, 340.00, "2026-09-01", "INV-ASP-3140", house_ids["H-005"], "Emulsion paint consignment")
        ]
        for mname, sid, qty, price, date, inv, hid, notes in inward_records:
            mid = material_ids[mname]
            total = qty * price
            cursor.execute("""
                INSERT INTO inventory_transactions 
                (transaction_type, material_id, house_id, supplier_id, quantity, unit_price, total_cost, transaction_date, invoice_number, purpose, notes, status)
                VALUES ('IN', %s, %s, %s, %s, %s, %s, %s, %s, 'Supplier Delivery', %s, 'COMPLETED');
            """, (mid, hid, sid, qty, price, total, date, inv, notes))

        print("9. Seeding Construction Updates (Approved & Pending)...")
        const_updates = [
            # Approved updates
            (house_ids["H-001"], builder_ids["kumar@buildtrack.com"], "Foundation", 15.00, "Excavation and PCC concrete bed laid", "Footing reinforcement in progress", "Site soil dry, excavation on schedule", "2026-08-25", "APPROVED", admin_id, "2026-08-26 10:00:00", "Approved after site inspection."),
            (house_ids["H-002"], builder_ids["kumar@buildtrack.com"], "Brickwork", 45.00, "Ground floor perimeter brick masonry completed", "First floor lintel level brickwork", "Curing completed for 7 days", "2026-08-28", "APPROVED", admin_id, "2026-08-29 11:30:00", "Quality of mortar verified."),
            (house_ids["H-003"], builder_ids["rajesh@buildtrack.com"], "Electrical", 65.00, "Concealed conduit laying and junction boxes fixed", "Main distribution board and circuit wiring", "Earthing pit dug and tested", "2026-09-01", "APPROVED", admin_id, "2026-09-02 09:15:00", "Conduit test passed."),
            (house_ids["H-005"], builder_ids["kumar@buildtrack.com"], "Completed", 100.00, "Full painting, final plumbing fixtures, cleaning and keys ready", "None", "Ready for handover", "2026-05-25", "APPROVED", admin_id, "2026-05-26 16:00:00", "Handover clearance given."),
            
            # PENDING updates for demo approval!
            (house_ids["H-001"], builder_ids["kumar@buildtrack.com"], "Foundation", 25.00, "Footing columns cast and curing completed", "Plinth beam shuttering and bar bending", "Awaiting beam shuttering inspection", "2026-09-04", "PENDING", None, None, None),
            (house_ids["H-004"], builder_ids["rajesh@buildtrack.com"], "Flooring", 82.00, "Living room and kitchen vitrified tile flooring completed", "Master bedroom wooden finish tiles and skirting", "Adhesive setting well, grouting pending", "2026-09-05", "PENDING", None, None, None)
        ]
        for hid, bid, stage, prog, done, pend, rem, udate, status, rev_by, rev_date, rev_notes in const_updates:
            cursor.execute("""
                INSERT INTO construction_updates
                (house_id, builder_id, stage, progress_pct, work_completed, work_pending, remarks, update_date, status, reviewed_by, review_date, review_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (hid, bid, stage, prog, done, pend, rem, udate, status, rev_by, rev_date, rev_notes))

        print("10. Seeding Stock Updates & Usage (Approved & Pending)...")
        stock_updates_data = [
            # Approved stock updates (H-001 Foundation)
            (house_ids["H-001"], builder_ids["kumar@buildtrack.com"], material_ids["Cement"], 0.00, 100.00, 50.00, 50.00, "2026-08-26", "Foundation footing concrete batching", "APPROVED", admin_id, "2026-08-27 10:00:00", "Approved and deducted from stock."),
            (house_ids["H-001"], builder_ids["kumar@buildtrack.com"], material_ids["TMT Steel Rods"], 0.00, 1000.00, 600.00, 400.00, "2026-08-27", "Footing cage rebar binding", "APPROVED", admin_id, "2026-08-28 10:00:00", "Approved."),
            
            # Approved stock updates (H-002 Brickwork)
            (house_ids["H-002"], builder_ids["kumar@buildtrack.com"], material_ids["Red Bricks"], 0.00, 5000.00, 3500.00, 1500.00, "2026-08-29", "Ground floor brick masonry mortar work", "APPROVED", admin_id, "2026-08-30 09:30:00", "Approved."),
            (house_ids["H-002"], builder_ids["kumar@buildtrack.com"], material_ids["Cement"], 50.00, 50.00, 30.00, 70.00, "2026-08-30", "Brickwork mortar preparation", "APPROVED", admin_id, "2026-08-31 09:30:00", "Approved."),

            # PENDING stock updates for Admin to review and approve!
            (house_ids["H-001"], builder_ids["kumar@buildtrack.com"], material_ids["Cement"], 50.00, 50.00, 40.00, 60.00, "2026-09-04", "Plinth beam casting concrete mix", "PENDING", None, None, None),
            (house_ids["H-003"], builder_ids["rajesh@buildtrack.com"], material_ids["PVC Conduit Pipes"], 100.00, 100.00, 60.00, 140.00, "2026-09-05", "Living room and master bed wall chasing conduit insertion", "PENDING", None, None, None)
        ]
        for hid, bid, mid, open_s, recv, used, rem, udate, remarks, status, rev_by, rev_date, rev_notes in stock_updates_data:
            cursor.execute("""
                INSERT INTO stock_updates
                (house_id, builder_id, material_id, opening_stock, material_received, material_used, remaining_stock, update_date, remarks, status, reviewed_by, review_date, review_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (hid, bid, mid, open_s, recv, used, rem, udate, remarks, status, rev_by, rev_date, rev_notes))

            # For approved material usage, also record the inventory transaction OUT
            if status == "APPROVED":
                cursor.execute("""
                    INSERT INTO inventory_transactions
                    (transaction_type, material_id, house_id, builder_id, quantity, unit_price, total_cost, transaction_date, purpose, notes, status)
                    SELECT 'OUT', %s, %s, %s, %s, unit_price, (unit_price * %s), %s, %s, 'Approved site usage', 'COMPLETED'
                    FROM materials WHERE material_id = %s;
                """, (mid, hid, bid, used, used, udate, rev_notes, mid))

        conn.commit()
        print("Database seeded successfully with realistic residential construction data!")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {repr(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_database()
