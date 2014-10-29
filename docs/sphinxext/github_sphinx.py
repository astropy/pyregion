"""
:Description: Sphinx extension to remove leading under-scores from directories names in the html build output directory.
"""
import os
import shutil

from docutils.io import StringOutput
from sphinx.util import relative_uri

from sphinx.builders.html import StandaloneHTMLBuilder as RealStandaloneHTMLBuilder

class StandaloneHTMLBuilder(RealStandaloneHTMLBuilder):
    def write_doc(self, docname, doctree):
        destination = StringOutput(encoding='utf-8')
        doctree.settings = self.docsettings

        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        self.imgpath = relative_uri(self.get_target_uri(docname), 'images')
        self.post_process_images(doctree)
        self.dlpath = relative_uri(self.get_target_uri(docname), 'downloads')
        self.docwriter.write(doctree, destination)
        self.docwriter.assemble_parts()
        body = self.docwriter.parts['fragment']
        metatags = self.docwriter.clean_meta

        ctx = self.get_doc_context(docname, body, metatags)
        self.index_page(docname, doctree, ctx.get('title', ''))
        self.handle_page(docname, ctx, event_arg=doctree)



def setup(app):
    """
    Add a html-page-context  and a build-finished event handlers
    """
    app.connect('html-page-context', change_pathto)
    app.connect('build-finished', move_private_folders)

    import sphinx.builders.html
    sphinx.builders.html.StandaloneHTMLBuilder = StandaloneHTMLBuilder
    
def change_pathto(app, pagename, templatename, context, doctree):
    """
    Replace pathto helper to change paths to folders with a leading underscore.
    """
    pathto = context.get('pathto')
    def gh_pathto(otheruri, *args, **kw):
        if otheruri.startswith('_'):
            otheruri = otheruri[1:]
        return pathto(otheruri, *args, **kw)
    context['pathto'] = gh_pathto
    
def move_private_folders(app, e):
    """
    remove leading underscore from folders in in the output folder.
    
    :todo: should only affect html built
    """
    def join(dir):
        return os.path.join(app.builder.outdir, dir)
    
    for item in os.listdir(app.builder.outdir):
        if item.startswith('_') and os.path.isdir(join(item)):
            if os.path.exists(join(item[1:])):
                shutil.rmtree(join(item[1:]))
            shutil.move(join(item), join(item[1:]))
