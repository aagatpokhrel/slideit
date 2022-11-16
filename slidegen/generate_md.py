import os

def create_markdown(doc):
    # Create a markdown object
    md = """"""
    f = open("slidegen/theme_data.md", "r")
    atext = f.read()
    f.close()
    md += atext
    md += create_home_slide(doc)
    md += create_new_slide(doc)
    return md

def create_home_slide(doc):
    # Create a home slide
    text = "\n# " + doc['title'] + "\n" + doc['subtitle'] + "\n"
    text += """<div class="pt-12">
        <span @click="$slidev.nav.next" class="px-2 py-1 rounded cursor-pointer" hover="bg-white bg-opacity-10">
            Press Space for next page <carbon:arrow-right class="inline"/>
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

def create_new_slide(doc):
    # Create a new slide
    contents = doc['slides']
    print (contents)
    text = ''
    for content in contents:
        text += "\n## " + content + "\n"
    return text