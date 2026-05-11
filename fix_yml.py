import glob

target_line = '            curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/refs/heads/main/kernel/setup.sh" | bash -s main\r\n'
insert_lines = [
    '            cd ./KernelSU\r\n',
    '            git checkout f9c7823e3e9a6034c236a3b275132878cbae7f9f\r\n',
    '            cd ..\r\n'
]

files = glob.glob('.github/workflows/fastbuild_*.yml')
for fpath in files:
    with open(fpath, 'r', newline='', encoding='utf-8') as f:
        lines = f.readlines()

    content_str = ''.join(lines)
    if 'git checkout f9c7823e3e9a6034c236a3b275132878cbae7f9f' in content_str:
        print(f'{fpath}: already patched, skipping')
        continue

    new_lines = []
    patched = False
    for line in lines:
        new_lines.append(line)
        if line == target_line and not patched:
            new_lines.extend(insert_lines)
            patched = True

    if patched:
        with open(fpath, 'w', newline='', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f'{fpath}: patched OK')
    else:
        print(f'{fpath}: target not found')
