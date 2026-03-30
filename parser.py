import re

class Parser:
    def __init__(self):
        self.file = None
        self.lines = []
        self.output = []

    def read(self):
        with open(self.file, 'r') as f:
            self.lines = f.readlines()

    def parse(self):
            i = 0
            while i < len(self.lines):
                line = self.lines[i].strip()
                if line.startswith('```'):
                    i = self.handle_code_blocks(i)
                elif re.match(r'^[-*+]\s+', line) or re.match(r'^\d+\.\s+', line):
                    i = self.handle_lists(i)
                else:
                    out = self.parse_line(self.lines[i])
                    if out:
                        self.output.append(out)
                    i += 1

    def parse_line(self, line):
        if not line.strip():
            return ""
        if line.strip() == '---':
            return '<hr>'
        result = self.handle_headings(line)
        if result: return result
        result = self.handle_blockquotes(line)
        if result: return result
        return self.handle_paragraphs(line)

    def handle_headings(self, line):
        match = re.match(r'^(#{1,6})\s+(.*)', line)
        if match:
            level = len(match.group(1))
            content = match.group(2).strip()
            return f'<h{level}>{content}</h{level}>'

    def handle_paragraphs(self, line):
        return f'<p>{self.handle_formatting(line.strip())}</p>'

    def handle_formatting(self, para):
        para = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', para)
        para = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', para)
        para = re.sub(r'\*(.*?)\*', r'<i>\1</i>', para)
        para = re.sub(r'`(.*?)`', r'<code>\1</code>', para)
        para = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', para)
        return para

    def handle_lists(self, i):
        tag = 'ol' if re.match(r'^\d+\.', self.lines[i]) else 'ul'
        items = ''
        while i < len(self.lines) and ((tag == 'ul' and (re.match(r'^[-*+]\s+', self.lines[i])) or (tag == 'ol' and re.match(r'^\d+\.\s+', self.lines[i])))):
            content = re.match(r'^[-*+\d.]+\s+(.*)', self.lines[i]).group(1).strip()
            items += f'  <li>{self.handle_formatting(content)}</li>\n'
            i += 1
        self.output.append(f'<{tag}>\n{items}</{tag}>')
        return i
    
    def handle_blockquotes(self, line):
        match = re.match(r"^>\s*(.*)", line)
        if match:
            return f'<blockquote><p>{self.handle_formatting(match.group(1))}</p></blockquote>'
        
    def handle_code_blocks(self, i):
        i += 1 
        content = []
        
        while i < len(self.lines) and not self.lines[i].strip().startswith('```'):
            content.append(self.lines[i].rstrip()) 
            i += 1
        
        code = '\n'.join(content)
        self.output.append(f'<pre><code>{code}</code></pre>')
        
        return i + 1

    def write(self, output_path):
        with open(output_path, 'w') as f:
            f.write('\n'.join(self.output))

    def wrap(self):
        content = '\n'.join(self.output)
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Parsed Document</title>
</head>
<body>
{content}
</body>
</html>"""
        self.output = [html]
    
    def do(self, input, output):
        self.file = input
        self.read()
        self.parse()
        self.wrap()
        self.write(output)

fparser = Parser()
fparser.do('test.md', 'test.html')