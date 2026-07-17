raw_text = "  Python, 起步,工具,Python  "

raw_tags = raw_text.split(",")
clean_tags = []
for tag in raw_tags:
    clean_tags.append(tag.strip())

unique_tags = sorted(set(clean_tags))

print("原文本：", repr(raw_text))
print("清理后：", clean_tags)
print("显示：", " | ".join(clean_tags))
print("去重：", unique_tags)
