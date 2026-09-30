
file_path = r'c:\codes\вкр\templates\super_dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1-indexed to 0-indexed conversion
# Keep 1-470 (indices 0-469)
# Skip 471-665 (indices 470-664)
# Keep 666-end (indices 665-end)

part1 = lines[:470]
part2 = lines[665:]

new_content = "".join(part1 + part2)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Fixed {file_path}. Original lines: {len(lines)}, New lines: {len(part1) + len(part2)}")
