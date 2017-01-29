# -*- coding: utf-8 -*-
"""
Recent news article list -- BNEWS
=================================
Author: Toni Heittola (toni.heittola@gmail.com)

"""

import os
import shutil
import logging
import copy
from bs4 import BeautifulSoup
from jinja2 import Template
from pelican import signals, contents
import datetime
from babel.dates import format_timedelta

logger = logging.getLogger(__name__)
__version__ = '0.1.0'

bnews_default_settings = {
    'header': 'News',
    'header-link': '/news.html',
    'panel-color': 'panel-default',
    'mode': 'panel',
    'template': {
        'panel': """
            <div class="panel {{ panel_color }} hidden-print">
              <div class="panel-heading">
                <h3 class="panel-title"><a href="{{ site_url }}{{header_link}}">{{header}}</a></h3>
              </div>
              <ul class="bnews-container list-group">
              {{news_list}}
              </ul>
            </div>
        """,
        'list': """
            <h3 class="section-heading text-center"><a href="{{ site_url }}{{header_link}}">{{header}}</a></h3>
            <div class="list-group bnews-container">
            {{news_list}}
            </div>
        """},
    'item-template': {
        'panel': """
            <a class="list-group-item" href="{{ site_url}}/{{ article_url}}">
            <div class="row">
            <div class="col-md-12 col-sm-12"><h5 class="list-group-item-heading">{{article_title}}</h5></div>
            <div class="col-md-12 col-sm-12"><p class="list-group-item-text text-muted">{{article_category}} {{article_date}}</p></div>
            </div>
            </a>
        """,
        'list': """
            <a class="list-group-item" href="{{ site_url}}/{{ article_url}}">
            <div class="row">
            <div class="col-md-12 col-sm-12"><h4 class="list-group-item-heading">{{article_title}}</h4></div>
            <div class="col-md-12 col-sm-12"><p class="list-group-item-text text-muted">{{article_category}} {{article_date}}</p></div>
            </div>
            </a>
        """},
    'category': None,
    'count': 4,
    'show': False,
    'minified': True,
    'generate_minified': True,
    'show-categories': False,
    'shorten-category-label': True,
    'category-label-css': {},
    'site-url': '',
    'template-variable': False,
    'articles': None
}

bnews_settings = copy.deepcopy(bnews_default_settings)


def get_attribute(attrs, name, default=None):
    """
    Get div attribute
    :param attrs: attribute dict
    :param name: name field
    :param default: default value
    :return: value
    """

    if 'data-'+name in attrs:
        return attrs['data-'+name]
    else:
        return default


def generate_listing(settings):
    count = 0
    html = "\n"
    for article_id, article in enumerate(settings['articles']):
        if count < bnews_settings['count']:
            if settings['category']:
                if article.category.name in settings['category']:
                    html += generate_item(article=article, settings=settings) + "\n"
                    count += 1
            else:
                html += generate_item(article=article, settings=settings) + "\n"
                count += 1
        else:
            break
    html += "\n"

    template = Template(settings['template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    div_html = BeautifulSoup(template.render(news_list=html,
                                             header=settings['header'],
                                             site_url=settings['site-url'],
                                             headerlink=settings['header-link'],
                                             panel_color=settings['panel-color']), "html.parser")
    return div_html


def generate_item(article, settings):
    current_datetime = datetime.datetime.now()
    article_datetime = datetime.datetime(year=article.date.year, day=article.date.day, month=article.date.month)

    date_label = format_timedelta(current_datetime - article_datetime, format='medium', locale='en') + ' ago'

    if settings['show-categories']:
        if article.category.name.lower() in settings['category-label-css']:
            category_label = '<span class="'+settings['category-label-css'][article.category.name.lower()]['label-css']+'">'
        else:
            category_label = '<span class="label label-default">'
        if settings['shorten-category-label']:
            category_label += article.category.name[:1].upper()
        else:
            category_label += article.category.name
        category_label += '</span>'
    else:
        category_label = ''

    template = Template(settings['item-template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    html = BeautifulSoup(template.render(site_url=settings['site-url'],
                                         article_url=article.url,
                                         article_title=article.title,
                                         article_date=date_label,
                                         article_category=category_label,
                                         ), "html.parser")

    return html.decode()


def bnews(content):
    """
    Main processing

    """

    if isinstance(content, contents.Static):
        return

    soup = BeautifulSoup(content._content, 'html.parser')

    if bnews_settings['template-variable']:
        # We have page variable set
        bnews_settings['show'] = True
        div_html = generate_listing(settings=bnews_settings)
        content.bnews = div_html.decode()

    else:
        content.bnews = None

    bnews_divs = soup.find_all('div', class_='bnews')

    if bnews_divs:
        # We have divs in the page
        bnews_settings['show'] = True
        for bnews_div in bnews_divs:
            settings = copy.deepcopy(bnews_settings)
            settings['mode'] = get_attribute(bnews_div.attrs, 'mode', bnews_settings['mode'])
            settings['header'] = get_attribute(bnews_div.attrs, 'header', bnews_settings['header'])
            settings['header-link'] = get_attribute(bnews_div.attrs, 'header-link', bnews_settings['header-link'])
            settings['category'] = get_attribute(bnews_div.attrs, 'category', bnews_settings['category'])
            if settings['category']:
                settings['category'] = bnews_settings['category'].split(',')
            settings['count'] = get_attribute(bnews_div.attrs, 'count', bnews_settings['count'])
            if settings['count']:
                settings['count'] = int(settings['count'])

            settings['panel-color'] = get_attribute(bnews_div.attrs, 'panel-color', bnews_settings['panel-color'])
            settings['show-categories'] = get_attribute(bnews_div.attrs, 'show-categories', bnews_settings['show-categories']) == 'True'

            div_html = generate_listing(settings=settings)
            bnews_div.replaceWith(div_html)

    if bnews_settings['show']:

        if bnews_settings['minified']:
            html_elements = {
                'css_include': [
                    '<link rel="stylesheet" href="' + bnews_settings['site-url'] + '/theme/css/bnews.min.css">'
                ]
            }
        else:
            html_elements = {
                'css_include': [
                    '<link rel="stylesheet" href="' + bnews_settings['site-url'] + '/theme/css/bnews.css">'
                ]
            }

        if u'styles' not in content.metadata:
            content.metadata[u'styles'] = []
        for element in html_elements['css_include']:
            if element not in content.metadata[u'styles']:
                content.metadata[u'styles'].append(element)

    content._content = soup.decode()


