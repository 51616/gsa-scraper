import sys
import markdown


def main():
  file = sys.argv[1]
  with open(file,'r') as f:
    t = f.read()
    html = markdown.markdown(t)
  with open(file.split('.')[0]+'.html','w') as f:
    f.write(html)

if __name__=='__main__':
  main()
