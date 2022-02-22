from json.tool import main


def toKeyword(keyword):
    p = "@_(r'\\b"
    for k in keyword:
        p+= "["+k.lower()+k.upper()+"]"
    p += "\\b')\n"
    p += f"def {keyword.upper()}(self, t): " + "return t"
    # p += "    return t"

    return p

if __name__ == "__main__":
    l = ["ELSE", "IF", "FI", "THEN", "NOT", "IN", "CASE", "ESAC", "CLASS",
        "INHERITS", "ISVOID", "LET", "LOOP", "NEW", "OF",
        "POOL", "THEN", "WHILE", "NUMBER"]

    for w in l:
        print(toKeyword(w))
        print()