def process_page_metadata(generator, metadata):
    """
    Process page metadata and assign css

    """

    global bnews_default_settings, bnews_settings

    # Inject article listing
    article_listing = bnews_settings['articles']
    bnews_settings = copy.deepcopy(bnews_default_settings)
    bnews_settings['articles'] = article_listing

    if u'styles' not in metadata:
        metadata[u'styles'] = []

    if u'bnews' in metadata and (metadata['bnews'] == 'True' or metadata['bnews'] == 'true'):
        bnews_settings['show'] = True
        bnews_settings['template-variable'] = True
    else:
        bnews_settings['show'] = False
        bnews_settings['template-variable'] = False

    if u'bnews_mode' in metadata:
        bnews_settings['mode'] = metadata['bnews_mode']

    if u'bnews_panel_color' in metadata:
        bnews_settings['panel-color'] = metadata['bnews_panel_color']

    if u'bnews_header' in metadata:
        bnews_settings['header'] = metadata['bnews_header']

    if u'bnews_header_link' in metadata:
        bnews_settings['header-link'] = metadata['bnews_header_link']

    if u'bnews_count' in metadata:
        bnews_settings['count'] = int(metadata['bnews_count'])

    if u'bnews_category' in metadata:
        bnews_settings['category'] = metadata['bnews_category']

    if u'bnews_show_categories' in metadata:
        bnews_settings['show-categories'] = metadata['bnews_show_categories']


def move_resources(gen):
    """
    Move files from css folders to output folder, use minified files.

    """

    plugin_paths = gen.settings['PLUGIN_PATHS']
    if bnews_settings['minified']:
        if bnews_settings['generate_minified']:
            minify_css_directory(gen=gen, source='css', target='css.min')

        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bnews.min.css')
        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-bnews', 'css.min', 'bnews.min.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break
    else:
        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bnews.css')
        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        for path in plugin_paths:
            print path
            css_source = os.path.join(path, 'pelican-bnews', 'css', 'bnews.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break


def minify_css_directory(gen, source, target):
    """
    Move CSS resources from source directory to target directory and minify. Using rcssmin.

    """

    import rcssmin

    plugin_paths = gen.settings['PLUGIN_PATHS']
    for path in plugin_paths:
        source_ = os.path.join(path, 'pelican-bnews', source)
        target_ = os.path.join(path, 'pelican-bnews', target)
        if os.path.isdir(source_):
            if not os.path.exists(target_):
                os.makedirs(target_)

            for root, dirs, files in os.walk(source_):
                for current_file in files:
                    if current_file.endswith(".css"):
                        current_file_path = os.path.join(root, current_file)
                        with open(current_file_path) as css_file:
                            with open(os.path.join(target_, current_file.replace('.css', '.min.css')), "w") as minified_file:
                                minified_file.write(rcssmin.cssmin(css_file.read(), keep_bang_comments=True))


def get_articles(generator):
    """
    Fetch article listing

    """

    bnews_settings['articles'] = generator.articles
    move_resources(generator)


def init_default_config(pelican):
    """
    Handle settings from pelicanconf.py

    """

    global bnews_default_settings, bnews_settings

    bnews_default_settings['site-url'] = pelican.settings['SITEURL']
    if 'BNEWS_HEADER' in pelican.settings:
        bnews_default_settings['header'] = pelican.settings['BNEWS_HEADER']

    if 'BNEWS_TEMPLATE' in pelican.settings:
        bnews_default_settings['template'].update(pelican.settings['BNEWS_TEMPLATE'])

    if 'BNEWS_ITEM_TEMPLATE' in pelican.settings:
        bnews_default_settings['item-template'].update(pelican.settings['BNEWS_ITEM_TEMPLATE'])

    if 'BNEWS_PANEL_COLOR' in pelican.settings:
        bnews_default_settings['panel-color'] = pelican.settings['BNEWS_PANEL_COLOR']

    if 'BNEWS_CATEGORY_LABEL_CSS' in pelican.settings:
        bnews_default_settings['category-label-css'] = pelican.settings['BNEWS_CATEGORY_LABEL_CSS']

    if 'BNEWS_MINIFIED' in pelican.settings:
        bnews_default_settings['minified'] = pelican.settings['BNEWS_MINIFIED']

    if 'BNEWS_GENERATE_MINIFIED' in pelican.settings:
        bnews_default_settings['generate_minified'] = pelican.settings['BNEWS_GENERATE_MINIFIED']

    bnews_settings = copy.deepcopy(bnews_default_settings)


def register():
    """
    Register signals

    """

    signals.initialized.connect(init_default_config)
    signals.article_generator_context.connect(process_page_metadata)
    signals.page_generator_context.connect(process_page_metadata)
    signals.article_generator_finalized.connect(get_articles)

    signals.content_object_init.connect(bnews)

