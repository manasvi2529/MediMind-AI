"""Small educational knowledge base: symptom matching, vitals ranges, first aid."""

SYMPTOMS = ["fever", "cough", "sore throat", "runny nose", "sneezing", "itchy eyes", "headache",
            "body aches", "fatigue", "nausea", "vomiting", "diarrhea", "stomach pain", "rash",
            "joint pain", "shortness of breath", "chest pain", "dizziness", "frequent urination",
            "burning urination", "excess thirst", "loss of smell"]

CONDITIONS = [
    ("Common cold", ["runny nose", "sore throat", "cough", "sneezing", "fatigue"],
     "Usually settles in 7-10 days. Rest, fluids, warm salt-water gargles, steam."),
    ("Influenza (flu)", ["fever", "body aches", "fatigue", "cough", "headache", "sore throat"],
     "Rest and fluids. See a doctor if elderly, pregnant, chronically ill, or getting worse."),
    ("Dengue / viral fever", ["fever", "headache", "body aches", "joint pain", "rash", "nausea"],
     "Get a blood test if fever lasts over 2 days. Avoid aspirin/ibuprofen unless a doctor says so. Urgent care for bleeding, severe belly pain or constant vomiting."),
    ("Allergic rhinitis", ["sneezing", "runny nose", "itchy eyes"],
     "Avoid triggers (dust, pollen). Ask a pharmacist about an antihistamine."),
    ("Gastroenteritis", ["nausea", "vomiting", "diarrhea", "stomach pain", "fever"],
     "Drink ORS often. Seek care for blood in stool, no urine for 8+ hours, or if you cannot keep fluids down."),
    ("Migraine / tension headache", ["headache", "nausea", "dizziness"],
     "Rest in a dark quiet room and drink water. See a doctor if new, severe or frequent."),
    ("Urinary tract infection", ["burning urination", "frequent urination", "stomach pain"],
     "Needs a urine test and often antibiotics. See a doctor within a day or two; sooner with fever or back pain."),
    ("High blood sugar (possible diabetes)", ["excess thirst", "frequent urination", "fatigue", "dizziness"],
     "Get a fasting glucose / HbA1c test."),
    ("COVID-19 or similar virus", ["fever", "cough", "loss of smell", "fatigue", "sore throat"],
     "Rest, keep away from others, watch oxygen. Seek care if SpO2 is below 94% or breathing worsens."),
    ("Chest infection / asthma flare", ["shortness of breath", "cough", "fever"],
     "Needs medical assessment. Do not wait if breathing is hard."),
]

AID = {
    "Burns": ["Cool under running tap water for 20 minutes.", "Remove rings/tight items before swelling.",
              "Cover loosely with clean cling film or cloth.", "No ice, butter, toothpaste or oil.",
              "Seek care for large, deep, facial or chemical burns."],
    "Choking (adult)": ["Ask if they are choking. If they cannot speak or breathe, act.",
                        "Give up to 5 firm back blows between the shoulder blades.",
                        "Then 5 abdominal thrusts. Repeat.", "Call 112 if it does not clear; start CPR if unresponsive."],
    "Severe bleeding": ["Call 112/108.", "Press firmly with a clean cloth. Add more cloth; do not remove soaked ones.",
                        "Raise the limb and keep pressing at least 10 minutes.", "Keep the person lying down and warm."],
    "Heart attack signs": ["Chest pressure or pain spreading to arm/jaw, sweating, breathlessness.",
                           "Call 112/108 and sit the person down.",
                           "If not allergic, chew one 300 mg aspirin.", "Be ready to start CPR."],
    "Stroke (FAST)": ["Face drooping, Arm weakness, Speech slurred means Time to call 112.",
                      "Note when symptoms began.", "Give no food, drink or medicine."],
    "Fainting": ["Lay them flat and raise their legs.", "Loosen tight clothing, give fresh air.",
                 "If not awake within a minute, call 112 and check breathing."],
    "Snake or animal bite": ["Keep calm and still; keep the limb below heart level.",
                             "Wash animal bites with soap and water for 15 minutes.",
                             "Do not cut, suck or tie tightly. Go to hospital at once."],
    "Fever in a child": ["Under 3 months with any fever: see a doctor today.", "Dress lightly, offer fluids.",
                         "Use paracetamol by weight as per label or doctor.",
                         "Urgent care for stiff neck, fits, rash that does not fade, or unusual drowsiness."],
}


def match(selected, days=1):
    sel = {s for s in selected if s in SYMPTOMS}
    scored = []
    for name, syms, advice in CONDITIONS:
        m = len(sel & set(syms))
        if m:
            scored.append({"name": name, "overlap": round(m / max(len(syms), len(sel)), 2), "advice": advice})
    scored.sort(key=lambda x: -x["overlap"])
    urgent = bool(sel & {"chest pain", "shortness of breath"})
    return {"matches": scored[:3], "urgent": urgent, "see_doctor": days >= 7}


def vitals(d):
    out = []

    def add(label, value, level, note):
        out.append({"label": label, "value": value, "level": level, "note": note})

    def num(k):
        try:
            v = float(d.get(k))
            return v if v > 0 else None
        except (TypeError, ValueError):
            return None

    sy, di, hr, tp, sp, bs = (num(k) for k in ("sys", "dia", "hr", "temp", "spo2", "sugar"))
    if sy and di:
        bp = f"{sy:.0f}/{di:.0f}"
        if sy >= 180 or di >= 120: add("Blood pressure", bp, "bad", "Crisis: seek care now")
        elif sy >= 140 or di >= 90: add("Blood pressure", bp, "bad", "High")
        elif sy >= 130 or di >= 80: add("Blood pressure", bp, "warn", "Elevated")
        elif sy < 90 or di < 60: add("Blood pressure", bp, "warn", "Low")
        else: add("Blood pressure", bp, "ok", "Normal")
    if hr:
        if hr > 120 or hr < 45: add("Pulse", f"{hr:.0f}", "bad", "See a doctor")
        elif hr > 100: add("Pulse", f"{hr:.0f}", "warn", "Fast")
        elif hr < 60: add("Pulse", f"{hr:.0f}", "warn", "Slow")
        else: add("Pulse", f"{hr:.0f}", "ok", "Normal")
    if tp:
        if tp >= 39.5: add("Temperature", f"{tp:.1f} C", "bad", "High fever")
        elif tp >= 38: add("Temperature", f"{tp:.1f} C", "warn", "Fever")
        elif tp < 35: add("Temperature", f"{tp:.1f} C", "bad", "Low")
        else: add("Temperature", f"{tp:.1f} C", "ok", "Normal")
    if sp:
        if sp < 90: add("SpO2", f"{sp:.0f}%", "bad", "Urgent: seek care")
        elif sp < 94: add("SpO2", f"{sp:.0f}%", "warn", "Low")
        else: add("SpO2", f"{sp:.0f}%", "ok", "Normal")
    if bs:
        if bs < 70: add("Fasting sugar", f"{bs:.0f}", "bad", "Low sugar")
        elif bs >= 126: add("Fasting sugar", f"{bs:.0f}", "bad", "Diabetic range")
        elif bs >= 100: add("Fasting sugar", f"{bs:.0f}", "warn", "Pre-diabetic range")
        else: add("Fasting sugar", f"{bs:.0f}", "ok", "Normal")
    return out
