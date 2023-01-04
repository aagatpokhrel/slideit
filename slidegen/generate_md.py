import os

def create_markdown(doc):
    noOfSLides = len(doc['slides'])

    print("doc is :::\n", doc)
    # Create a markdown object
    md = """"""
    f = open("slidegen/theme_data.md", "r")
    atext = f.read()
    f.close()
    md += atext
    md += create_home_slide(doc)

    for i in range(noOfSLides):
        md += create_new_slide(doc,i)

    return md

def create_home_slide(doc):
    # Create a home slide
    text = "\n# " + doc['title'] + "\n" + doc['subtitle'] + "\n"
    text += """<div class="pt-12">
        <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
            <carbon:arrow-right class="inline"/>
        </span></div>
        <div class="abs-br m-6 flex gap-2">
        <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="text-xl icon-btn opacity-50 !border-none !hover:text-white">
            <carbon:edit />
        </button>
        <a href="https://github.com/slidevjs/slidev" target="_blank" alt="GitHub"
            class="text-xl icon-btn opacity-50 !border-none !hover:text-white">
            <carbon-logo-github />
        </a>
        </div>
---
    """
    return text

def create_new_slide(doc,slideNum):
    # Create a new slide
    contents = doc['slides'][slideNum]
    totalSlides = len(doc['slides'])

    # print (contents)
    text = ''

    # adding the title
    titles = list(doc['slides'].keys())
    text += "\n# " + str(titles[slideNum]) + "\n"

    # adding the bullet points
    for content in contents:
        text += "\n- " + content + "\n"

    if slideNum != totalSlides-1:
        text += "\n---\n"

    return text