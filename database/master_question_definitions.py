"""
Comprehensive Master Question Bank Definitions for Personalized Career Recommendation System.
Generates 317+ level-stratified questions across all 19 standardized assessment sections.
"""

import json
from pathlib import Path


def get_all_master_questions():
    questions = []

    def make_mcq(options_data, correct_idx):
        opts = []
        for i, (text, val) in enumerate(options_data):
            is_corr = (i == correct_idx)
            opts.append({
                "option_text": text,
                "option_value": str(val),
                "score": 100.0 if is_corr else 0.0,
                "is_correct": is_corr,
                "display_order": i + 1
            })
        return opts

    def make_rating(low="Strongly Disagree", high="Strongly Agree"):
        return [
            {"option_text": f"1 - {low}", "option_value": "1", "score": 20.0, "is_correct": False, "display_order": 1},
            {"option_text": "2 - Slight", "option_value": "2", "score": 40.0, "is_correct": False, "display_order": 2},
            {"option_text": "3 - Moderate / Neutral", "option_value": "3", "score": 60.0, "is_correct": False, "display_order": 3},
            {"option_text": "4 - High", "option_value": "4", "score": 80.0, "is_correct": False, "display_order": 4},
            {"option_text": f"5 - {high}", "option_value": "5", "score": 100.0, "is_correct": False, "display_order": 5}
        ]

    def make_freq():
        return [
            {"option_text": "1 - Never", "option_value": "1", "score": 20.0, "is_correct": False, "display_order": 1},
            {"option_text": "2 - Rarely", "option_value": "2", "score": 40.0, "is_correct": False, "display_order": 2},
            {"option_text": "3 - Sometimes", "option_value": "3", "score": 60.0, "is_correct": False, "display_order": 3},
            {"option_text": "4 - Often", "option_value": "4", "score": 80.0, "is_correct": False, "display_order": 4},
            {"option_text": "5 - Very Often", "option_value": "5", "score": 100.0, "is_correct": False, "display_order": 5}
        ]

    # Helper to add question
    def q(code, text, sec_id, q_type, c_min, c_max, diff, skill, stream="All", req=True, order=1, expl="", opts=None):
        questions.append({
            "question_code": code,
            "question_text": text,
            "section_id": sec_id,
            "question_type": q_type,
            "class_min": c_min,
            "class_max": c_max,
            "difficulty": diff,
            "skill_category": skill,
            "stream_specific": stream,
            "is_required": req,
            "display_order": order,
            "explanation": expl,
            "options": opts or []
        })

    # ========================================================
    # SECTION 1: ACADEMIC PROFILE (15 Questions)
    # ========================================================
    # Middle School (7-8)
    q("ACAD_78_01", "Which school subject do you naturally look forward to the most during the week?", 1, "MCQ", 7, 8, "Easy", "learning_ability", "All", True, 1, "Exploratory subject interest",
      make_mcq([("Mathematics and logical puzzles", "A"), ("Science experiments and nature", "B"), ("Computers and digital technology", "C"), ("Social studies, languages, or visual arts", "D")], 0))
    q("ACAD_78_02", "How do you prefer to learn new concepts in class?", 1, "RATING", 7, 8, "Easy", "learning_ability", "All", True, 2, "Active vs passive learning preference",
      make_rating("Passive Memorization", "Hands-on Practical Exploration"))
    q("ACAD_78_03", "When studying for an exam, how often do you make summary notes or mind maps?", 1, "RATING", 7, 8, "Easy", "learning_ability", "All", True, 3, "Study habits",
      make_rating("Never", "Always create structured notes"))
    q("ACAD_78_04", "How easily do you understand word problems in science or mathematics?", 1, "RATING", 7, 8, "Easy", "learning_ability", "All", True, 4, "Foundational comprehension",
      make_rating("Need Significant Help", "Understand Immediately"))
    q("ACAD_78_05", "Which learning activity excites you the most in school?", 1, "MCQ", 7, 8, "Easy", "learning_ability", "All", True, 5, "Learning mode preference",
      make_mcq([("Building models or doing science experiments", "A"), ("Solving challenging math riddles", "B"), ("Writing stories or debating topics", "C"), ("Drawing, coding, or creating digital graphics", "D")], 0))

    # Secondary (9-10)
    q("ACAD_910_01", "When planning for Class 11-12, which academic stream aligns closest with your career vision?", 1, "MCQ", 9, 10, "Medium", "learning_ability", "All", True, 6, "Stream transition",
      make_mcq([("Science (Physics, Chemistry, Math / Bio)", "A"), ("Commerce (Accountancy, Economics, Business)", "B"), ("Humanities (Psychology, Political Science, History)", "C"), ("Vocational / Computer Applications / Design", "D")], 0))
    q("ACAD_910_02", "How confident do you feel preparing for comprehensive board-level exams?", 1, "RATING", 9, 10, "Medium", "learning_ability", "All", True, 7, "Academic resilience",
      make_rating("Highly Anxious", "Fully Prepared & Confident"))
    q("ACAD_910_03", "When encountering a difficult academic chapter, what is your first response?", 1, "MCQ", 9, 10, "Medium", "learning_ability", "All", True, 8, "Problem approach",
      make_mcq([("Break it into smaller sections and research online", "A"), ("Ask a teacher or peer for detailed guidance", "B"), ("Re-read the textbook multiple times until clear", "C"), ("Move to another topic and return later", "D")], 0))
    q("ACAD_910_04", "How often do you connect concepts learned in science/math to real-world applications?", 1, "RATING", 9, 10, "Medium", "learning_ability", "All", True, 9, "Conceptual integration",
      make_rating("Rarely Connect", "Constantly Identify Real-world Applications"))
    q("ACAD_910_05", "In group study sessions, which role do you naturally assume?", 1, "MCQ", 9, 10, "Medium", "learning_ability", "All", True, 10, "Peer learning dynamic",
      make_mcq([("Explaining concepts and solving tough questions", "A"), ("Organizing topics, timetable, and materials", "B"), ("Asking probing questions and debating viewpoints", "C"), ("Taking detailed notes and summarizing conclusions", "D")], 0))

    # Senior Secondary (11-12)
    q("ACAD_1112_01", "What is your primary academic preparation focus alongside your Class 11-12 curriculum?", 1, "MCQ", 11, 12, "Medium", "learning_ability", "All", True, 11, "Post-secondary focus",
      make_mcq([("National entrance exams (JEE, NEET, NDA, CLAT, CUET, CA Foundation)", "A"), ("Board examination top percentile and university merit scholarships", "B"), ("Building portfolio for design, coding, or entrepreneurship", "C"), ("International standardized admissions (SAT, AP, IELTS/TOEFL)", "D")], 0))
    q("ACAD_1112_02", "How effectively do you manage independent self-study schedules (4+ hours daily)?", 1, "RATING", 11, 12, "Hard", "learning_ability", "All", True, 12, "Self-directed rigor",
      make_rating("Struggle with Consistency", "Highly Disciplined & Productive"))
    q("ACAD_1112_03", "When analyzing complex theoretical papers or case studies, how easily do you extract key insights?", 1, "RATING", 11, 12, "Hard", "learning_ability", "All", True, 13, "Advanced comprehension",
      make_rating("Find it Overwhelming", "Extract & Synthesize Insights Rapidly"))
    q("ACAD_1112_04", "How do you evaluate your academic performance over the past 2 years?", 1, "RATING", 11, 12, "Medium", "learning_ability", "All", True, 14, "Self-assessment",
      make_rating("Below My Potential", "Consistent Top-Tier Performance"))
    q("ACAD_1112_05", "Which higher-education pathway represents your primary aspiration?", 1, "MCQ", 11, 12, "Medium", "learning_ability", "All", True, 15, "Higher ed aspiration",
      make_mcq([("Top Tier Technical / Medical Institution (IIT, AIIMS, NIT, BITS)", "A"), ("Prestigious Commerce / Economics / Law College (SRCC, NLU, IIM-IPM)", "B"), ("Top Liberal Arts / Design / Media Institute (Ashoka, NID, NIFT)", "C"), ("Global University Undergraduate Degree Abroad", "D")], 0))

    # ========================================================
    # SECTION 2: MATHEMATICAL ABILITY (35 Questions)
    # ========================================================
    # Class 7-8 Math (12)
    q("MATH_78_01", "If 3 pens cost Rs. 45, what is the cost of 7 pens at the same rate?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 1, "Unitary method",
      make_mcq([("Rs. 95", "A"), ("Rs. 105", "B"), ("Rs. 115", "C"), ("Rs. 120", "D")], 1))
    q("MATH_78_02", "What is 25% of 240?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 2, "Percentages",
      make_mcq([("50", "A"), ("60", "B"), ("70", "C"), ("80", "D")], 1))
    q("MATH_78_03", "Find the perimeter of a rectangle with length 14 cm and width 8 cm.", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 3, "Geometry perimeter",
      make_mcq([("44 cm", "A"), ("112 cm", "B"), ("48 cm", "C"), ("52 cm", "D")], 0))
    q("MATH_78_04", "If x + 15 = 42, what is the value of 2x - 10?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 4, "Linear algebra",
      make_mcq([("44", "A"), ("54", "B"), ("34", "C"), ("48", "D")], 0))
    q("MATH_78_05", "A train travels 180 km in 3 hours. What is its speed in km/h?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 5, "Speed distance time",
      make_mcq([("50 km/h", "A"), ("60 km/h", "B"), ("65 km/h", "C"), ("70 km/h", "D")], 1))
    q("MATH_78_06", "What is the average (mean) of 12, 18, 24, 30, and 36?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 6, "Averages",
      make_mcq([("22", "A"), ("24", "B"), ("26", "C"), ("28", "D")], 1))
    q("MATH_78_07", "Simplify: 3/4 + 2/5", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 7, "Fractions",
      make_mcq([("5/9", "A"), ("23/20", "B"), ("11/20", "C"), ("15/20", "D")], 1))
    q("MATH_78_08", "The sum of angles in any triangle is always equal to:", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 8, "Basic geometry",
      make_mcq([("90 degrees", "A"), ("180 degrees", "B"), ("270 degrees", "C"), ("360 degrees", "D")], 1))
    q("MATH_78_09", "If a square has an area of 81 sq cm, what is its perimeter?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 9, "Square area & perimeter",
      make_mcq([("36 cm", "A"), ("45 cm", "B"), ("18 cm", "C"), ("72 cm", "D")], 0))
    q("MATH_78_10", "What is the value of 2^4 + 3^2?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 10, "Exponents",
      make_mcq([("23", "A"), ("25", "B"), ("32", "C"), ("17", "D")], 1))
    q("MATH_78_11", "A shopkeeper buys an item for Rs. 200 and sells it for Rs. 250. What is the profit percentage?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 11, "Profit & loss",
      make_mcq([("20%", "A"), ("25%", "B"), ("30%", "C"), ("50%", "D")], 1))
    q("MATH_78_12", "If 5 workers can build a wall in 12 days, how many days will 10 workers take at the same pace?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 12, "Inverse proportion",
      make_mcq([("6 days", "A"), ("8 days", "B"), ("24 days", "C"), ("10 days", "D")], 0))

    # Class 9-10 Math (12)
    q("MATH_910_01", "Solve for x: 2x^2 - 8x = 0. The positive solution is:", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 13, "Quadratic equations",
      make_mcq([("x = 2", "A"), ("x = 4", "B"), ("x = 8", "C"), ("x = 0", "D")], 1))
    q("MATH_910_02", "In a right triangle, if sin(theta) = 3/5, what is tan(theta)?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 14, "Trigonometry",
      make_mcq([("3/4", "A"), ("4/3", "B"), ("4/5", "C"), ("5/3", "D")], 0))
    q("MATH_910_03", "Find the distance between the points (2, 3) and (6, 6) in the coordinate plane.", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 15, "Coordinate geometry",
      make_mcq([("4 units", "A"), ("5 units", "B"), ("7 units", "C"), ("25 units", "D")], 1))
    q("MATH_910_04", "What is the probability of getting a prime number when rolling a standard 6-sided die?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 16, "Probability",
      make_mcq([("1/3", "A"), ("1/2", "B"), ("2/3", "C"), ("1/6", "D")], 1))
    q("MATH_910_05", "The 10th term of an arithmetic progression with first term a = 3 and common difference d = 4 is:", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 17, "Arithmetic progressions",
      make_mcq([("39", "A"), ("43", "B"), ("36", "C"), ("40", "D")], 0))
    q("MATH_910_06", "If the volume of a sphere is (4/3) * pi * r^3, doubling the radius increases the volume by a factor of:", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 18, "Mensuration & scaling",
      make_mcq([("2", "A"), ("4", "B"), ("6", "C"), ("8", "D")], 3))
    q("MATH_910_07", "If log10(x) = 3, what is the value of x?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 19, "Logarithms",
      make_mcq([("30", "A"), ("100", "B"), ("1000", "C"), ("3000", "D")], 2))
    q("MATH_910_08", "Solve the system: x + y = 10 and x - y = 4. What is the value of x * y?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 20, "Linear systems",
      make_mcq([("21", "A"), ("24", "B"), ("18", "C"), ("28", "D")], 0))
    q("MATH_910_09", "If a line has equation 3x + 2y = 12, what is its y-intercept?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 21, "Coordinate geometry intercepts",
      make_mcq([("(0, 4)", "A"), ("(0, 6)", "B"), ("(4, 0)", "C"), ("(6, 0)", "D")], 1))
    q("MATH_910_10", "A cone and a cylinder have the same radius and height. The ratio of cone volume to cylinder volume is:", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 22, "Solid geometry ratios",
      make_mcq([("1:2", "A"), ("1:3", "B"), ("2:3", "C"), ("1:4", "D")], 1))
    q("MATH_910_11", "Find the sum of all interior angles of a regular hexagon (6 sides):", 2, "MCQ", 9, 10, "Hard", "mathematical_ability", "All", True, 23, "Polygons",
      make_mcq([("540 degrees", "A"), ("720 degrees", "B"), ("900 degrees", "C"), ("1080 degrees", "D")], 1))
    q("MATH_910_12", "If roots of x^2 - kx + 16 = 0 are equal, what is the positive value of k?", 2, "MCQ", 9, 10, "Hard", "mathematical_ability", "All", True, 24, "Discriminant",
      make_mcq([("4", "A"), ("8", "B"), ("16", "C"), ("64", "D")], 1))

    # Class 11-12 Math (11)
    q("MATH_1112_01", "What is the derivative d/dx (x^3 * sin(x)) at x = 0?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Science-PCM", True, 25, "Calculus differentiation",
      make_mcq([("0", "A"), ("1", "B"), ("3", "C"), ("Undefined", "D")], 0))
    q("MATH_1112_02", "Evaluate the definite integral: Integral from 0 to 2 of (3x^2) dx.", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Science-PCM", True, 26, "Definite integrals",
      make_mcq([("6", "A"), ("8", "B"), ("12", "C"), ("16", "D")], 1))
    q("MATH_1112_03", "If vectors A = 2i + 3j and B = 3i - 2j, what is their dot product A . B?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Science-PCM", True, 27, "Vector dot product",
      make_mcq([("0 (orthogonal)", "A"), ("12", "B"), ("13", "C"), ("-6", "D")], 0))
    q("MATH_1112_04", "If matrix A is a 2x2 matrix with rows [2, 3] and [1, 4], what is the determinant det(A)?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "All", True, 28, "Determinants",
      make_mcq([("5", "A"), ("8", "B"), ("11", "C"), ("-5", "D")], 0))
    q("MATH_1112_05", "What is the limit of (sin(3x) / x) as x approaches 0?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Science-PCM", True, 29, "Calculus limits",
      make_mcq([("0", "A"), ("1", "B"), ("3", "C"), ("Does not exist", "D")], 2))
    q("MATH_1112_06", "In how many distinct ways can the letters of the word 'CAREER' be arranged?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "All", True, 30, "Permutations & combinations",
      make_mcq([("120", "A"), ("180", "B"), ("360", "C"), ("720", "D")], 1))
    q("MATH_1112_07", "If the compound interest on Rs. 10,000 at 10% annual interest compounded annually for 2 years is calculated, the total amount is:", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Commerce", True, 31, "Financial mathematics",
      make_mcq([("Rs. 12,000", "A"), ("Rs. 12,100", "B"), ("Rs. 12,250", "C"), ("Rs. 13,000", "D")], 1))
    q("MATH_1112_08", "What is the standard deviation of the numbers [5, 5, 5, 5, 5]?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "All", True, 32, "Statistics variance",
      make_mcq([("0", "A"), ("1", "B"), ("5", "C"), ("25", "D")], 0))
    q("MATH_1112_09", "If P(A) = 0.6, P(B) = 0.5, and A and B are independent events, what is P(A and B)?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "All", True, 33, "Independent probability",
      make_mcq([("0.1", "A"), ("0.3", "B"), ("0.55", "C"), ("1.1", "D")], 1))
    q("MATH_1112_10", "Find the maximum value of f(x) = -x^2 + 6x - 5.", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "All", True, 34, "Quadratic optimization",
      make_mcq([("3", "A"), ("4", "B"), ("5", "C"), ("9", "D")], 1))
    q("MATH_1112_11", "If marginal cost MC = 4x + 10, what is the total cost function C(x) assuming fixed cost is 50?", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Commerce", True, 35, "Applied economic calculus",
      make_mcq([("2x^2 + 10x + 50", "A"), ("4x^2 + 10x + 50", "B"), ("2x^2 + 10", "C"), ("4x + 60", "D")], 0))

    # ========================================================
    # SECTION 3: LOGICAL REASONING (25 Questions)
    # ========================================================
    # Middle (7-8)
    q("LOGIC_78_01", "Complete the sequence: 4, 9, 16, 25, 36, ___", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 1, "Square numbers sequence",
      make_mcq([("45", "A"), ("49", "B"), ("54", "C"), ("64", "D")], 1))
    q("LOGIC_78_02", "Book is to Reading as Fork is to: ___", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 2, "Verbal analogy",
      make_mcq([("Writing", "A"), ("Eating", "B"), ("Cooking", "C"), ("Drinking", "D")], 1))
    q("LOGIC_78_03", "If all dogs are animals and Tommy is a dog, then Tommy is:", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 3, "Simple deduction",
      make_mcq([("An animal", "A"), ("A bird", "B"), ("Not an animal", "C"), ("Cannot be determined", "D")], 0))
    q("LOGIC_78_04", "Find the odd one out: Circle, Square, Triangle, Cube, Pentagon", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 4, "Dimensional classification",
      make_mcq([("Square", "A"), ("Cube (3D shape)", "B"), ("Triangle", "C"), ("Circle", "D")], 1))
    q("LOGIC_78_05", "Complete the letter sequence: B, D, F, H, ___", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 5, "Alphabet pattern",
      make_mcq([("I", "A"), ("J", "B"), ("K", "C"), ("L", "D")], 1))
    q("LOGIC_78_06", "A clock shows 3:15. What is the angle between the hour hand and minute hand approximately?", 3, "MCQ", 7, 8, "Medium", "logical_reasoning", "All", True, 6, "Clock logic",
      make_mcq([("0 degrees", "A"), ("7.5 degrees", "B"), ("15 degrees", "C"), ("30 degrees", "D")], 1))
    q("LOGIC_78_07", "If CAT = 24 and DOG = 26, what is the code for PIG (P=16, I=9, G=7)?", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 7, "Coding decoding",
      make_mcq([("30", "A"), ("32", "B"), ("34", "C"), ("36", "D")], 1))
    q("LOGIC_78_08", "Pointing to a photograph, Rohit says: 'She is the mother of my father''s only son.' Rohit is her:", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 8, "Blood relations",
      make_mcq([("Brother", "A"), ("Son", "B"), ("Father", "C"), ("Uncle", "D")], 1))

    # Secondary (9-10)
    q("LOGIC_910_01", "Statements: Some doctors are teachers. All teachers are researchers. Conclusion: Some doctors are researchers.", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 9, "Syllogism",
      make_mcq([("Definitely True", "A"), ("Definitely False", "B"), ("Cannot be determined", "C"), ("Partially True", "D")], 0))
    q("LOGIC_910_02", "In a race: Alex finished before Ben but after Chris. David finished before Chris. Who won the race?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 10, "Ranking sequence",
      make_mcq([("Alex", "A"), ("Ben", "B"), ("Chris", "C"), ("David", "D")], 3))
    q("LOGIC_910_03", "Find the missing term: 2, 6, 12, 20, 30, ___", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 11, "Difference sequence n*(n+1)",
      make_mcq([("40", "A"), ("42", "B"), ("44", "C"), ("46", "D")], 1))
    q("LOGIC_910_04", "If 'NORTH' is coded as 'MQSUI', how is 'SOUTH' coded using the same offset rule?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 12, "Letter transposition",
      make_mcq([("RPTSG", "A"), ("TRVSI", "B"), ("RPVSI", "C"), ("RPTUI", "D")], 1))
    q("LOGIC_910_05", "A man walks 3 km North, then 4 km East. How far is he from his starting point?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 13, "Direction Pythagoras",
      make_mcq([("5 km", "A"), ("7 km", "B"), ("12 km", "C"), ("1 km", "D")], 0))
    q("LOGIC_910_06", "Which Venn diagram best represents: Mammals, Whales, Reptiles?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 14, "Venn classification",
      make_mcq([("Whales inside Mammals, Reptiles completely separate", "A"), ("Three intersecting circles", "B"), ("Whales and Reptiles inside Mammals", "C"), ("Three disjoint circles", "D")], 0))
    q("LOGIC_910_07", "If P > Q, Q >= R, and R > S, which relationship must be FALSE?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 15, "Inequality deduction",
      make_mcq([("P > S", "A"), ("Q > S", "B"), ("S > P", "C"), ("P > R", "D")], 2))
    q("LOGIC_910_08", "Six friends are seated around a circular table facing the center. A is opposite D. B is right of A. Where is B relative to D?", 3, "MCQ", 9, 10, "Hard", "logical_reasoning", "All", True, 16, "Circular arrangement",
      make_mcq([("Opposite D", "A"), ("Left of D", "B"), ("Two seats to left of D", "C"), ("Right of D", "D")], 1))

    # Senior (11-12)
    q("LOGIC_1112_01", "Statement: 'If inflation rises, interest rates will increase.' Given: Interest rates did not increase. Conclusion:", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 17, "Modus Tollens logic",
      make_mcq([("Inflation definitely rose", "A"), ("Inflation did not rise", "B"), ("Inflation remained unchanged", "C"), ("No conclusion possible", "D")], 1))
    q("LOGIC_1112_02", "In a logic grid with 4 variables (Person, City, Profession, Car), how many binary relationships exist?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 18, "Combinatorial logic",
      make_mcq([("4", "A"), ("6 pairs", "B"), ("12", "C"), ("16", "D")], 1))
    q("LOGIC_1112_03", "Which assumption is necessary for the argument: 'Autonomous cars reduce accidents because human errors cause 90% of crashes'?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 19, "Critical reasoning assumptions",
      make_mcq([("Autonomous systems do not introduce new fatal errors at a higher rate", "A"), ("Human drivers will completely stop driving immediately", "B"), ("Car insurance will no longer be needed", "C"), ("All roads will have 5G coverage", "D")], 0))
    q("LOGIC_1112_04", "If A implies B, and B implies (C or D), but D is known to be false, what follows if A is true?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 20, "Propositional logic chaining",
      make_mcq([("C is definitely True", "A"), ("C is False", "B"), ("B is False", "C"), ("A is False", "D")], 0))
    q("LOGIC_1112_05", "Consider the sequence: 1, 1, 2, 3, 5, 8, 13, 21, ___. What is the ratio of term 8 to term 7 approximately?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 21, "Fibonacci Golden ratio",
      make_mcq([("1.414", "A"), ("1.618 (Golden Ratio)", "B"), ("2.718", "C"), ("3.141", "D")], 1))
    q("LOGIC_1112_06", "Find the statement that weakens the claim: 'Strict speed limits reduce highway fatalities.'", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 22, "Argument analysis",
      make_mcq([("Highways with reduced speed limits experienced severe congestion leading to higher low-speed collisions", "A"), ("Fewer cars were on the road during the study period", "B"), ("Police issued more speeding tickets", "C"), ("Drivers bought newer cars with airbags", "D")], 0))
    q("LOGIC_1112_07", "Data Sufficiency: Is x > 0? (1) x^2 = 25 (2) x^3 = 125. Which statement(s) are sufficient?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 23, "Data sufficiency",
      make_mcq([("Statement 1 alone is sufficient", "A"), ("Statement 2 alone is sufficient (x=5 only)", "B"), ("Both together are needed", "C"), ("Neither is sufficient", "D")], 1))
    q("LOGIC_1112_08", "A binary truth teller and liar puzzle: Guard A says 'Guard B always lies.' Guard B says 'We both tell the truth.' Who is telling the truth?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 24, "Knights & Knaves puzzle",
      make_mcq([("Guard A tells the truth; Guard B lies", "A"), ("Guard B tells the truth; Guard A lies", "B"), ("Both tell the truth", "C"), ("Both lie", "D")], 0))
    q("LOGIC_1112_09", "What is the logical negation of the statement: 'Every employee received a bonus'?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 25, "Predicate logic negation",
      make_mcq([("No employee received a bonus", "A"), ("At least one employee did not receive a bonus", "B"), ("All employees received a penalty", "C"), ("Some employees received a bonus", "D")], 1))

    # ========================================================
    # SECTION 4: SCIENTIFIC THINKING (25 Questions)
    # ========================================================
    # Middle (7-8)
    q("SCI_78_01", "Which process allows green plants to synthesize glucose using sunlight and carbon dioxide?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 1, "Photosynthesis",
      make_mcq([("Respiration", "A"), ("Photosynthesis", "B"), ("Transpiration", "C"), ("Fermentation", "D")], 1))
    q("SCI_78_02", "What is the boiling point of pure water at standard sea-level atmospheric pressure?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 2, "States of matter",
      make_mcq([("50 deg C", "A"), ("100 deg C", "B"), ("150 deg C", "C"), ("212 deg C only in Fahrenheit", "D")], 1))
    q("SCI_78_03", "Which subatomic particle carries a negative electrical charge?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 3, "Atomic structure",
      make_mcq([("Proton", "A"), ("Neutron", "B"), ("Electron", "C"), ("Nucleus", "D")], 2))
    q("SCI_78_04", "When a magnet is freely suspended horizontally, in which direction does it align?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 4, "Magnetism",
      make_mcq([("East-West", "A"), ("North-South", "B"), ("North-East", "C"), ("South-West", "D")], 1))
    q("SCI_78_05", "Which gas is primarily responsible for the greenhouse effect on Earth?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 5, "Environmental science",
      make_mcq([("Oxygen", "A"), ("Nitrogen", "B"), ("Carbon Dioxide", "C"), ("Argon", "D")], 2))
    q("SCI_78_06", "What organ in the human body filters metabolic waste from blood to form urine?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 6, "Human anatomy",
      make_mcq([("Lungs", "A"), ("Kidneys", "B"), ("Liver", "C"), ("Heart", "D")], 1))
    q("SCI_78_07", "Which simple machine consists of a grooved wheel with a rope running through it?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 7, "Simple machines",
      make_mcq([("Lever", "A"), ("Pulley", "B"), ("Inclined Plane", "C"), ("Wedge", "D")], 1))
    q("SCI_78_08", "What is the chemical formula for common table salt?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 8, "Basic chemistry",
      make_mcq([("H2O", "A"), ("NaCl", "B"), ("CO2", "C"), ("HCl", "D")], 1))

    # Secondary (9-10)
    q("SCI_910_01", "According to Newton's Second Law of Motion, Force (F) equals:", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 9, "Classical mechanics",
      make_mcq([("Mass x Velocity", "A"), ("Mass x Acceleration", "B"), ("Mass / Acceleration", "C"), ("Work / Time", "D")], 1))
    q("SCI_910_02", "What is the pH value of a completely neutral aqueous solution at 25 deg C?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 10, "Acids & bases",
      make_mcq([("0", "A"), ("7", "B"), ("14", "C"), ("1", "D")], 1))
    q("SCI_910_03", "Which cellular organelle is known as the 'powerhouse of the cell' due to ATP production?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 11, "Cell biology",
      make_mcq([("Ribosome", "A"), ("Mitochondria", "B"), ("Golgi apparatus", "C"), ("Endoplasmic reticulum", "D")], 1))
    q("SCI_910_04", "When white light passes through a glass prism, which color refracts (bends) the most?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 12, "Optics dispersion",
      make_mcq([("Red", "A"), ("Yellow", "B"), ("Violet", "C"), ("Green", "D")], 2))
    q("SCI_910_05", "According to Ohm's Law in electrical circuits, V equals:", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 13, "Electricity",
      make_mcq([("I * R", "A"), ("I / R", "B"), ("I^2 * R", "C"), ("R / I", "D")], 0))
    q("SCI_910_06", "Which element has the atomic number 6 and forms the backbone of organic molecules?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 14, "Periodic table",
      make_mcq([("Oxygen", "A"), ("Carbon", "B"), ("Nitrogen", "C"), ("Helium", "D")], 1))
    q("SCI_910_07", "What type of chemical reaction is: 2H2 + O2 -> 2H2O?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 15, "Chemical reactions",
      make_mcq([("Decomposition", "A"), ("Combination / Synthesis", "B"), ("Displacement", "C"), ("Double Displacement", "D")], 1))
    q("SCI_910_08", "According to Mendel's laws of inheritance, what is the phenotypic ratio in a standard monohybrid F2 cross?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 16, "Genetics",
      make_mcq([("1:1", "A"), ("3:1", "B"), ("9:3:3:1", "C"), ("1:2:1", "D")], 1))

    # Senior (11-12)
    q("SCI_1112_01", "In rotational mechanics, what is the rotational analogue of mass in linear motion?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 17, "Moment of inertia",
      make_mcq([("Torque", "A"), ("Moment of Inertia", "B"), ("Angular Momentum", "C"), ("Angular Velocity", "D")], 1))
    q("SCI_1112_02", "Which thermodynamic law states that the entropy of an isolated system always increases over time?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 18, "Thermodynamics",
      make_mcq([("Zeroth Law", "A"), ("First Law", "B"), ("Second Law", "C"), ("Third Law", "D")], 2))
    q("SCI_1112_03", "In organic chemistry, which reaction mechanism converts an alkyl halide to an alcohol with inversion of configuration?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 19, "Organic reaction mechanism",
      make_mcq([("SN1", "A"), ("SN2", "B"), ("E1", "C"), ("E2", "D")], 1))
    q("SCI_1112_04", "What is the primary function of restriction endonuclease enzymes in recombinant DNA technology?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCB", True, 20, "Biotechnology",
      make_mcq([("Ligate DNA fragments", "A"), ("Cleave DNA at specific palindromic sequences", "B"), ("Synthesize RNA primers", "C"), ("Amplify DNA via PCR", "D")], 1))
    q("SCI_1112_05", "In quantum mechanics, de Broglie wavelength lambda is inversely proportional to which particle property?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 21, "Quantum dual nature",
      make_mcq([("Energy", "A"), ("Linear Momentum (p)", "B"), ("Charge", "C"), ("Potential", "D")], 1))
    q("SCI_1112_06", "During cellular respiration in humans, what is the net yield of ATP produced per glucose molecule under aerobic conditions approximately?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCB", True, 22, "Biochemistry metabolism",
      make_mcq([("2 ATP", "A"), ("4 ATP", "B"), ("30 to 32 ATP", "C"), ("100 ATP", "D")], 2))
    q("SCI_1112_07", "Which law governs electromagnetic induction: 'The induced electromotive force is proportional to the rate of change of magnetic flux'?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 23, "Electromagnetism",
      make_mcq([("Ampere's Law", "A"), ("Faraday's Law", "B"), ("Coulomb's Law", "C"), ("Gauss's Law", "D")], 1))
    q("SCI_1112_08", "What structural feature gives aromatic compounds like benzene exceptional chemical stability?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "All", True, 24, "Aromaticity resonance",
      make_mcq([("Triple bonds", "A"), ("Delocalized pi electron ring resonance (Huckel's 4n+2 rule)", "B"), ("Ionic lattice energy", "C"), ("Hydrogen bonding", "D")], 1))
    q("SCI_1112_09", "Which neurochemical transmitter plays a central role in reward pathways and motor control?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCB", True, 25, "Neurobiology",
      make_mcq([("Dopamine", "A"), ("Insulin", "B"), ("Thyroxine", "C"), ("Glucagon", "D")], 0))

    # ========================================================
    # SECTION 5: PROBLEM SOLVING (20 Questions)
    # ========================================================
    # Middle (7-8)
    q("PS_78_01", "You have a 3-liter jug and a 5-liter jug with unlimited water. How can you measure exactly 4 liters?", 5, "MCQ", 7, 8, "Easy", "problem_solving", "All", True, 1, "Water jug puzzle",
      make_mcq([("Fill 5L, pour into 3L (leaving 2L in 5L jug), empty 3L, pour 2L into 3L, fill 5L, pour into 3L until full (leaving exactly 4L)", "A"), ("Fill 3L twice and pour into 5L", "B"), ("Fill half of both jugs", "C"), ("Cannot be done without a scale", "D")], 0))
    q("PS_78_02", "A farmer has chickens and cows. There are 10 heads and 28 legs. How many cows are there?", 5, "MCQ", 7, 8, "Easy", "problem_solving", "All", True, 2, "Heads & legs algebraic logic",
      make_mcq([("4 cows (and 6 chickens)", "A"), ("6 cows (and 4 chickens)", "B"), ("5 cows", "C"), ("3 cows", "D")], 0))
    q("PS_78_03", "When your home Wi-Fi stops working, what is your first systematic troubleshooting step?", 5, "MCQ", 7, 8, "Easy", "problem_solving", "All", True, 3, "Practical troubleshooting",
      make_mcq([("Check power, reboot the router, and verify on multiple devices", "A"), ("Immediately call a technician without checking", "B"), ("Assume internet is permanently broken", "C"), ("Turn off the computer and wait until tomorrow", "D")], 0))
    q("PS_78_04", "If you need to cut a 12-meter rope into 2-meter pieces, how many cuts must you make?", 5, "MCQ", 7, 8, "Easy", "problem_solving", "All", True, 4, "Boundary logic cuts",
      make_mcq([("5 cuts", "A"), ("6 cuts", "B"), ("7 cuts", "C"), ("4 cuts", "D")], 0))
    q("PS_78_05", "How do you handle unexpected setbacks during a science project?", 5, "RATING", 7, 8, "Easy", "problem_solving", "All", True, 5, "Resilience",
      make_rating("Give up immediately", "Analyze what failed and try alternative method"))
    q("PS_78_06", "Three switches outside a closed room control three light bulbs inside. You can only enter the room once. How do you find which switch controls which bulb?", 5, "MCQ", 7, 8, "Medium", "problem_solving", "All", True, 6, "Classic lateral thinking puzzle",
      make_mcq([("Turn on Switch 1 for 10 min, turn it off, turn on Switch 2, enter room: On bulb = Switch 2, Warm bulb = Switch 1, Cold bulb = Switch 3", "A"), ("Turn on all switches simultaneously", "B"), ("Turn on Switch 1 and hope for luck", "C"), ("Impossible without looking inside", "D")], 0))

    # Secondary (9-10)
    q("PS_910_01", "You are organizing a school festival with a fixed budget. Venue cost doubles unexpectedly. How do you resolve the budget deficit?", 5, "MCQ", 9, 10, "Medium", "problem_solving", "All", True, 7, "Resource constraint optimization",
      make_mcq([("Re-prioritize expenses, negotiate vendor discounts, and secure student club sponsorships", "A"), ("Cancel the festival immediately", "B"), ("Ignore the deficit and overspend", "C"), ("Ask every student for emergency cash", "D")], 0))
    q("PS_910_02", "In binary search algorithm, searching a sorted list of 1,000 items takes at most how many comparisons?", 5, "MCQ", 9, 10, "Medium", "problem_solving", "All", True, 8, "Algorithmic thinking",
      make_mcq([("10 comparisons (log2 1000 approx 10)", "A"), ("100 comparisons", "B"), ("500 comparisons", "C"), ("1,000 comparisons", "D")], 0))
    q("PS_910_03", "When writing a computer program that crashes with a runtime error, how do you locate the bug?", 5, "MCQ", 9, 10, "Medium", "problem_solving", "All", True, 9, "Debugging methodology",
      make_mcq([("Use print statements / debugger to trace variable state step-by-step", "A"), ("Delete all code and start from scratch blindly", "B"), ("Randomly modify lines hoping it works", "C"), ("Ignore the bug and submit the program", "D")], 0))
    q("PS_910_04", "How effectively do you break large ambiguous assignments into concrete sub-tasks?", 5, "RATING", 9, 10, "Medium", "problem_solving", "All", True, 10, "Decomposition capability",
      make_rating("Feel Overwhelmed", "Decompose into Structured Milestones"))
    q("PS_910_05", "A batch of 9 coins contains 1 counterfeit coin that is lighter than the others. Using a balance scale, what is the minimum number of weighings to guarantee finding it?", 5, "MCQ", 9, 10, "Medium", "problem_solving", "All", True, 11, "Ternary search weighing",
      make_mcq([("2 weighings (divide into 3 groups of 3)", "A"), ("3 weighings", "B"), ("4 weighings", "C"), ("1 weighing", "D")], 0))
    q("PS_910_06", "A leak drains a water tank in 6 hours, while a tap fills it in 4 hours. If both are open, how long does it take to fill the empty tank?", 5, "MCQ", 9, 10, "Medium", "problem_solving", "All", True, 12, "Pipes & cisterns rate problem",
      make_mcq([("10 hours", "A"), ("12 hours (1/4 - 1/6 = 1/12)", "B"), ("24 hours", "C"), ("2 hours", "D")], 1))
    q("PS_910_07", "How do you react when initial assumptions in a project turn out to be fundamentally flawed?", 5, "RATING", 9, 10, "Medium", "problem_solving", "All", True, 13, "Adaptive problem mindset",
      make_rating("Become Frustrated and Discard", "Pivot Rapidly and Reformulate Strategy"))

    # Senior (11-12)
    q("PS_1112_01", "In graph theory, finding the shortest path between all pairs of nodes efficiently uses which algorithm?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "Science-PCM", True, 14, "Algorithmic optimization",
      make_mcq([("Floyd-Warshall / Dijkstra with priority queue", "A"), ("Bubble Sort", "B"), ("Linear Search", "C"), ("Depth First Search only", "D")], 0))
    q("PS_1112_02", "A company faces supply chain disruption in raw materials. Which risk mitigation strategy is most robust?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "Commerce", True, 15, "Operations management",
      make_mcq([("Dual-sourcing from geographically diverse suppliers with safety stock buffer", "A"), ("Sole-sourcing from the cheapest supplier with zero inventory", "B"), ("Halting all production until market stabilizes", "C"), ("Increasing marketing spend", "D")], 0))
    q("PS_1112_03", "When designing a large-scale database for millions of users, how do you prevent bottleneck latency?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "All", True, 16, "System architecture optimization",
      make_mcq([("Indexing high-frequency query keys, caching, and horizontal sharding", "A"), ("Putting all data into a single unindexed table", "B"), ("Restarting the server every hour", "C"), ("Removing authentication security", "D")], 0))
    q("PS_1112_04", "How comfortable are you making high-stakes decisions under incomplete information?", 5, "RATING", 11, 12, "Hard", "problem_solving", "All", True, 17, "Ambiguity tolerance",
      make_rating("Completely Paralyzed by Uncertainty", "Thrive via Probabilistic Reasoning"))
    q("PS_1112_05", "Dynamic Programming is primarily applied to solve problems with which two properties?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "All", True, 18, "Dynamic programming criteria",
      make_mcq([("Overlapping Subproblems and Optimal Substructure", "A"), ("Greedy choice and unweighted edges", "B"), ("Random distribution and continuous variables", "C"), ("Linear equations and single variables", "D")], 0))
    q("PS_1112_06", "A hospital emergency room must triage patients effectively during a mass casualty event. What framework optimizes patient survival?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "Science-PCB", True, 19, "Clinical triage optimization",
      make_mcq([("START Triage based on airway, respiration rate, and perfusion", "A"), ("First come, first served regardless of severity", "B"), ("Alphabetical order by patient name", "C"), ("Treat minor injuries first", "D")], 0))
    q("PS_1112_07", "How do you systematically validate whether a proposed machine learning model is overfitting the training data?", 5, "MCQ", 11, 12, "Hard", "problem_solving", "All", True, 20, "ML validation methodology",
      make_mcq([("Evaluate on unseen test/validation sets and check cross-validation variance", "A"), ("Train for 1000 more epochs on the same training set", "B"), ("Remove all regularization constraints", "C"), ("Evaluate training accuracy only", "D")], 0))

    # ========================================================
    # SECTION 6: ANALYTICAL THINKING (18 Questions)
    # ========================================================
    # Middle (7-8)
    q("ANAL_78_01", "A bar chart shows sales: Mon=20, Tue=30, Wed=25, Thu=45, Fri=30. What was the percentage increase from Mon to Thu?", 6, "MCQ", 7, 8, "Easy", "analytical_ability", "All", True, 1, "Data interpretation",
      make_mcq([("50%", "A"), ("100%", "B"), ("125% ((45-20)/20 * 100)", "C"), ("150%", "D")], 2))
    q("ANAL_78_02", "If a pie chart has a slice representing 90 degrees, what percentage of the total does it represent?", 6, "MCQ", 7, 8, "Easy", "analytical_ability", "All", True, 2, "Pie chart angles",
      make_mcq([("20%", "A"), ("25% (90/360 * 100)", "B"), ("30%", "C"), ("50%", "D")], 1))
    q("ANAL_78_03", "When comparing two mobile phones, what do you look at to judge which offers better performance?", 6, "MCQ", 7, 8, "Easy", "analytical_ability", "All", True, 3, "Feature comparison",
      make_mcq([("Processor benchmarks, RAM, battery capacity, and display refresh rate", "A"), ("Only the color of the case", "B"), ("Only the celebrity in the advertisement", "C"), ("The weight of the box", "D")], 0))
    q("ANAL_78_04", "How easily do you spot patterns in tables of numbers?", 6, "RATING", 7, 8, "Easy", "analytical_ability", "All", True, 4, "Numerical pattern discernment",
      make_rating("Find tables confusing", "Instantly recognize numerical trends"))
    q("ANAL_78_05", "If City A has population 50,000 and 5 hospitals, while City B has population 120,000 and 10 hospitals, which city has better hospital availability per capita?", 6, "MCQ", 7, 8, "Easy", "analytical_ability", "All", True, 5, "Per capita analysis",
      make_mcq([("City A (1 per 10k vs 1 per 12k)", "A"), ("City B", "B"), ("Both are equal", "C"), ("Cannot be determined", "D")], 0))

    # Secondary (9-10)
    q("ANAL_910_01", "A line graph shows Company Revenue rising while Net Profit is falling. What is the most plausible analytical explanation?", 6, "MCQ", 9, 10, "Medium", "analytical_ability", "All", True, 6, "Financial chart analysis",
      make_mcq([("Operating expenses / cost of goods rose faster than revenue growth", "A"), ("Sales volume dropped to zero", "B"), ("Prices were raised too high", "C"), ("Company stopped paying taxes", "D")], 0))
    q("ANAL_910_02", "Correlation between Ice Cream Sales and Drowning Incidents is positive (r = 0.85). What explains this statistical relationship?", 6, "MCQ", 9, 10, "Medium", "analytical_ability", "All", True, 7, "Confounding variables",
      make_mcq([("A confounding third variable (Summer / High Temperature) causes both", "A"), ("Eating ice cream causes cramps and drowning", "B"), ("Drowning causes people to buy ice cream", "C"), ("The data is fake", "D")], 0))
    q("ANAL_910_03", "When reading a news article citing a statistical survey, how do you verify its credibility?", 6, "MCQ", 9, 10, "Medium", "analytical_ability", "All", True, 8, "Source critique",
      make_mcq([("Examine sample size, methodology, potential bias, and source peer review", "A"), ("Accept headline uncritically if it sounds interesting", "B"), ("Judge based on social media likes", "C"), ("Believe only if confirmed by friends", "D")], 0))
    q("ANAL_910_04", "How comfortable are you working with Excel / Google Sheets formulas to analyze datasets?", 6, "RATING", 9, 10, "Medium", "analytical_ability", "All", True, 9, "Spreadsheet analytical fluency",
      make_rating("No Experience", "Advanced Formulas & Pivot Tables"))
    q("ANAL_910_05", "In an A/B test of two website layouts: Layout A has 100 conversions from 1,000 visitors (10%). Layout B has 180 conversions from 1,500 visitors (12%). Which performed better?", 6, "MCQ", 9, 10, "Medium", "analytical_ability", "All", True, 10, "Conversion rate analysis",
      make_mcq([("Layout B (12% conversion rate)", "A"), ("Layout A", "B"), ("Both are identical", "C"), ("Need 1 million visitors to tell", "D")], 0))
    q("ANAL_910_06", "If median house price in a city is Rs. 50 Lakh while mean is Rs. 1.2 Crore, what does this indicate about the distribution?", 6, "MCQ", 9, 10, "Medium", "analytical_ability", "All", True, 11, "Skewed distributions",
      make_mcq([("Positively skewed with extreme luxury properties pulling the mean up", "A"), ("Symmetrical normal distribution", "B"), ("Negatively skewed distribution", "C"), ("Calculation error", "D")], 0))

    # Senior (11-12)
    q("ANAL_1112_01", "In statistical hypothesis testing, what does a p-value < 0.05 signify?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "All", True, 12, "Statistical significance",
      make_mcq([("Less than 5% probability the observed result occurred under null hypothesis (statistically significant)", "A"), ("95% chance the data is invalid", "B"), ("The experiment must be repeated 5 times", "C"), ("Effect size is exactly 0.05", "D")], 0))
    q("ANAL_1112_02", "In financial statement analysis, what does a current ratio of 2.5 indicate?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "Commerce", True, 13, "Liquidity ratio analysis",
      make_mcq([("Healthy short-term liquidity with Rs. 2.50 in current assets for every Rs. 1 in current liabilities", "A"), ("Company is insolvent", "B"), ("Debt exceeds assets", "C"), ("Zero cash flow", "D")], 0))
    q("ANAL_1112_03", "When evaluating a machine learning classifier on an imbalanced dataset (95% negative, 5% positive), which metric is misleading?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "All", True, 14, "Metric analysis under imbalance",
      make_mcq([("Raw Accuracy (predicting all negative yields 95% accuracy)", "A"), ("F1-Score", "B"), ("PR-AUC", "C"), ("Balanced Accuracy", "D")], 0))
    q("ANAL_1112_04", "How proficient are you at synthesizing complex multi-variable trade-offs in technical or economic scenarios?", 6, "RATING", 11, 12, "Hard", "analytical_ability", "All", True, 15, "Multi-criteria analysis",
      make_rating("Struggle with Multiple Trade-offs", "Perform Structured Multi-Criteria Decision Analysis"))
    q("ANAL_1112_05", "In regression analysis, what does an R-squared value of 0.88 indicate?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "All", True, 16, "Goodness of fit",
      make_mcq([("88% of variance in the dependent variable is explained by the independent variables", "A"), ("Model has 88% error", "B"), ("Correlation coefficient is 0.88", "C"), ("Only 12 data points exist", "D")], 0))
    q("ANAL_1112_06", "What is Simpson's Paradox in statistical analysis?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "All", True, 17, "Statistical paradoxes",
      make_mcq([("A trend that appears in aggregated groups reverses when divided into subgroups", "A"), ("Mean and median are always identical", "B"), ("Two variables cannot correlate", "C"), ("All survey respondents lie", "D")], 0))
    q("ANAL_1112_07", "How do you evaluate whether a price elasticity of demand equal to -2.4 represents elastic or inelastic demand?", 6, "MCQ", 11, 12, "Hard", "analytical_ability", "Commerce", True, 18, "Elasticity interpretation",
      make_mcq([("Highly Price Elastic (|E| > 1, 1% price cut increases demand by 2.4%)", "A"), ("Perfect Inelastic", "B"), ("Unit Elastic", "C"), ("Zero Elasticity", "D")], 0))

    # ========================================================
    # SECTION 7: COMMUNICATION (12 Questions)
    # ========================================================
    q("COMM_78_01", "How comfortable do you feel presenting a topic in front of your class?", 7, "RATING", 7, 8, "Easy", "communication", "All", True, 1, "Public speaking comfort",
      make_rating("Extremely Nervous", "Completely Confident & Articulate"))
    q("COMM_78_02", "When explaining a game rule to a friend who doesn't understand, how do you explain it?", 7, "MCQ", 7, 8, "Easy", "communication", "All", True, 2, "Clarity of instruction",
      make_mcq([("Break it down step-by-step with simple examples", "A"), ("Repeat the exact same words louder", "B"), ("Get impatient and play alone", "C"), ("Assume they will figure it out eventually", "D")], 0))
    q("COMM_78_03", "How often do you express your ideas through creative writing, essays, or journaling?", 7, "RATING", 7, 8, "Easy", "communication", "All", True, 3, "Written expression",
      make_rating("Never", "Frequently & Joyfully"))
    q("COMM_78_04", "When listening to a speaker, what is your primary focus?", 7, "MCQ", 7, 8, "Easy", "communication", "All", True, 4, "Active listening",
      make_mcq([("Understand their core message, tone, and underlying intent", "A"), ("Wait for my turn to interrupt and talk", "B"), ("Zone out and think about lunch", "C"), ("Criticize their pronunciation only", "D")], 0))

    q("COMM_910_01", "How effectively can you debate opposing viewpoints respectfully during school debates?", 7, "RATING", 9, 10, "Medium", "communication", "All", True, 5, "Debate ability",
      make_rating("Struggle with Rebuttals", "Construct Clear, Evidence-Based Arguments"))
    q("COMM_910_02", "Which writing style do you find most natural and engaging?", 7, "MCQ", 9, 10, "Medium", "communication", "All", True, 6, "Writing modality",
      make_mcq([("Persuasive essays and argumentative articles", "A"), ("Technical reports and step-by-step documentation", "B"), ("Creative fiction, poetry, and storytelling", "C"), ("Business emails and formal presentations", "D")], 0))
    q("COMM_910_03", "When a misunderstanding arises in a group project, what is your resolution strategy?", 7, "MCQ", 9, 10, "Medium", "communication", "All", True, 7, "Conflict resolution",
      make_mcq([("Initiate an open conversation to clarify expectations and align goals", "A"), ("Complain to the teacher immediately", "B"), ("Refuse to talk to group members", "C"), ("Do all the work in secret", "D")], 0))
    q("COMM_910_04", "How often do you read books, articles, or editorials outside of school syllabus?", 7, "RATING", 9, 10, "Medium", "communication", "All", True, 8, "Literary engagement",
      make_rating("Never", "Daily Habit"))

    q("COMM_1112_01", "How proficient are you in crafting structured formal proposals, research abstracts, or pitches?", 7, "RATING", 11, 12, "Hard", "communication", "All", True, 9, "Professional communication",
      make_rating("Beginner", "Executive Polish & Precision"))
    q("COMM_1112_02", "When tailoring a technical presentation for non-technical executives, how do you adapt your language?", 7, "MCQ", 11, 12, "Hard", "communication", "All", True, 10, "Audience adaptation",
      make_mcq([("Replace jargon with business impact metaphors, visuals, and clear bottom-line outcomes", "A"), ("Use heavy mathematical formulas to prove knowledge", "B"), ("Speak as quickly as possible", "C"), ("Cancel the presentation", "D")], 0))
    q("COMM_1112_03", "How effectively do you negotiate mutually beneficial outcomes during complex negotiations?", 7, "RATING", 11, 12, "Hard", "communication", "All", True, 11, "Negotiation capability",
      make_rating("Avoid Negotiation", "Master of Principled Negotiation"))
    q("COMM_1112_04", "Which medium do you find most impactful for inspiring others?", 7, "MCQ", 11, 12, "Hard", "communication", "All", True, 12, "Leadership rhetoric",
      make_mcq([("Inspiring keynote speech with compelling storytelling", "A"), ("In-depth whitepaper backed by quantitative data", "B"), ("Interactive multimedia video / visual prototype", "C"), ("One-on-one empathetic mentorship conversation", "D")], 0))

    # ========================================================
    # SECTION 8: CREATIVITY & DESIGN (12 Questions)
    # ========================================================
    q("CREAT_78_01", "How often do you come up with unique drawings, stories, or creative crafts?", 8, "RATING", 7, 8, "Easy", "creativity", "All", True, 1, "Creative expression",
      make_rating("Never", "Constantly Creating"))
    q("CREAT_78_02", "If you are given an ordinary cardboard box, what do you naturally envision?", 8, "MCQ", 7, 8, "Easy", "creativity", "All", True, 2, "Imaginative divergence",
      make_mcq([("A spaceship, medieval castle, or robotic prototype", "A"), ("Just trash to throw away", "B"), ("A plain container for books", "C"), ("Nothing special", "D")], 0))
    q("CREAT_78_03", "How much do you enjoy designing color schemes, room decorations, or avatars?", 8, "RATING", 7, 8, "Easy", "creativity", "All", True, 3, "Aesthetic sensitivity",
      make_rating("Not Interested", "Extremely Passionate"))
    q("CREAT_78_04", "When solving a problem, how often do you propose out-of-the-box unconventional ideas?", 8, "RATING", 7, 8, "Easy", "creativity", "All", True, 4, "Divergent thinking",
      make_rating("Stick to Standard Rules", "Always Explore Novel Angles"))

    q("CREAT_910_01", "How often do you use digital design tools (Canva, Photoshop, Figma, Blender, Video Editors)?", 8, "RATING", 9, 10, "Medium", "creativity", "All", True, 5, "Digital creation",
      make_rating("Never Used", "Proficient Digital Creator"))
    q("CREAT_910_02", "When designing a poster for a school event, what is your top design priority?", 8, "MCQ", 9, 10, "Medium", "creativity", "All", True, 6, "Visual hierarchy",
      make_mcq([("Clear visual hierarchy, balanced typography, and striking color contrast", "A"), ("Filling every square inch with dense text", "B"), ("Using 15 different random fonts", "C"), ("Copying someone else's poster exactly", "D")], 0))
    q("CREAT_910_03", "How easily do you improvise when musical instruments, drama scripts, or design constraints change?", 8, "RATING", 9, 10, "Medium", "creativity", "All", True, 7, "Creative improvisation",
      make_rating("Freeze Up", "Improvise Creatively with Ease"))
    q("CREAT_910_04", "Which artistic / creative discipline attracts you the most?", 8, "MCQ", 9, 10, "Medium", "creativity", "All", True, 8, "Creative domain",
      make_mcq([("UI/UX Design, 3D Animation, and Game Art", "A"), ("Film-making, Photography, and Video Editing", "B"), ("Music Composition, Audio Production, or Performing Arts", "C"), ("Architecture, Fashion, or Interior Design", "D")], 0))

    q("CREAT_1112_01", "Design Thinking consists of which standardized 5-stage iterative framework?", 8, "MCQ", 11, 12, "Hard", "creativity", "All", True, 9, "Design thinking methodology",
      make_mcq([("Empathize -> Define -> Ideate -> Prototype -> Test", "A"), ("Code -> Compile -> Debug -> Ship -> Forget", "B"), ("Budget -> Spend -> Build -> Sell -> Close", "C"), ("Advertise -> Pitch -> Discount -> Sign -> Deliver", "D")], 0))
    q("CREAT_1112_02", "How do you evaluate the aesthetic and functional harmony of a consumer product (e.g., smartphone or luxury watch)?", 8, "RATING", 11, 12, "Hard", "creativity", "All", True, 10, "Industrial design appreciation",
      make_rating("Never Think About Design", "Deeply Analyze Materiality, Ergonomics & Form-Factor"))
    q("CREAT_1112_03", "In visual branding, what does 'Kerning' refer to?", 8, "MCQ", 11, 12, "Hard", "creativity", "All", True, 11, "Typography terminology",
      make_mcq([("Adjusting spacing between individual letter characters in typography", "A"), ("Compressing video files", "B"), ("Mixing CMYK ink pigments", "C"), ("Rendering 3D polygon meshes", "D")], 0))
    q("CREAT_1112_04", "How often do you develop original intellectual property (screenplays, patentable concepts, apps, music)?", 8, "RATING", 11, 12, "Hard", "creativity", "All", True, 12, "Original IP generation",
      make_rating("Never", "Actively Building Creative Portfolio"))

    # ========================================================
    # SECTION 9: DIGITAL & COMPUTATIONAL (15 Questions)
    # ========================================================
    q("DIGI_78_01", "What does 'CPU' stand for in a computer system?", 9, "MCQ", 7, 8, "Easy", "digital_ability", "All", True, 1, "Computer basics",
      make_mcq([("Central Processing Unit", "A"), ("Central Power Utility", "B"), ("Computer Printing Unit", "C"), ("Control Processing Unit", "D")], 0))
    q("DIGI_78_02", "How interested are you in learning how video games or mobile apps are coded?", 9, "RATING", 7, 8, "Easy", "digital_ability", "All", True, 2, "Coding interest",
      make_rating("Not Interested", "Extremely Interested"))
    q("DIGI_78_03", "Which keyboard shortcut is universally used to copy highlighted text on Windows/Linux?", 9, "MCQ", 7, 8, "Easy", "digital_ability", "All", True, 3, "Digital literacy shortcut",
      make_mcq([("Ctrl + C", "A"), ("Ctrl + V", "B"), ("Ctrl + Z", "C"), ("Ctrl + X", "D")], 0))
    q("DIGI_78_04", "What is an algorithm in computing?", 9, "MCQ", 7, 8, "Easy", "digital_ability", "All", True, 4, "Algorithm concept",
      make_mcq([("A step-by-step set of instructions to solve a specific problem", "A"), ("A piece of hardware inside the monitor", "B"), ("A computer virus", "C"), ("A type of power cable", "D")], 0))
    q("DIGI_78_05", "How comfortable are you searching the internet to learn new software tools?", 9, "RATING", 7, 8, "Easy", "digital_ability", "All", True, 5, "Self-directed digital learning",
      make_rating("Struggle without Help", "Completely Self-Reliant"))

    q("DIGI_910_01", "In programming languages (Python, JavaScript, C++), what is a 'Loop' used for?", 9, "MCQ", 9, 10, "Medium", "digital_ability", "All", True, 6, "Programming constructs",
      make_mcq([("Repeating a block of code multiple times while a condition is met", "A"), ("Shutting down the operating system", "B"), ("Playing background audio in games", "C"), ("Increasing monitor brightness", "D")], 0))
    q("DIGI_910_02", "What is the primary difference between RAM (Random Access Memory) and SSD Storage?", 9, "MCQ", 9, 10, "Medium", "digital_ability", "All", True, 7, "Hardware architecture",
      make_mcq([("RAM is fast volatile working memory; SSD is persistent long-term storage", "A"), ("RAM stores files permanently when powered off", "B"), ("SSD is only used for audio files", "C"), ("RAM and SSD are identical", "D")], 0))
    q("DIGI_910_03", "How frequently do you write code or build digital automation scripts?", 9, "RATING", 9, 10, "Medium", "digital_ability", "All", True, 8, "Coding practice",
      make_rating("Never Coded", "Code Weekly / Build Projects"))
    q("DIGI_910_04", "What is 'Artificial Intelligence / Machine Learning' fundamentally doing?", 9, "MCQ", 9, 10, "Medium", "digital_ability", "All", True, 9, "AI concept",
      make_mcq([("Learning statistical patterns from large datasets to make predictions/decisions", "A"), ("Possessing human consciousness and emotions", "B"), ("Replacing all electronic hardware with magic", "C"), ("A simple calculator program", "D")], 0))
    q("DIGI_910_05", "Which protocol secures website communications by encrypting traffic between browser and server?", 9, "MCQ", 9, 10, "Medium", "digital_ability", "All", True, 10, "Web security",
      make_mcq([("HTTPS (SSL/TLS)", "A"), ("HTTP", "B"), ("FTP", "C"), ("SMTP", "D")], 0))

    q("DIGI_1112_01", "What is the time complexity of searching an element in a balanced Hash Map on average?", 9, "MCQ", 11, 12, "Hard", "digital_ability", "All", True, 11, "Data structures complexity",
      make_mcq([("O(1) Constant Time", "A"), ("O(log N)", "B"), ("O(N) Linear Time", "C"), ("O(N^2)", "D")], 0))
    q("DIGI_1112_02", "In cloud computing, what does 'Serverless Computing' (e.g., AWS Lambda, Google Cloud Functions) mean?", 9, "MCQ", 11, 12, "Hard", "digital_ability", "Science-PCM", True, 12, "Cloud architecture",
      make_mcq([("Developers run backend code on-demand without provisioning or managing dedicated servers", "A"), ("No computers are used anywhere in the cloud", "B"), ("Applications only work when offline", "C"), ("Servers operate without electricity", "D")], 0))
    q("DIGI_1112_03", "In relational database design, what is the role of a 'Foreign Key'?", 9, "MCQ", 11, 12, "Hard", "digital_ability", "All", True, 13, "Database design",
      make_mcq([("Enforces referential integrity by linking a record in one table to the primary key of another", "A"), ("Encrypts passwords in memory", "B"), ("Speeds up Wi-Fi connection", "C"), ("Deletes redundant tables automatically", "D")], 0))
    q("DIGI_1112_04", "How proficient are you in Git version control workflows (commit, branch, pull request, merge)?", 9, "RATING", 11, 12, "Hard", "digital_ability", "All", True, 14, "DevOps fluency",
      make_rating("Never Used Git", "Proficient in Git Collaboration"))
    q("DIGI_1112_05", "What is the core principle behind asymmetric public-key cryptography (e.g., RSA)?", 9, "MCQ", 11, 12, "Hard", "digital_ability", "Science-PCM", True, 15, "Cybersecurity cryptography",
      make_mcq([("A mathematical pair of keys: Public Key encrypts, Private Key decrypts", "A"), ("Sharing the same secret password with everyone", "B"), ("Hiding files in invisible folders", "C"), ("Changing IP addresses every second", "D")], 0))

    # ========================================================
    # SECTION 10: LEARNING ABILITY & AGILITY (12 Questions)
    # ========================================================
    q("LEARN_78_01", "When learning a completely new topic, how quickly do you grasp the core concept?", 10, "RATING", 7, 8, "Easy", "learning_ability", "All", True, 1, "Learning speed",
      make_rating("Take Long Time", "Grasp Core Concept Rapidly"))
    q("LEARN_78_02", "If you receive feedback that your work has mistakes, what is your mindset?", 10, "MCQ", 7, 8, "Easy", "learning_ability", "All", True, 2, "Growth mindset",
      make_mcq([("View feedback as an opportunity to improve and correct errors", "A"), ("Feel offended and ignore the feedback", "B"), ("Stop trying completely", "C"), ("Blame the teacher", "D")], 0))
    q("LEARN_78_03", "How often do you read Wikipedia or watch educational science/history videos just out of curiosity?", 10, "RATING", 7, 8, "Easy", "learning_ability", "All", True, 3, "Intellectual curiosity",
      make_rating("Never", "Constantly Exploring"))
    q("LEARN_78_04", "When a computer program or game introduces new rules, how do you learn them?", 10, "MCQ", 7, 8, "Easy", "learning_ability", "All", True, 4, "Adaptive learning",
      make_mcq([("Experiment actively and figure out the mechanics through trial and error", "A"), ("Give up if it is not immediately obvious", "B"), ("Wait for someone else to play for me", "C"), ("Complain that the game is too hard", "D")], 0))

    q("LEARN_910_01", "How effectively do you transfer knowledge from one domain (e.g., math) to solve problems in another (e.g., economics)?", 10, "RATING", 9, 10, "Medium", "learning_ability", "All", True, 5, "Cross-domain transfer",
      make_rating("Struggle to Connect", "Seamlessly Connect Cross-Disciplinary Concepts"))
    q("LEARN_910_02", "When adopting a new technology or tool, how long does it take you to reach proficiency?", 10, "RATING", 9, 10, "Medium", "learning_ability", "All", True, 6, "Technology adoption velocity",
      make_rating("Weeks of Tutoring Needed", "Master Fundamentals within Hours"))
    q("LEARN_910_03", "Which learning style helps you retain complex technical concepts longest?", 10, "MCQ", 9, 10, "Medium", "learning_ability", "All", True, 7, "Metacognition",
      make_mcq([("Feynman Technique: Explaining the concept in simple terms to someone else / building a project", "A"), ("Rote cramming the night before", "B"), ("Passive highlighting of textbook pages", "C"), ("Re-reading without practice", "D")], 0))
    q("LEARN_910_04", "How do you maintain focus during long, intensive study or research sessions?", 10, "RATING", 9, 10, "Medium", "learning_ability", "All", True, 8, "Cognitive stamina",
      make_rating("Easily Distracted in 10 min", "Maintain Deep Flow State for Hours"))

    q("LEARN_1112_01", "In self-directed research, how do you navigate conflicting claims in scientific or economic literature?", 10, "MCQ", 11, 12, "Hard", "learning_ability", "All", True, 9, "Epistemic rigor",
      make_mcq([("Evaluate underlying methodologies, statistical power, funding conflicts, and replication studies", "A"), ("Accept the claim with the loudest headlines", "B"), ("Pick whichever claim confirms my prior bias", "C"), ("Ignore the research entirely", "D")], 0))
    q("LEARN_1112_02", "How rapidly can you unlearn outdated methods and embrace superior modern frameworks?", 10, "RATING", 11, 12, "Hard", "learning_ability", "All", True, 10, "Cognitive flexibility",
      make_rating("Rigidly Cling to Past Habits", "Unlearn & Adapt Rapidly"))
    q("LEARN_1112_03", "When studying for highly competitive national examinations, how do you analyze mock test mistakes?", 10, "MCQ", 11, 12, "Hard", "learning_ability", "All", True, 11, "Error analysis discipline",
      make_mcq([("Maintain an error log categorizing conceptual, calculation, and time-management flaws to systematically drill weaknesses", "A"), ("Look at the total score only and feel sad", "B"), ("Blame the test makers for tricky questions", "C"), ("Never review mock tests", "D")], 0))
    q("LEARN_1112_04", "How often do you take online courses (Coursera, edX, YouTube lectures, MIT OpenCourseWare) beyond school?", 10, "RATING", 11, 12, "Hard", "learning_ability", "All", True, 12, "Autonomous lifelong learning",
      make_rating("Never", "Regular Active Self-Study"))

    # ========================================================
    # SECTION 11: SPATIAL & MECHANICAL ABILITY (12 Questions)
    # ========================================================
    q("SPAT_78_01", "If you fold a flat 2D cardboard template with 6 square faces, what 3D shape does it form?", 11, "MCQ", 7, 8, "Easy", "spatial_ability", "All", True, 1, "Cube net",
      make_mcq([("Cube", "A"), ("Pyramid", "B"), ("Cylinder", "C"), ("Cone", "D")], 0))
    q("SPAT_78_02", "Gear A has 20 teeth and rotates clockwise. It meshes with Gear B which has 10 teeth. Gear B rotates:", 11, "MCQ", 7, 8, "Easy", "spatial_ability", "All", True, 2, "Gears rotation",
      make_mcq([("Counter-Clockwise at twice the speed", "A"), ("Clockwise at twice the speed", "B"), ("Counter-Clockwise at half speed", "C"), ("Does not rotate", "D")], 0))
    q("SPAT_78_03", "How easily can you assemble LEGO sets, IKEA furniture, or 3D puzzles without step-by-step guidance?", 11, "RATING", 7, 8, "Easy", "spatial_ability", "All", True, 3, "Mechanical assembly",
      make_rating("Struggle Significantly", "Assemble Intuitively & Rapidly"))
    q("SPAT_78_04", "When looking at a map, how easily can you navigate a new neighborhood without GPS?", 11, "RATING", 7, 8, "Easy", "spatial_ability", "All", True, 4, "Mental orientation",
      make_rating("Easily Lost", "Strong Mental Compass"))

    q("SPAT_910_01", "If a solid cylinder is sliced horizontally parallel to its base, what is the shape of the cross-section?", 11, "MCQ", 9, 10, "Medium", "spatial_ability", "All", True, 5, "Cross-sections",
      make_mcq([("Circle", "A"), ("Rectangle", "B"), ("Triangle", "C"), ("Ellipse", "D")], 0))
    q("SPAT_910_02", "In a hydraulic lift system, pressing a small piston with area 5 cm^2 lifts a car on a large piston with area 500 cm^2. The force is multiplied by:", 11, "MCQ", 9, 10, "Medium", "spatial_ability", "All", True, 6, "Pascal's principle hydraulics",
      make_mcq([("100 times (500/5)", "A"), ("10 times", "B"), ("50 times", "C"), ("5 times", "D")], 0))
    q("SPAT_910_03", "How easily can you mentally rotate a complex 3D object and visualize its rear view?", 11, "RATING", 9, 10, "Medium", "spatial_ability", "All", True, 7, "Mental rotation",
      make_rating("Cannot Visualize", "Crystal Clear 3D Mental Model"))
    q("SPAT_910_04", "When looking at 2D engineering blueprints or architectural floor plans, how well do you envision the built room?", 11, "RATING", 9, 10, "Medium", "spatial_ability", "All", True, 8, "Architectural projection",
      make_rating("See Only Flat Lines", "Instantly Visualize 3D Space & Scale"))

    q("SPAT_1112_01", "In isometric projection, what are the angles between the three coordinate axes?", 11, "MCQ", 11, 12, "Hard", "spatial_ability", "Science-PCM", True, 9, "Engineering drawing isometric",
      make_mcq([("120 degrees between all axes", "A"), ("90 degrees between all axes", "B"), ("45, 45, 90 degrees", "C"), ("60, 60, 60 degrees", "D")], 0))
    q("SPAT_1112_02", "In structural engineering, which truss geometry provides maximum rigidity against deformation under load?", 11, "MCQ", 11, 12, "Hard", "spatial_ability", "Science-PCM", True, 10, "Structural mechanics",
      make_mcq([("Triangular truss networks", "A"), ("Square grids", "B"), ("Pentagonal frames", "C"), ("Circular rings", "D")], 0))
    q("SPAT_1112_03", "How proficient are you in 3D CAD modeling software (SolidWorks, AutoCAD, Fusion 360, Rhino)?", 11, "RATING", 11, 12, "Hard", "spatial_ability", "All", True, 11, "CAD proficiency",
      make_rating("Never Used CAD", "Proficient in 3D Parametric CAD"))
    q("SPAT_1112_04", "If a right circular cone is intersected by a plane at an angle steeper than its slant edge, what conic section curve is generated?", 11, "MCQ", 11, 12, "Hard", "spatial_ability", "Science-PCM", True, 12, "Conic sections geometry",
      make_mcq([("Hyperbola", "A"), ("Parabola", "B"), ("Ellipse", "C"), ("Circle", "D")], 0))

    # ========================================================
    # SECTION 12: PRACTICAL & KINESTHETIC ABILITY (10 Questions)
    # ========================================================
    q("PRAC_78_01", "How much do you enjoy taking broken gadgets apart to see how they work inside?", 12, "RATING", 7, 8, "Easy", "practical_ability", "All", True, 1, "Tinkering inclination",
      make_rating("Not Interested", "Love Disassembling & Repairing"))
    q("PRAC_78_02", "When assembling a bicycle chain or fixing a loose toy screw, how steady are your hands?", 12, "RATING", 7, 8, "Easy", "practical_ability", "All", True, 2, "Manual dexterity",
      make_rating("Clumsy / Avoid Tools", "Very Steady & Precise with Tools"))
    q("PRAC_78_03", "Which activity would you rather spend a Saturday afternoon doing?", 12, "MCQ", 7, 8, "Easy", "practical_ability", "All", True, 3, "Practical vs theoretical preference",
      make_mcq([("Building a working model / gardening / baking", "A"), ("Writing a long theoretical essay", "B"), ("Memorizing historical dates", "C"), ("Doing nothing", "D")], 0))

    q("PRAC_910_01", "How comfortable are you handling science laboratory equipment (burettes, microscopes, Bunsen burners, soldering irons)?", 12, "RATING", 9, 10, "Medium", "practical_ability", "All", True, 4, "Lab dexterity",
      make_rating("Uncomfortable & Hesitant", "Extremely Skillful & Safe"))
    q("PRAC_910_02", "When a household electrical appliance fails, what is your approach?", 12, "MCQ", 9, 10, "Medium", "practical_ability", "All", True, 5, "Applied troubleshooting",
      make_mcq([("Safely isolate power, check fuses, test with multimeter, or consult schematic", "A"), ("Bang it on the table repeatedly", "B"), ("Throw it in the trash without checking", "C"), ("Leave it plugged in while smoking", "D")], 0))
    q("PRAC_910_03", "How frequently do you participate in hands-on STEM maker clubs, robotics workshops, or craft studios?", 12, "RATING", 9, 10, "Medium", "practical_ability", "All", True, 6, "Maker participation",
      make_rating("Never", "Weekly Active Participant"))

    q("PRAC_1112_01", "In electrical prototyping, what instrument measures voltage, current, and resistance across components?", 12, "MCQ", 11, 12, "Hard", "practical_ability", "Science-PCM", True, 7, "Electronic instrumentation",
      make_mcq([("Digital Multimeter", "A"), ("Thermometer", "B"), ("Barometer", "C"), ("Spectrophotometer", "D")], 0))
    q("PRAC_1112_02", "How proficient are you in soldering electronic circuit boards or breadboard circuit wiring?", 12, "RATING", 11, 12, "Hard", "practical_ability", "Science-PCM", True, 8, "Circuit assembly",
      make_rating("Never Soldered", "Flawless Soldering & Circuit Assembly"))
    q("PRAC_1112_03", "When executing a complex chemical titration, what visual indicator signals the exact endpoint?", 12, "MCQ", 11, 12, "Hard", "practical_ability", "Science-PCB", True, 9, "Analytical chemistry lab",
      make_mcq([("A sharp, persistent color change of the indicator solution", "A"), ("Liquid starts boiling furiously", "B"), ("The burette glass turns opaque", "C"), ("Smell of smoke", "D")], 0))
    q("PRAC_1112_04", "How confident are you in managing fieldwork logistics, physical surveying, or environmental sample collection in the field?", 12, "RATING", 11, 12, "Hard", "practical_ability", "All", True, 10, "Fieldwork stamina",
      make_rating("Prefer 100% Desk Work", "Thrive in Rigorous Fieldwork & Lab Settings"))

    # ========================================================
    # SECTION 13: DISCIPLINARY INTERESTS (40 Questions)
    # ========================================================
    clusters = [
        ("TECH", "Technology, Software & AI Engineering", "technology_interest"),
        ("ENG", "Core Engineering, Robotics & Aerospace", "engineering_interest"),
        ("MED", "Medicine, Healthcare, Surgery & Pharmacy", "medical_interest"),
        ("SCI", "Pure & Applied Sciences, Research & Space", "scientific_interest"),
        ("BUS", "Business, Finance, Banking & Investment", "business_interest"),
        ("DES", "Design, Architecture, Fashion & Fine Arts", "creative_interest"),
        ("MEDIA", "Media, Journalism, Film & Content Creation", "creative_interest"),
        ("LAW", "Law, Civil Services, Policy & Governance", "governance_interest"),
        ("EDU", "Education, Psychology, Counselling & Social Work", "social_interest"),
        ("HOSP", "Hospitality, Aviation, Culinary & Sports Management", "practical_ability")
    ]

    order_counter = 1
    for prefix, domain_name, skill_cat in clusters:
        q(f"INT_{prefix}_78", f"How interested are you in exploring topics related to {domain_name}?", 13, "RATING", 7, 8, "Easy", skill_cat, "All", True, order_counter, f"Junior interest in {domain_name}",
          make_rating("Not Interested at all", "Extremely Excited to Learn"))
        order_counter += 1

        q(f"INT_{prefix}_910_A", f"How much do you enjoy hands-on projects, simulations, or case studies in {domain_name}?", 13, "RATING", 9, 10, "Medium", skill_cat, "All", True, order_counter, f"Secondary engagement with {domain_name}",
          make_rating("Zero Interest", "High Project Engagement"))
        order_counter += 1

        q(f"INT_{prefix}_1112_A", f"How strongly do you consider building a long-term professional career in {domain_name}?", 13, "RATING", 11, 12, "Hard", skill_cat, "All", True, order_counter, f"Career conviction in {domain_name}",
          make_rating("Would Never Choose", "Primary Dream Career Path"))
        order_counter += 1

        q(f"INT_{prefix}_1112_B", f"How closely do you follow emerging industry trends, research breakthroughs, and startups in {domain_name}?", 13, "RATING", 11, 12, "Hard", skill_cat, "All", True, order_counter, f"Industry awareness in {domain_name}",
          make_rating("Never Follow", "Obsessively Follow Industry Leaders"))
        order_counter += 1

    # ========================================================
    # SECTION 14: CO-CURRICULAR & EXTRACURRICULAR ACTIVITIES (20 Questions)
    # ========================================================
    activities = [
        ("ACT_CODING", "Participating in coding competitions, hackathons, or robotics challenges", "technology_interest"),
        ("ACT_SCIENCE_FAIR", "Designing working science models or entering Olympiads (Math/Science)", "scientific_interest"),
        ("ACT_DEBATE", "Participating in Model United Nations (MUN), public speaking, or school debates", "governance_interest"),
        ("ACT_CREATIVE_WRITING", "Writing poetry, school magazine articles, blog posts, or stories", "creative_interest"),
        ("ACT_FINE_ARTS", "Painting, sketching, digital illustration, or graphic poster design", "creative_interest"),
        ("ACT_MUSIC_THEATRE", "Playing musical instruments, choir singing, or acting in school plays", "creative_interest"),
        ("ACT_SPORTS_ATHLETICS", "Competing in competitive team sports (football, basketball, cricket, athletics)", "practical_ability"),
        ("ACT_COMMUNITY_SERVICE", "Volunteering for NGOs, teaching underprivileged kids, or environmental cleanups", "social_interest"),
        ("ACT_BUSINESS_FEST", "Participating in student enterprise fairs, stock market simulations, or commerce fests", "business_interest"),
        ("ACT_PHOTOGRAPHY_FILM", "Filming video vlogs, editing YouTube videos, or event photography", "creative_interest"),
        ("ACT_STUDENT_COUNCIL", "Running for student council, prefect roles, or organizing school ceremonies", "leadership"),
        ("ACT_TINKERING_ELECTRONICS", "Building DIY Arduino / Raspberry Pi circuits, drones, or 3D prints", "engineering_interest"),
        ("ACT_HEALTH_CAMPAIGN", "Organizing blood donation drives, first-aid workshops, or mental health awareness", "medical_interest"),
        ("ACT_QUIZ_COMPETITION", "Competing in general knowledge, trivia, or business quiz competitions", "learning_ability"),
        ("ACT_BOOK_CLUB", "Participating in literary book clubs, philosophy discussions, or history seminars", "social_interest"),
        ("ACT_ENVIRONMENT_CLUB", "Tree plantation drives, climate action advocacy, or bird-watching expeditions", "scientific_interest"),
        ("ACT_INVESTMENT_CLUB", "Tracking cryptocurrency, stocks, venture capital, and startup funding news", "business_interest"),
        ("ACT_LEGAL_MOOT", "Participating in mock trials, youth parliament, or legal debate forums", "governance_interest"),
        ("ACT_CHESS_PUZZLES", "Playing competitive chess, solving Sudoku tournaments, or escape room puzzles", "logical_reasoning"),
        ("ACT_TEACHING_PEERS", "Conducting free tutoring sessions for classmates who struggle with difficult subjects", "social_interest")
    ]

    for i, (code, act_name, skill_cat) in enumerate(activities, 1):
        q_min = 7 if i <= 8 else (9 if i <= 15 else 11)
        q_max = 12
        diff = "Easy" if i <= 8 else ("Medium" if i <= 15 else "Hard")
        q(code, f"How frequently do you engage in: {act_name}?", 14, "RATING", q_min, q_max, diff, skill_cat, "All", True, i, f"Participation in {act_name}",
          make_freq())

    # ========================================================
    # SECTION 15: TEAMWORK & COLLABORATION (8 Questions)
    # ========================================================
    q("TEAM_78_01", "When working on a group assignment in school, how well do you cooperate with teammates?", 15, "RATING", 7, 8, "Easy", "teamwork", "All", True, 1, "Team cooperation",
      make_rating("Prefer Working Alone", "Love Collaborating with Teammates"))
    q("TEAM_78_02", "If a teammate struggles to finish their part, what do you do?", 15, "MCQ", 7, 8, "Easy", "teamwork", "All", True, 2, "Team empathy",
      make_mcq([("Offer encouragement and help them understand their section", "A"), ("Complain to the teacher to get them kicked out", "B"), ("Ignore them completely", "C"), ("Do nothing and let the project fail", "D")], 0))
    q("TEAM_910_01", "How effectively do you handle disagreements on creative direction within a project team?", 15, "RATING", 9, 10, "Medium", "teamwork", "All", True, 3, "Constructive conflict",
      make_rating("Argue Stubbornly", "Find Synergy & Common Ground"))
    q("TEAM_910_02", "In a cross-functional team, what is your attitude toward diverse opinions and perspectives?", 15, "RATING", 9, 10, "Medium", "teamwork", "All", True, 4, "Diversity inclusion",
      make_rating("Dislike Different Views", "Deeply Value Diverse Perspectives"))
    q("TEAM_1112_01", "How do you ensure accountability when delegating tasks in large student committees?", 15, "MCQ", 11, 12, "Hard", "teamwork", "All", True, 5, "Team accountability",
      make_mcq([("Set transparent deliverables, milestone checkpoints, and supportive check-ins", "A"), ("Micromanage every single second aggressively", "B"), ("Assign tasks without deadlines and hope for the best", "C"), ("Do everything myself", "D")], 0))
    q("TEAM_1112_02", "How comfortable are you working in asynchronous remote global teams (Slack, Discord, Zoom)?", 15, "RATING", 11, 12, "Hard", "teamwork", "All", True, 6, "Remote collaboration",
      make_rating("Struggle with Remote Work", "Highly Productive in Remote Teams"))
    q("TEAM_1112_03", "When receiving credit for a successful project, how do you acknowledge team contributions?", 15, "MCQ", 11, 12, "Hard", "teamwork", "All", True, 7, "Humility & credit sharing",
      make_mcq([("Publicly highlight and celebrate every team member's specific contributions", "A"), ("Take 100% of the credit silently", "B"), ("Forget who helped", "C"), ("Downplay the success", "D")], 0))
    q("TEAM_1112_04", "How effectively do you foster psychological safety so timid team members voice bold ideas?", 15, "RATING", 11, 12, "Hard", "teamwork", "All", True, 8, "Psychological safety",
      make_rating("Never Think About It", "Create Empowering, Safe Environment"))

    # ========================================================
    # SECTION 16: LEADERSHIP & INITIATIVE (8 Questions)
    # ========================================================
    q("LEAD_78_01", "When a group has no clear direction, how often do you step forward to organize the plan?", 16, "RATING", 7, 8, "Easy", "leadership", "All", True, 1, "Natural initiative",
      make_rating("Wait for Others", "Step Forward Naturally"))
    q("LEAD_78_02", "What is the most important quality of a great school team captain?", 16, "MCQ", 7, 8, "Easy", "leadership", "All", True, 2, "Leadership philosophy",
      make_mcq([("Listening to everyone and inspiring the team to do their best", "A"), ("Bossing people around loudly", "B"), ("Scoring all points alone", "C"), ("Punishing mistakes harshly", "D")], 0))
    q("LEAD_910_01", "How comfortable are you making decisions that may be unpopular initially but right for the team?", 16, "RATING", 9, 10, "Medium", "leadership", "All", True, 3, "Courage in leadership",
      make_rating("Avoid Conflict at All Costs", "Stand Resolute for Principle"))
    q("LEAD_910_02", "When launching a new school club or initiative, what is your primary motivator?", 16, "MCQ", 9, 10, "Medium", "leadership", "All", True, 4, "Visionary drive",
      make_mcq([("Solving a real student need and creating lasting positive impact", "A"), ("Looking important on college resume only", "B"), ("Having a shiny title", "C"), ("Skipping class", "D")], 0))
    q("LEAD_1112_01", "Which leadership style aligns closest with your natural approach when directing complex operations?", 16, "MCQ", 11, 12, "Hard", "leadership", "All", True, 5, "Executive leadership styles",
      make_mcq([("Servant Leadership: Empowering leaders and removing roadblocks for the team", "A"), ("Authoritarian: Top-down command and control", "B"), ("Laissez-faire: Complete detachment and zero guidance", "C"), ("Transactional: Strict reward and punishment only", "D")], 0))
    q("LEAD_1112_02", "How effectively do you rally demoralized teammates after a major defeat or project failure?", 16, "RATING", 11, 12, "Hard", "leadership", "All", True, 6, "Crisis leadership resilience",
      make_rating("Feel Defeated Together", "Inspire Hope, Re-align Vision & Lead Comeback"))
    q("LEAD_1112_03", "When mentoring younger junior students, what is your greatest satisfaction?", 16, "RATING", 11, 12, "Hard", "leadership", "All", True, 7, "Mentorship satisfaction",
      make_rating("Not Interested in Mentoring", "Watching Mentees Surpass My Own Achievements"))
    q("LEAD_1112_04", "How proficient are you in strategic long-term roadmap planning (1 to 5 year horizon)?", 16, "RATING", 11, 12, "Hard", "leadership", "All", True, 8, "Strategic vision",
      make_rating("Live Day to Day", "Architect Structured Multi-Year Strategic Roadmaps"))

    # ========================================================
    # SECTION 17: WORK ENVIRONMENT & LIFESTYLE (10 Questions)
    # ========================================================
    q("WORK_78_01", "Which work setting sounds most exciting for your future daily life?", 17, "MCQ", 7, 8, "Easy", "work_preference", "All", True, 1, "Environment preference",
      make_mcq([("Modern high-tech software office or digital lab", "A"), ("Hospital, surgical clinic, or healthcare center", "B"), ("Outdoor field, architectural site, or aerospace hangar", "C"), ("Creative studio, film set, or design atelier", "D")], 0))
    q("WORK_78_02", "How do you feel about working with computers for most of your workday?", 17, "RATING", 7, 8, "Easy", "work_preference", "All", True, 2, "Screen time tolerance",
      make_rating("Dislike Screen Time", "Love Digital Workstations"))
    q("WORK_78_03", "Would you prefer a predictable routine or a job where every single day brings new surprises?", 17, "RATING", 7, 8, "Easy", "work_preference", "All", True, 3, "Routine vs novelty",
      make_rating("Strict Predictable Routine", "Dynamic, Ever-Changing Environment"))

    q("WORK_910_01", "Which work culture appeals to you the most?", 17, "MCQ", 9, 10, "Medium", "work_preference", "All", True, 4, "Corporate culture",
      make_mcq([("Fast-paced entrepreneurial startup with high innovation and equity", "A"), ("Prestigious global corporation with structured corporate hierarchy", "B"), ("Public service / governmental agency dedicated to societal welfare", "C"), ("Academic university / research institute with intellectual autonomy", "D")], 0))
    q("WORK_910_02", "How important is geographical flexibility (working from anywhere in the world / remote) to you?", 17, "RATING", 9, 10, "Medium", "work_preference", "All", True, 5, "Remote flexibility",
      make_rating("Must be in Local Office", "Essential Requirement"))
    q("WORK_910_03", "How do you handle high-pressure deadlines in competitive environments?", 17, "RATING", 9, 10, "Medium", "work_preference", "All", True, 6, "Pressure tolerance",
      make_rating("Severe Stress & Burnout", "Thrive on High-Stakes Adrenaline"))

    q("WORK_1112_01", "When weighing compensation versus social purpose, what is your primary career equation?", 17, "MCQ", 11, 12, "Hard", "work_preference", "All", True, 7, "Value orientation",
      make_mcq([("High financial upside and wealth accumulation", "A"), ("Maximum societal impact and public service mission", "B"), ("Deep intellectual mastery and scientific discovery", "C"), ("Work-life harmony, creative freedom, and mental wellness", "D")], 0))
    q("WORK_1112_02", "How comfortable are you with frequent international travel (30%+ travel time)?", 17, "RATING", 11, 12, "Hard", "work_preference", "All", True, 8, "Travel willingness",
      make_rating("Prefer Zero Travel", "Enthusiastic Global Traveler"))
    q("WORK_1112_03", "Would you rather be an individual specialist contributor or an executive manager leading 100+ people?", 17, "RATING", 11, 12, "Hard", "work_preference", "All", True, 9, "Track preference",
      make_rating("Deep Technical Specialist", "Executive Enterprise Leader"))
    q("WORK_1112_04", "How much risk are you willing to take (e.g., founding a venture with 0 salary for 2 years)?", 17, "RATING", 11, 12, "Hard", "work_preference", "All", True, 10, "Risk appetite",
      make_rating("Zero Risk / Guaranteed Salary", "High Risk / High Reward Entrepreneur"))

    # ========================================================
    # SECTION 18: CAREER AWARENESS (10 Questions)
    # ========================================================
    q("AWARE_78_01", "What does a Software Architect do on a day-to-day basis?", 18, "MCQ", 7, 8, "Easy", "career_awareness", "All", True, 1, "Role awareness tech",
      make_mcq([("Designs high-level structure and technical blueprints of software systems", "A"), ("Builds brick walls for computer buildings", "B"), ("Sells laptop bags in shopping malls", "C"), ("Fixes broken smartphone screens", "D")], 0))
    q("AWARE_78_02", "Which career focuses on investigating crime scenes and analyzing forensic evidence in labs?", 18, "MCQ", 7, 8, "Easy", "career_awareness", "All", True, 2, "Role awareness forensics",
      make_mcq([("Forensic Scientist / Criminologist", "A"), ("Civil Engineer", "B"), ("Chartered Accountant", "C"), ("Commercial Pilot", "D")], 0))
    q("AWARE_78_03", "How well do you understand the educational degrees required for your top 3 dream careers?", 18, "RATING", 7, 8, "Easy", "career_awareness", "All", True, 3, "Education awareness",
      make_rating("No Idea", "Know Exact Degrees & Entrance Exams"))

    q("AWARE_910_01", "What is the primary role of a Chartered Financial Analyst (CFA) or Investment Banker?", 18, "MCQ", 9, 10, "Medium", "career_awareness", "All", True, 4, "Role awareness finance",
      make_mcq([("Managing corporate mergers, stock market portfolios, capital raising, and valuations", "A"), ("Filing personal income tax returns only", "B"), ("Printing physical bank currency notes", "C"), ("Selling insurance door-to-door", "D")], 0))
    q("AWARE_910_02", "What is the educational roadmap to become a licensed Medical Doctor (MBBS / Specialist) in India?", 18, "MCQ", 9, 10, "Medium", "career_awareness", "All", True, 5, "Medical pathway",
      make_mcq([("Class 12 PCB -> NEET-UG -> 5.5 yr MBBS -> NEET-PG / INI-CET -> MD/MS Specialization", "A"), ("Class 12 Commerce -> 3 yr B.Com -> Hospital Manager", "B"), ("Class 10 -> 1 yr diploma -> Surgeon", "C"), ("Direct college admission without entrance exam", "D")], 0))
    q("AWARE_910_03", "How frequently do you research career profiles, salary ranges, and job markets online?", 18, "RATING", 9, 10, "Medium", "career_awareness", "All", True, 6, "Labor market research",
      make_rating("Never Researched", "Regularly Study Job Trends"))

    q("AWARE_1112_01", "In tech startups, what does the role of a 'Product Manager (PM)' entail?", 18, "MCQ", 11, 12, "Hard", "career_awareness", "All", True, 7, "Role awareness PM",
      make_mcq([("Intersecting Business, Technology, and UX to define product vision, roadmap, and user metrics", "A"), ("Writing 100% of the backend SQL code", "B"), ("Managing office supplies and furniture", "C"), ("Sales cold-calling", "D")], 0))
    q("AWARE_1112_02", "What is the primary difference between Corporate Law and Litigation Law?", 18, "MCQ", 11, 12, "Hard", "career_awareness", "All", True, 8, "Role awareness legal",
      make_mcq([("Corporate Law focuses on contracts, M&A, and regulatory compliance; Litigation represents clients in courtrooms", "A"), ("Corporate Law only handles traffic tickets", "B"), ("Litigation lawyers work exclusively in banks", "C"), ("They are identical fields", "D")], 0))
    q("AWARE_1112_03", "How clearly have you mapped your backup contingency career options (Plan B & Plan C)?", 18, "RATING", 11, 12, "Hard", "career_awareness", "All", True, 9, "Contingency planning",
      make_rating("Only Have Plan A", "Structured Tiered Career Contingencies Mapped"))
    q("AWARE_1112_04", "What is the role of an Actuary in insurance and risk management?", 18, "MCQ", 11, 12, "Hard", "career_awareness", "Commerce", True, 10, "Actuarial science",
      make_mcq([("Using advanced mathematical modeling, probability, and statistics to price financial risk", "A"), ("Selling retail motor vehicle insurance", "B"), ("Auditing office petty cash receipts", "C"), ("Designing car body panels", "D")], 0))

    # ========================================================
    # SECTION 19: CAREER PREFERENCES & ASPIRATIONS (10 Questions)
    # ========================================================
    q("PREF_78_01", "If you could shadow any professional for an entire week, which would you pick?", 19, "MCQ", 7, 8, "Easy", "career_preference", "All", True, 1, "Exploratory shadow",
      make_mcq([("An AI Robotics Engineer or Video Game Director", "A"), ("A Wildlife Biologist, Surgeon, or Astrobiologist", "B"), ("An Entrepreneur, Stock Trader, or Film Director", "C"), ("A Supreme Court Lawyer, Diplomat, or Author", "D")], 0))
    q("PREF_78_02", "How excited are you to discover which modern careers match your unique strengths?", 19, "RATING", 7, 8, "Easy", "career_preference", "All", True, 2, "Career excitement",
      make_rating("Indifferent", "Incredibly Excited & Ready"))
    q("PREF_78_03", "What is your main reason for wanting to choose the right career early?", 19, "MCQ", 7, 8, "Easy", "career_preference", "All", True, 3, "Career motivation",
      make_mcq([("To develop relevant skills early, avoid regret, and pursue my true passions", "A"), ("Because parents told me to pick a job", "B"), ("To stop going to school", "C"), ("No specific reason", "D")], 0))

    q("PREF_910_01", "Which of these future industry sectors excites you the most over the next 10 years?", 19, "MCQ", 9, 10, "Medium", "career_preference", "All", True, 4, "Emerging industries",
      make_mcq([("Generative AI, Quantum Computing, Cyber Defense, and Autonomous Systems", "A"), ("Biotechnology, Personalized Genomics, and Neuro-Engineering", "B"), ("Renewable Clean Energy, EV Mobility, and Sustainable Cities", "C"), ("FinTech, Global Venture Capital, and Creative Media Production", "D")], 0))
    q("PREF_910_02", "How aligned do you feel your current subject choices are with your dream profession?", 19, "RATING", 9, 10, "Medium", "career_preference", "All", True, 5, "Curriculum alignment",
      make_rating("Completely Misaligned", "100% Perfectly Aligned"))
    q("PREF_910_03", "What is your stance on pursuing non-traditional / emerging modern careers (e.g., Cloud Architect, UX Researcher, Data Ethicist)?", 19, "RATING", 9, 10, "Medium", "career_preference", "All", True, 6, "New-age career openness",
      make_rating("Only Want Traditional Jobs", "Highly Eager to Pursue Modern Cutting-Edge Fields"))

    q("PREF_1112_01", "Where do you envision yourself 10 years after completing your undergraduate education?", 19, "MCQ", 11, 12, "Hard", "career_preference", "All", True, 7, "Long term vision",
      make_mcq([("Leading innovative technology / scientific breakthroughs as Chief Architect / Principal Scientist", "A"), ("Senior Partner, Managing Director, or Venture Capitalist in global finance", "B"), ("Practicing Specialist Doctor / Chief Medical Officer saving lives", "C"), ("Founder / CEO of a high-growth global startup enterprise", "D")], 0))
    q("PREF_1112_02", "How confident are you in taking personal ownership of your career trajectory regardless of peer pressure?", 19, "RATING", 11, 12, "Hard", "career_preference", "All", True, 8, "Autonomy & self-authorship",
      make_rating("Bow to Peer Pressure", "100% Autonomous & Determined Self-Author"))
    q("PREF_1112_03", "Which legacy would you most like your professional career to leave behind?", 19, "MCQ", 11, 12, "Hard", "career_preference", "All", True, 9, "Career legacy",
      make_mcq([("Pioneering technological or scientific inventions that advance humanity", "A"), ("Empowering millions through social justice, education, or public policy", "B"), ("Building iconic companies, creating jobs, and driving economic prosperity", "C"), ("Creating timeless works of art, culture, architecture, or literature", "D")], 0))
    q("PREF_1112_04", "How eager are you to review the personalized AI career compatibility matches and skill roadmaps generated from this assessment?", 19, "RATING", 11, 12, "Hard", "career_preference", "All", True, 10, "Recommendation receptivity",
      make_rating("Skeptical", "Ready to Execute Recommended Roadmap"))

    # Integrate expanded stratified question bank
    try:
        from database.expanded_questions_data import get_expanded_questions
        expanded = get_expanded_questions()
        questions.extend(expanded)
    except Exception as e:
        print(f"Note: Expanded questions import skipped: {e}")

    return questions
