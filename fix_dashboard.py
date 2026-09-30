
file_path = r'c:\codes\вкр\templates\super_dashboard.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1-based indices to delete: 399 to 786
# 0-based: 398 to 786 (exclusive of end? No, inclusive of 786)
# Python slice: [0:398] + [786:]

start_delete = 399
end_delete = 786

new_lines = lines[:start_delete-1] + lines[end_delete:]

# Replace label
for i, line in enumerate(new_lines):
    if 'Выручка (Месяц)' in line:
        new_lines[i] = line.replace('Выручка (Месяц)', 'Выручка (День)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Fixed file. New line count: {len(new_lines)}")
