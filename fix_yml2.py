import glob
import re

files = glob.glob('.github/workflows/fastbuild_*.yml')

for fpath in files:
    with open(fpath, 'r', newline='', encoding='utf-8') as f:
        content = f.read()
    
    # We want to replace the whole block starting from curl setup.sh to sed DKSU_VERSION
    # Because it is a bit messy right now with the previous script.
    
    # Find the block inside `elif [[ ${{ github.event.inputs.ksu_type }} == "ksu" ]]; then`
    # Let's just use regex to match the exact block to rewrite it cleanly.
    pattern = re.compile(
        r'elif \[\[ \$\{\{ github\.event\.inputs\.ksu_type \}\} == "ksu" \]\]; then\s*'
        r'echo "正在配置原版 KernelSU \(tiann/KernelSU\)\.\.\."\s*'
        r'curl -LSs "https://raw\.githubusercontent\.com/tiann/KernelSU/refs/heads/main/kernel/setup\.sh" \| bash -s main\s*'
        r'(?:cd \./KernelSU\s*git checkout f9c7823e3e9a6034c236a3b275132878cbae7f9f\s*cd \.\.\s*)?'
        r'cd \./KernelSU\s*'
        r'KSU_VERSION=\$\(expr \$\(curl -sI "https://api\.github\.com/repos/tiann/KernelSU/commits\?sha=main&per_page=1" \| grep -i "link:" \| sed -n \'s/\.\*page=\\(\[0-9\]\*\\)>; rel="last"\.\*/\\1/p\'\) "\+" 30000\)\s*'
        r'echo "KSUVER=\$KSU_VERSION" >> \$GITHUB_ENV\s*'
        r'echo "ksuver=\$KSU_VERSION" >> \$GITHUB_OUTPUT\s*'
        r'sed -i "s/DKSU_VERSION=16/DKSU_VERSION=\$\{KSU_VERSION\}/" kernel/Kbuild'
    )
    
    replacement = (
        'elif [[ ${{ github.event.inputs.ksu_type }} == "ksu" ]]; then\n'
        '            echo "正在配置原版 KernelSU (tiann/KernelSU)..."\n'
        '            curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/refs/heads/main/kernel/setup.sh" | bash -s main\n'
        '            cd ./KernelSU\n'
        '            echo "回退 KernelSU 到 32483 版本 (commit f9c7823)..."\n'
        '            git checkout f9c7823e3e9a6034c236a3b275132878cbae7f9f\n'
        '            KSU_VERSION=32483\n'
        '            echo "KSUVER=$KSU_VERSION" >> $GITHUB_ENV\n'
        '            echo "ksuver=$KSU_VERSION" >> $GITHUB_OUTPUT\n'
        '            sed -i "s/DKSU_VERSION=16/DKSU_VERSION=${KSU_VERSION}/" kernel/Kbuild'
    )
    
    if pattern.search(content):
        # We need to preserve original line endings (CRLF vs LF)
        if '\r\n' in content:
            replacement_str = replacement.replace('\n', '\r\n')
        else:
            replacement_str = replacement
            
        new_content = pattern.sub(replacement_str, content)
        with open(fpath, 'w', newline='', encoding='utf-8') as f:
            f.write(new_content)
        print(f'{fpath}: replaced block OK')
    else:
        print(f'{fpath}: block not found')
