import os

def create_markdown(document):
    md = """"""
    f = open("slidegen/theme.md", "r")
    atext = f.read()
    f.close()
    md += atext+"\n"
    md += create_home_slide(document)

    for i, (topic, content) in enumerate(document['slides'].items()):
        for num, sentences in content.items():
            md += create_new_slide(topic,sentences)

    return md

def create_home_slide(document):
    # Create a home slide
    text = "\n# " + document['title'] + "\n" + document['author'][0] + "\n\n"
    if document['image'] != '':
        text += "---\n![bg]({})\n".format(document['image'])
    return text


def create_new_slide(topic,content):
    text = "\n---\n# " + topic + "\n"
    for sentence in content:
        text += "\n- " + sentence + "\n"
    return text

def create_slides(document):
    md = create_markdown(document)
    f = open('output.md', 'w')
    f.write(md)
    f.close()
    #marp should have executable permissions
    os.system('marp output.md --html')