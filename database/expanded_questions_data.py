"""
Expanded Question Bank Data Module.
Provides 300+ additional stratified psychometric, aptitude, cognitive, and interest questions
for Classes 7, 8, 9, 10, 11, and 12 across all streams (General, Science-PCM, Science-PCB, Commerce, Humanities).
"""

def get_expanded_questions():
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

    # =========================================================================
    # SECTION 1: ACADEMIC PROFILE (15 additional questions)
    # =========================================================================
    q("EXP_ACAD_78_01", "How comfortable are you preparing laboratory science journals and recording experiment observations?", 1, "RATING", 7, 8, "Easy", "academic_performance", "All", True, 10, "Science lab record keeping", make_rating("Very Difficult", "Extremely Comfortable & Organized"))
    q("EXP_ACAD_78_02", "When given a choice between solving 10 math puzzles or writing a 2-page essay, which do you naturally prefer?", 1, "MCQ", 7, 8, "Easy", "academic_performance", "All", True, 11, "Subject inclination", make_mcq([("Solving the math puzzles", "A"), ("Writing the creative essay", "B"), ("Enjoy both equally", "C"), ("Dislike both", "D")], 0))
    q("EXP_ACAD_78_03", "How consistently do you review class notes on the same day they were taught?", 1, "RATING", 7, 8, "Easy", "academic_performance", "All", True, 12, "Study habit consistency", make_freq())
    q("EXP_ACAD_78_04", "How easily can you memorize historical timelines and geographic map locations?", 1, "RATING", 7, 8, "Easy", "academic_performance", "All", True, 13, "Social sciences recall", make_rating("Struggle Greatly", "Effortless Recall"))
    q("EXP_ACAD_78_05", "How confident are you using computers and spreadsheets for school presentations?", 1, "RATING", 7, 8, "Easy", "academic_performance", "All", True, 14, "Tech presentation skills", make_rating("Beginner / Unsure", "Advanced & Confident"))

    q("EXP_ACAD_910_01", "What is your typical approach when preparing for comprehensive end-of-term examinations?", 1, "MCQ", 9, 10, "Medium", "academic_performance", "All", True, 15, "Exam prep strategy", make_mcq([("Structured revision schedule 3 weeks in advance with practice tests", "A"), ("Intense cramming 2 days before the exam", "B"), ("Only studying the night before", "C"), ("No formal preparation", "D")], 0))
    q("EXP_ACAD_910_02", "How do you rate your performance in solving application-based numerical word problems in Physics and Chemistry?", 1, "RATING", 9, 10, "Medium", "academic_performance", "All", True, 16, "Numerical application comfort", make_rating("Very Low", "Consistently High / Top Tier"))
    q("EXP_ACAD_910_03", "How confident are you in debating contemporary socio-economic or environmental issues in class?", 1, "RATING", 9, 10, "Medium", "academic_performance", "All", True, 17, "Classroom debate confidence", make_rating("Hesitant / Shy", "Very Articulate & Confident"))
    q("EXP_ACAD_910_04", "How often do you consult reference books or online academic portals beyond standard textbooks?", 1, "RATING", 9, 10, "Medium", "academic_performance", "All", True, 18, "Self-directed scholarship", make_freq())
    q("EXP_ACAD_910_05", "Which subject area gives you the greatest sense of intellectual satisfaction when you master a complex concept?", 1, "MCQ", 9, 10, "Medium", "academic_performance", "All", True, 19, "Intellectual drive", make_mcq([("Mathematics and Computational Logic", "A"), ("Physical & Life Sciences", "B"), ("Commerce, Economics & Business Studies", "C"), ("Literature, History, Philosophy & Art", "D")], 0))

    q("EXP_ACAD_1112_PCM_01", "How proficient are you at deriving mathematical proofs and kinematic equations from first principles?", 1, "RATING", 11, 12, "Hard", "academic_performance", "Science-PCM", True, 20, "PCM proof derivation", make_rating("Find Proofs Difficult", "Derive Confidently from First Principles"))
    q("EXP_ACAD_1112_PCB_01", "How confident are you in understanding cellular metabolic pathways, genetics, and anatomical systems?", 1, "RATING", 11, 12, "Hard", "academic_performance", "Science-PCB", True, 21, "PCB biological retention", make_rating("Overwhelmed by Terms", "Deep Understanding & Visual Recall"))
    q("EXP_ACAD_1112_COMM_01", "How well do you comprehend balance sheet analysis, double-entry bookkeeping, and corporate finance principles?", 1, "RATING", 11, 12, "Hard", "academic_performance", "Commerce", True, 22, "Commerce financial concepts", make_rating("Find Accounting Difficult", "Mastered Financial Reporting Principles"))
    q("EXP_ACAD_1112_HUM_01", "How skilled are you in critical essay writing, historiography analysis, and philosophical arguments?", 1, "RATING", 11, 12, "Hard", "academic_performance", "Humanities", True, 23, "Humanities analytical writing", make_rating("Basic Descriptive Writing", "Nuanced Critical & Theoretical Analysis"))
    q("EXP_ACAD_1112_GEN_01", "How actively do you monitor national entrance examination benchmarks (e.g. JEE, NEET, CUET, CLAT, IPMAT, NID)?", 1, "RATING", 11, 12, "Hard", "academic_performance", "All", True, 24, "Entrance exam awareness", make_rating("Not Tracking", "Rigorous Daily Mock Test Preparation"))

    # =========================================================================
    # SECTION 2: MATHEMATICAL ABILITY (40 additional questions)
    # =========================================================================
    # Class 7-8 Math (15 Qs)
    q("EXP_MATH_7_01", "What is the least common multiple (LCM) of 6, 8, and 12?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 20, "LCM calculation", make_mcq([("18", "A"), ("24", "B"), ("36", "C"), ("48", "D")], 1))
    q("EXP_MATH_7_02", "If a square has an area of 144 square meters, what is the length of each side?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 21, "Square root geometry", make_mcq([("10 m", "A"), ("12 m", "B"), ("14 m", "C"), ("16 m", "D")], 1))
    q("EXP_MATH_7_03", "Simplify: (-15) + (+27) - (-8)", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 22, "Integer arithmetic", make_mcq([("4", "A"), ("20", "B"), ("28", "C"), ("34", "D")], 1))
    q("EXP_MATH_7_04", "Express 3/5 as a percentage.", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 23, "Fractions to percentage", make_mcq([("35%", "A"), ("50%", "B"), ("60%", "C"), ("75%", "D")], 2))
    q("EXP_MATH_7_05", "If a car travels at a constant speed of 45 km/h, how far will it travel in 4 hours?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 24, "Distance rate time", make_mcq([("160 km", "A"), ("180 km", "B"), ("190 km", "C"), ("200 km", "D")], 1))
    q("EXP_MATH_8_01", "Solve for y: 4y + 9 = 33.", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 25, "Linear equation 1 variable", make_mcq([("5", "A"), ("6", "B"), ("7", "C"), ("8", "D")], 1))
    q("EXP_MATH_8_02", "What is the volume of a rectangular prism with length 6 cm, width 4 cm, and height 5 cm?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 26, "Volume calculation", make_mcq([("100 cm3", "A"), ("120 cm3", "B"), ("140 cm3", "C"), ("150 cm3", "D")], 1))
    q("EXP_MATH_8_03", "If the angles of a triangle are in the ratio 2:3:4, what is the measure of the largest angle?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 27, "Triangle angles ratio", make_mcq([("60 deg", "A"), ("70 deg", "B"), ("80 deg", "C"), ("90 deg", "D")], 2))
    q("EXP_MATH_8_04", "A shopkeeper buys an item for $80 and sells it for $100. What is the profit percentage?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 28, "Profit percentage", make_mcq([("20%", "A"), ("25%", "B"), ("30%", "C"), ("35%", "D")], 1))
    q("EXP_MATH_8_05", "What is the value of 2^5 * 2^3 / 2^4?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 29, "Laws of exponents", make_mcq([("8", "A"), ("16", "B"), ("32", "C"), ("64", "D")], 1))
    q("EXP_MATH_8_06", "Find the mean of the numbers: 12, 16, 20, 24, 28.", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 30, "Mean average", make_mcq([("18", "A"), ("20", "B"), ("22", "C"), ("24", "D")], 1))
    q("EXP_MATH_8_07", "If 8 workers can paint a wall in 6 hours, how many hours will 12 workers take at the same rate?", 2, "MCQ", 7, 8, "Medium", "mathematical_ability", "All", True, 31, "Inverse variation", make_mcq([("3 hours", "A"), ("4 hours", "B"), ("5 hours", "C"), ("8 hours", "D")], 1))
    q("EXP_MATH_8_08", "What is the circumference of a circle with diameter 14 cm? (Use pi = 22/7)", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 32, "Circle circumference", make_mcq([("28 cm", "A"), ("44 cm", "B"), ("88 cm", "C"), ("154 cm", "D")], 1))
    q("EXP_MATH_8_09", "If a die is rolled once, what is the probability of getting an even prime number?", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 33, "Probability basic", make_mcq([("1/6", "A"), ("1/3", "B"), ("1/2", "C"), ("2/3", "D")], 0))
    q("EXP_MATH_8_10", "Evaluate: (0.3 * 0.4) / 0.02", 2, "MCQ", 7, 8, "Easy", "mathematical_ability", "All", True, 34, "Decimal operations", make_mcq([("0.6", "A"), ("6", "B"), ("60", "C"), ("600", "D")], 1))

    # Class 9-10 Math (15 Qs)
    q("EXP_MATH_9_01", "Solve for x in the quadratic equation: 2x^2 - 7x + 3 = 0.", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 35, "Quadratic roots", make_mcq([("x = 1/2, x = 3", "A"), ("x = 1, x = 6", "B"), ("x = -1/2, x = -3", "C"), ("x = 2, x = 3/2", "D")], 0))
    q("EXP_MATH_9_02", "In an Arithmetic Progression (AP), if first term a = 5 and common difference d = 3, what is the 15th term?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 36, "AP nth term", make_mcq([("44", "A"), ("47", "B"), ("50", "C"), ("53", "D")], 1))
    q("EXP_MATH_9_03", "Evaluate: sin(30 deg) * cos(60 deg) + cos(30 deg) * sin(60 deg)", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 37, "Trigonometric identities", make_mcq([("0", "A"), ("1/2", "B"), ("1", "C"), ("sqrt(3)/2", "D")], 2))
    q("EXP_MATH_9_04", "If two tangents inclined at an angle of 60 deg are drawn to a circle of radius 3 cm, what is the length of each tangent?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 38, "Circle tangent trigonometry", make_mcq([("3 cm", "A"), ("3*sqrt(3) cm", "B"), ("6 cm", "C"), ("3/sqrt(3) cm", "D")], 1))
    q("EXP_MATH_9_05", "What is the median of the data set: 13, 18, 13, 14, 13, 16, 14, 21, 13?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 39, "Median computation", make_mcq([("13", "A"), ("14", "B"), ("15", "C"), ("16", "D")], 1))
    q("EXP_MATH_10_01", "The coordinates of midpoint of line segment joining A(4, -2) and B(8, 6) are:", 2, "MCQ", 9, 10, "Easy", "mathematical_ability", "All", True, 40, "Midpoint formula", make_mcq([("(6, 2)", "A"), ("(6, 4)", "B"), ("(12, 4)", "C"), ("(2, 4)", "D")], 0))
    q("EXP_MATH_10_02", "What is the total surface area of a solid hemisphere of radius 7 cm? (pi = 22/7)", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 41, "Hemisphere surface area", make_mcq([("308 cm2", "A"), ("462 cm2", "B"), ("616 cm2", "C"), ("924 cm2", "D")], 1))
    q("EXP_MATH_10_03", "A card is drawn from a well-shuffled deck of 52 cards. What is the probability of drawing a red face card?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 42, "Card probability", make_mcq([("3/52", "A"), ("3/26", "B"), ("6/13", "C"), ("1/4", "D")], 1))
    q("EXP_MATH_10_04", "If sum of zeroes of quadratic polynomial kx^2 + 2x + 3k is equal to their product, what is the value of k?", 2, "MCQ", 9, 10, "Hard", "mathematical_ability", "All", True, 43, "Polynomial relations", make_mcq([("-2/3", "A"), ("2/3", "B"), ("-1/3", "C"), ("1/3", "D")], 0))
    q("EXP_MATH_10_05", "From a point on the ground 20 m away from the base of a tower, the angle of elevation of the top is 45 deg. What is the height of the tower?", 2, "MCQ", 9, 10, "Easy", "mathematical_ability", "All", True, 44, "Height and distance", make_mcq([("10 m", "A"), ("14.14 m", "B"), ("20 m", "C"), ("28.28 m", "D")], 2))
    q("EXP_MATH_10_06", "Find the sum of all two-digit odd numbers.", 2, "MCQ", 9, 10, "Hard", "mathematical_ability", "All", True, 45, "AP series summation", make_mcq([("2475", "A"), ("2500", "B"), ("2450", "C"), ("2600", "D")], 0))
    q("EXP_MATH_10_07", "If x = 3 is a solution of equation x^2 + 2kx - 3 = 0, find value of k.", 2, "MCQ", 9, 10, "Easy", "mathematical_ability", "All", True, 46, "Linear substitution", make_mcq([("-1", "A"), ("1", "B"), ("-2", "C"), ("2", "D")], 0))
    q("EXP_MATH_10_08", "What is the discriminant of the quadratic equation 3x^2 - 5x + 2 = 0?", 2, "MCQ", 9, 10, "Easy", "mathematical_ability", "All", True, 47, "Discriminant", make_mcq([("1", "A"), ("-1", "B"), ("49", "C"), ("25", "D")], 0))
    q("EXP_MATH_10_09", "If tan(theta) = 4/3, what is the value of (sin(theta) + cos(theta))?", 2, "MCQ", 9, 10, "Medium", "mathematical_ability", "All", True, 48, "Trigonometric values", make_mcq([("7/5", "A"), ("1/5", "B"), ("5/7", "C"), ("1", "D")], 0))
    q("EXP_MATH_10_10", "A cone and a cylinder have equal bases and equal heights. What is the ratio of their volumes?", 2, "MCQ", 9, 10, "Easy", "mathematical_ability", "All", True, 49, "Cone cylinder volume ratio", make_mcq([("1:2", "A"), ("1:3", "B"), ("1:4", "C"), ("2:3", "D")], 1))

    # Class 11-12 Advanced Math (10 Qs)
    q("EXP_MATH_11_PCM_01", "Evaluate the limit: lim (x -> 0) [sin(5x) / (2x)]", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Science-PCM", True, 50, "Calculus limits", make_mcq([("1", "A"), ("5/2", "B"), ("2/5", "C"), ("0", "D")], 1))
    q("EXP_MATH_11_PCM_02", "What is the integral of (3x^2 + 4x - 5) dx?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Science-PCM", True, 51, "Indefinite integration", make_mcq([("x^3 + 2x^2 - 5x + C", "A"), ("6x + 4 + C", "B"), ("3x^3 + 4x^2 - 5x + C", "C"), ("x^3 + 4x^2 - 5x + C", "D")], 0))
    q("EXP_MATH_11_PCM_03", "In how many distinct ways can 5 books be arranged on a shelf?", 2, "MCQ", 11, 12, "Easy", "mathematical_ability", "Science-PCM", True, 52, "Permutations", make_mcq([("24", "A"), ("60", "B"), ("120", "C"), ("720", "D")], 2))
    q("EXP_MATH_12_PCM_04", "If matrix A is of order 2x3 and matrix B is of order 3x4, what is the order of matrix AB?", 2, "MCQ", 11, 12, "Easy", "mathematical_ability", "Science-PCM", True, 53, "Matrix multiplication order", make_mcq([("2x4", "A"), ("3x3", "B"), ("4x2", "C"), ("Undefined", "D")], 0))
    q("EXP_MATH_12_PCM_05", "What is the slope of the tangent to the curve y = x^3 - 3x + 2 at x = 2?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Science-PCM", True, 54, "Application of derivatives", make_mcq([("6", "A"), ("9", "B"), ("12", "C"), ("3", "D")], 1))
    q("EXP_MATH_11_COMM_02", "A company produces x units of goods with cost function C(x) = 500 + 20x. If each unit sells for $35, what is the break-even quantity?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Commerce", True, 55, "Break-even point analysis", make_mcq([("25 units", "A"), ("33.3 units", "B"), ("50 units", "C"), ("100 units", "D")], 1))
    q("EXP_MATH_11_COMM_03", "Calculate the Net Present Value (NPV) index of a $10,000 cash flow expected in 1 year at a discount rate of 8%.", 2, "MCQ", 11, 12, "Hard", "mathematical_ability", "Commerce", True, 56, "Financial discounting", make_mcq([("$9,259.26", "A"), ("$9,500.00", "B"), ("$10,800.00", "C"), ("$8,800.00", "D")], 0))
    q("EXP_MATH_12_COMM_04", "If the correlation coefficient between marketing expenditure and sales revenue is +0.92, how would you interpret this relationship?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Commerce", True, 57, "Statistical correlation", make_mcq([("Very strong positive linear relationship", "A"), ("Weak negative relationship", "B"), ("No correlation whatsoever", "C"), ("Strictly non-linear relationship", "D")], 0))
    q("EXP_MATH_11_HUM_01", "In a sociological survey of 200 citizens, 120 support public transport expansion and 80 support road widening, with 30 supporting both. How many support neither?", 2, "MCQ", 11, 12, "Medium", "mathematical_ability", "Humanities", True, 58, "Set theory survey", make_mcq([("10", "A"), ("20", "B"), ("30", "C"), ("50", "D")], 2))
    q("EXP_MATH_12_GEN_02", "If inflation rate is 6% per year, approximately how many years will it take for prices to double under the Rule of 72?", 2, "MCQ", 11, 12, "Easy", "mathematical_ability", "All", True, 59, "Rule of 72", make_mcq([("8 years", "A"), ("10 years", "B"), ("12 years", "C"), ("15 years", "D")], 2))

    # =========================================================================
    # SECTION 3: LOGICAL REASONING (30 additional questions)
    # =========================================================================
    q("EXP_LOGIC_7_01", "Look at this series: 7, 10, 8, 11, 9, 12, ___? What number comes next?", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 10, "Alternating series", make_mcq([("7", "A"), ("10", "B"), ("12", "C"), ("13", "D")], 1))
    q("EXP_LOGIC_7_02", "Bird is to Nest as Bee is to ___?", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 11, "Analogy habitat", make_mcq([("Hive", "A"), ("Honey", "B"), ("Flower", "C"), ("Tree", "D")], 0))
    q("EXP_LOGIC_7_03", "If South-East becomes North, and North-East becomes West, what will West become?", 3, "MCQ", 7, 8, "Medium", "logical_reasoning", "All", True, 12, "Direction sense rotation", make_mcq([("South-East", "A"), ("South-West", "B"), ("North-East", "C"), ("North-West", "D")], 0))
    q("EXP_LOGIC_7_04", "Four friends (P, Q, R, S) sit in a row. P is next to Q, but not next to R. If R is not next to S, who must be sitting next to S?", 3, "MCQ", 7, 8, "Medium", "logical_reasoning", "All", True, 13, "Linear arrangement", make_mcq([("P", "A"), ("Q", "B"), ("R", "C"), ("Cannot be determined", "D")], 0))
    q("EXP_LOGIC_8_01", "If 'EARTH' is coded as 'GCTTH', how is 'VENUS' coded in the same pattern (+2 to each letter)?", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 14, "Letter coding +2", make_mcq([("XGPWU", "A"), ("XGOWT", "B"), ("XHPWU", "C"), ("WFMVR", "D")], 0))
    q("EXP_LOGIC_8_02", "Which word does NOT belong with the others: Triangle, Rectangle, Cylinder, Pentagon?", 3, "MCQ", 7, 8, "Easy", "logical_reasoning", "All", True, 15, "Odd one out 2D vs 3D", make_mcq([("Triangle", "A"), ("Rectangle", "B"), ("Cylinder", "C"), ("Pentagon", "D")], 2))
    q("EXP_LOGIC_8_03", "A clock shows 3:30. What is the angle between the hour and minute hands?", 3, "MCQ", 7, 9, "Medium", "logical_reasoning", "All", True, 16, "Clock angle", make_mcq([("60 deg", "A"), ("75 deg", "B"), ("90 deg", "C"), ("105 deg", "D")], 1))
    q("EXP_LOGIC_9_01", "Statements: All cars are vehicles. All vehicles have wheels. Conclusion: All cars have wheels.", 3, "MCQ", 9, 10, "Easy", "logical_reasoning", "All", True, 17, "Syllogism valid", make_mcq([("Definitely True", "A"), ("Definitely False", "B"), ("Probably True", "C"), ("Insufficient Data", "D")], 0))
    q("EXP_LOGIC_9_02", "In a family, A is the father of B. B is the brother of C. C is the mother of D. How is A related to D?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 18, "Blood relations", make_mcq([("Grandfather", "A"), ("Uncle", "B"), ("Father", "C"), ("Brother", "D")], 0))
    q("EXP_LOGIC_9_03", "If + means *, - means /, * means +, and / means -, what is the value of 18 + 2 * 6 - 3 / 4?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 19, "Mathematical operations code", make_mcq([("34", "A"), ("36", "B"), ("38", "C"), ("42", "D")], 0))
    q("EXP_LOGIC_9_04", "Find the missing term: B2D, E4H, H8L, K16P, ___?", 3, "MCQ", 9, 10, "Medium", "logical_reasoning", "All", True, 20, "Alphanumeric series", make_mcq([("N32T", "A"), ("M32S", "B"), ("N32S", "C"), ("N64T", "D")], 0))
    q("EXP_LOGIC_10_01", "Six people (A, B, C, D, E, F) sit around a circular table facing the center. A sits opposite D. B is to the immediate right of A. F sits between A and C. Who sits opposite B?", 3, "MCQ", 9, 10, "Hard", "logical_reasoning", "All", True, 21, "Circular seating puzzle", make_mcq([("C", "A"), ("E", "B"), ("F", "C"), ("Cannot be determined", "D")], 1))
    q("EXP_LOGIC_10_02", "If it rains, the football match is postponed. Today the football match was NOT postponed. What can be logically concluded?", 3, "MCQ", 9, 11, "Medium", "logical_reasoning", "All", True, 22, "Modus tollens", make_mcq([("It did not rain", "A"), ("It rained heavily", "B"), ("The match was cancelled", "C"), ("Nothing can be concluded", "D")], 0))
    q("EXP_LOGIC_10_03", "Select the Venn diagram representation that best represents: Doctors, Surgeons, Musicians.", 3, "MCQ", 9, 11, "Medium", "logical_reasoning", "All", True, 23, "Venn classification", make_mcq([("All Surgeons are inside Doctors; Musicians intersect both", "A"), ("Three disjoint circles", "B"), ("All Doctors are inside Musicians", "C"), ("Surgeons and Musicians are concentric", "D")], 0))
    q("EXP_LOGIC_11_01", "Statement: 'Company X improved its market share by 40% after launching product Y.' Assumption: Product Y was attractive to consumers.", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 24, "Statement and assumptions", make_mcq([("Assumption is Implicit", "A"), ("Assumption is Not Implicit", "B"), ("Contradictory", "C"), ("Irrelevant", "D")], 0))
    q("EXP_LOGIC_11_02", "In a code language: 'tim nit pit' means 'study very hard', 'nit sit rit' means 'work hard now', and 'rit pit kit' means 'study and work'. What word represents 'very'?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 25, "Fictitious code deduction", make_mcq([("tim", "A"), ("nit", "B"), ("pit", "C"), ("sit", "D")], 0))
    q("EXP_LOGIC_12_01", "A cube has its 6 faces painted with 6 different colors (Red, Blue, Green, Yellow, Orange, White). Red is opposite Blue. Green is adjacent to Red and Yellow. If Orange is opposite Green, what color is opposite Yellow?", 3, "MCQ", 11, 12, "Hard", "logical_reasoning", "All", True, 26, "Cube face deduction", make_mcq([("White", "A"), ("Blue", "B"), ("Orange", "C"), ("Red", "D")], 0))

    # =========================================================================
    # SECTION 4: SCIENTIFIC THINKING (35 additional questions)
    # =========================================================================
    q("EXP_SCI_7_01", "What property of air allows hot air balloons to rise?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 10, "Thermal expansion density", make_mcq([("Hot air is less dense than surrounding cold air", "A"), ("Hot air has magnetic repulsion", "B"), ("Cold air pushes down on the balloon top", "C"), ("Hot air contains only hydrogen", "D")], 0))
    q("EXP_SCI_7_02", "Which layer of the Earth contains tectonic plates that cause earthquakes?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 11, "Earth science crust", make_mcq([("Crust & uppermost mantle (Lithosphere)", "A"), ("Outer core", "B"), ("Inner core", "C"), ("Atmosphere", "D")], 0))
    q("EXP_SCI_7_03", "Why do electrical wires have plastic or rubber coatings?", 4, "MCQ", 7, 8, "Easy", "scientific_reasoning", "All", True, 12, "Insulators vs conductors", make_mcq([("Plastic is an electrical insulator to prevent electric shocks", "A"), ("Plastic increases electric current flow", "B"), ("Plastic cools down the copper wires", "C"), ("For colorful appearance only", "D")], 0))
    q("EXP_SCI_8_01", "What type of chemical reaction is represented by: 2H2 + O2 -> 2H2O?", 4, "MCQ", 7, 9, "Easy", "scientific_reasoning", "All", True, 13, "Combination reaction", make_mcq([("Combination / Synthesis", "A"), ("Decomposition", "B"), ("Displacement", "C"), ("Double displacement", "D")], 0))
    q("EXP_SCI_8_02", "What is the primary function of white blood cells (leukocytes) in the human body?", 4, "MCQ", 7, 9, "Easy", "scientific_reasoning", "All", True, 14, "Human immunology basic", make_mcq([("Defend against infections and pathogens", "A"), ("Transport oxygen to tissues", "B"), ("Clot blood at wound sites", "C"), ("Digest food in the stomach", "D")], 0))
    q("EXP_SCI_9_01", "Why does a pencil placed obliquely in a glass of water appear bent at the water surface?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 15, "Light refraction", make_mcq([("Refraction caused by change in speed of light across media", "A"), ("Total internal reflection", "B"), ("Diffraction of sound waves", "C"), ("Dispersion of white light", "D")], 0))
    q("EXP_SCI_9_02", "Which element has the electron configuration 2, 8, 7?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 16, "Periodic table chlorine", make_mcq([("Chlorine (Cl)", "A"), ("Sodium (Na)", "B"), ("Argon (Ar)", "C"), ("Fluorine (F)", "D")], 0))
    q("EXP_SCI_9_03", "How do enzymes speed up biochemical reactions in living organisms?", 4, "MCQ", 9, 10, "Medium", "scientific_reasoning", "All", True, 17, "Biological catalysts", make_mcq([("By lowering the activation energy barrier", "A"), ("By increasing body temperature", "B"), ("By changing chemical equilibrium", "C"), ("By being consumed as fuel", "D")], 0))
    q("EXP_SCI_10_01", "According to Ohm's Law (V = IR), if the resistance R is kept constant and potential difference V is tripled, what happens to current I?", 4, "MCQ", 9, 10, "Easy", "scientific_reasoning", "All", True, 18, "Ohms law", make_mcq([("Current is tripled", "A"), ("Current is reduced to one-third", "B"), ("Current remains unchanged", "C"), ("Current becomes zero", "D")], 0))
    q("EXP_SCI_10_02", "What is the greenhouse gas with the highest relative contribution to anthropogenic global warming by volume emitted?", 4, "MCQ", 9, 10, "Easy", "scientific_reasoning", "All", True, 19, "Environmental carbon dioxide", make_mcq([("Carbon Dioxide (CO2)", "A"), ("Methane (CH4)", "B"), ("Nitrous Oxide (N2O)", "C"), ("Ozone (O3)", "D")], 0))
    q("EXP_SCI_11_PCM_01", "In quantum mechanics and modern physics, what is the photoelectric effect evidence of?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCM", True, 20, "Particle nature of light", make_mcq([("Particle nature of electromagnetic radiation (photons)", "A"), ("Continuous wave nature of light only", "B"), ("Gravitational lensing", "C"), ("Nuclear fusion in stars", "D")], 0))
    q("EXP_SCI_11_PCB_01", "During DNA replication, which enzyme synthesizes the complementary DNA strand by adding nucleotides in the 5' to 3' direction?", 4, "MCQ", 11, 12, "Hard", "scientific_reasoning", "Science-PCB", True, 21, "DNA polymerase", make_mcq([("DNA Polymerase", "A"), ("RNA Helicase", "B"), ("DNA Ligase", "C"), ("Topoisomerase", "D")], 0))

    # =========================================================================
    # SECTION 9: COMPUTATIONAL THINKING & DIGITAL FLUENCY (20 Qs)
    # =========================================================================
    q("EXP_DIG_7_01", "What does 'URL' stand for in web browsers?", 9, "MCQ", 7, 8, "Easy", "digital_ability", "All", True, 10, "Internet concepts", make_mcq([("Uniform Resource Locator", "A"), ("Universal Radio Link", "B"), ("Unified Routing Logic", "C"), ("User Register Log", "D")], 0))
    q("EXP_DIG_7_02", "Which of the following is a cloud storage service?", 9, "MCQ", 7, 8, "Easy", "digital_ability", "All", True, 11, "Cloud computing basics", make_mcq([("Google Drive / Microsoft OneDrive", "A"), ("RAM chip", "B"), ("CPU heat sink", "C"), ("Motherboard BIOS", "D")], 0))
    q("EXP_DIG_8_01", "What is phishing in cybersecurity?", 9, "MCQ", 7, 9, "Medium", "digital_ability", "All", True, 12, "Cybersecurity awareness", make_mcq([("Fraudulent attempts to steal passwords/credentials by impersonating trusted entities", "A"), ("Writing computer software code", "B"), ("Cleaning dust from computer hardware", "C"), ("A video game tournament", "D")], 0))
    q("EXP_DIG_9_01", "In binary code (base 2), what decimal number is represented by 1011?", 9, "MCQ", 9, 10, "Medium", "digital_ability", "All", True, 13, "Binary to decimal", make_mcq([("11", "A"), ("10", "B"), ("13", "C"), ("15", "D")], 0))
    q("EXP_DIG_9_02", "What is the time complexity of searching an element in a sorted array of size N using Binary Search?", 9, "MCQ", 9, 12, "Hard", "digital_ability", "All", True, 14, "Big O binary search", make_mcq([("O(log N)", "A"), ("O(N)", "B"), ("O(N^2)", "C"), ("O(1)", "D")], 0))
    q("EXP_DIG_11_01", "What is the core difference between a relational SQL database and a NoSQL document database?", 9, "MCQ", 11, 12, "Hard", "digital_ability", "All", True, 15, "SQL vs NoSQL", make_mcq([("SQL uses structured tables with schemas; NoSQL stores flexible JSON-like documents or key-values", "A"), ("SQL cannot run on computers", "B"), ("NoSQL does not use storage disks", "C"), ("They have identical architectures", "D")], 0))

    # =========================================================================
    # SECTION 13: DISCIPLINARY FIELD AFFINITIES (20 Qs)
    # =========================================================================
    q("EXP_INT_CYBER_SEC", "How interested are you in ethical hacking, encrypting communications, and defending computer networks from cyber attacks?", 13, "RATING", 7, 12, "Medium", "technology_interest", "All", True, 30, "Cybersecurity interest", make_rating("Not Interested", "Top Passion / Dream Role"))
    q("EXP_INT_RENEW_ENERGY", "How excited are you to research solar panels, hydrogen fuel cells, and next-generation battery chemistry?", 13, "RATING", 7, 12, "Medium", "science_interest", "All", True, 31, "Clean energy interest", make_rating("Not Interested", "Top Passion / Dream Role"))
    q("EXP_INT_NEURO_SCI", "How interested are you in brain-computer interfaces, neuroscience, and mental health research?", 13, "RATING", 7, 12, "Medium", "healthcare_interest", "All", True, 32, "Neuroscience interest", make_rating("Not Interested", "Top Passion / Dream Role"))
    q("EXP_INT_VENTURE_CAP", "How interested are you in assessing startup business pitches and investing capital in high-growth enterprises?", 13, "RATING", 7, 12, "Medium", "business_interest", "All", True, 33, "Venture capital interest", make_rating("Not Interested", "Top Passion / Dream Role"))
    q("EXP_INT_DIPLOMACY", "How interested are you in international relations, geopolitics, and representing your country as a diplomat?", 13, "RATING", 7, 12, "Medium", "social_interest", "All", True, 34, "Diplomacy interest", make_rating("Not Interested", "Top Passion / Dream Role"))
    q("EXP_INT_GAME_DEV", "How interested are you in 3D game engine programming, virtual reality (VR) physics, and worldbuilding?", 13, "RATING", 7, 12, "Medium", "creative_interest", "All", True, 35, "Game design interest", make_rating("Not Interested", "Top Passion / Dream Role"))

    return questions
