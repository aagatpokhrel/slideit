from slidegen.generate_md import create_markdown
import os

def generateSlides(doc):
    print ("generating slides...")
    # Create a markdown object
    md = create_markdown(doc)
    # Create a pdf object
    print (md)
    f = open('slidev/slides.md', 'w')
    f.write(md)
    f.close()
    os.system('cd slidev && npm run export')
