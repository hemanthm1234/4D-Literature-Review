import sys

if __name__ == '__main__':
    content = sys.stdin.read()
    with open('/data1/hemanth/4D/notes.md', 'a') as f:
        f.write(content + '\n\n')
