import re

VARIATION_REGEX = re.compile(r'^[A-Z]{3}(CH|FA|FT|HE|HN|LG|MN|TA|TL|UA)\d{4}_MDF$')

def material_tag_parse(tag: str, is_chr=True) -> str:

    if not is_chr:
        return ""

    if len(tag) >= 5 and tag.startswith("CLK"):
        if tag[3:5].isdigit():
            return "CLK"

    if tag.startswith("CHR_EYE") and len(tag) >= len("CHR_EYE") + 3:
        digits = tag[-7:-4]
        if digits.isdigit():
            return tag[:-5]

    if VARIATION_REGEX.match(tag) and len(tag) == 13:
        sixth_seventh = int(tag[5:7])
        eighth_ninth = int(tag[7:9])

        if sixth_seventh > 0 or eighth_ninth > 10:
            return tag[:3]

    return ""