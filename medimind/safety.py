"""Emergency red-flag detection (English + Hindi keywords). Runs on every message."""
import re

RULES = [
    (r"chest (pain|pressure|tight)|crushing|सीने में दर्द|छाती में दर्द|सीने में जकड़न", "chest pain"),
    (r"can.?t breathe|cannot breathe|gasping|severe (shortness|breathless)|सांस (नहीं|लेने में (बहुत )?तकलीफ)|साँस (नहीं|लेने में)", "trouble breathing"),
    (r"face droop|slurred|one.?sided weak|sudden (numb|confus|vision)|worst headache|लकवा|बोलने में दिक्कत|मुंह टेढ़ा", "possible stroke"),
    (r"unconscious|not responding|passed out|seizure|convuls|बेहोश|दौरा पड़|मिर्गी", "unconscious or seizure"),
    (r"heavy bleeding|bleeding (a lot|won.?t stop)|vomit(ing)? blood|coughing (up )?blood|खून (बह|बंद नहीं)|खून की उल्टी", "serious bleeding"),
    (r"swelling of (the )?(face|throat|tongue)|anaphyla|गले में सूजन|होंठ.*सूज", "severe allergy"),
    (r"suicid|kill myself|end my life|want to die|self.?harm|आत्महत्या|मर जाना चाहता|मरना चाहती|जान देना", "self-harm"),
    (r"overdose|poison|swallowed (bleach|pills|acid)|जहर|ज़हर|ज्यादा गोलियां", "poisoning"),
]
_COMPILED = [(re.compile(p, re.I), label) for p, label in RULES]


def detect(text: str) -> list[str]:
    return sorted({label for rx, label in _COMPILED if rx.search(text or "")})
