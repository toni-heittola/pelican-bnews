# -*- coding: utf-8 -*-
"""
Recent news article list -- BNEWS
=================================
Author: Toni Heittola (toni.heittola@gmail.com)

"""

from builtins import str
import os
import shutil
import logging
import copy
import yaml
import time
import collections
from bs4 import BeautifulSoup
from jinja2 import Template
from pelican import signals, contents
import datetime
from babel.dates import format_timedelta

logger = logging.getLogger(__name__)
__version__ = '0.1.0'

bnews_default_settings = {
    'header': 'News',
    'header-link': 'news',
    'panel-color': 'panel-default',
    'mode': 'panel',
    'template': {
        'panel': """
            <div class="panel {{ panel_color }} hidden-print">
              <div class="panel-heading">
                <h3 class="panel-title"><a href="{{ site_url }}/{{header_link}}">{{header}}</a></h3>
              </div>
              <ul class="bnews-container list-group">
              {{news_list}}
              </ul>
            </div>
        """,
        'list': """
            <h3 class="section-heading text-center"><a href="{{ site_url }}/{{header_link}}">{{header}}</a></h3>
            <div class="list-group bnews-container">
            {{news_list}}
            </div>
        """},
    'item-template': {
        'panel': """
            <a class="list-group-item" href="{{ article_url}}" target="{{ article_url_target }}">
            <div class="row">
                <div class="col-md-12 col-sm-12"><h5 class="list-group-item-heading">{{article_title}}</h5></div>
                <div class="col-md-12 col-sm-12">
                <p class="list-group-item-text text-muted">{{article_category}}
                {% if article_date %}<small><span class="bnews-time" datetime="{{article_date}}"></span><small>{% endif %}
                </p>
                </div>
            </div>
            </a>
        """,
        'list': """
            <a class="list-group-item" href="{{ article_url}}" target="{{ article_url_target }}">
            <div class="row">
                <div class="col-md-12 col-sm-12">
                    <h4 class="list-group-item-heading">
                    {% if article_date and not article_category%}
                    <span class="bnews-time pull-right text-muted" datetime="{{article_date}}"></span>
                    {% endif %}
                    {{article_title}}
                    </h4>
                </div>
                <div class="col-md-12 col-sm-12">
                <p class="list-group-item-text text-muted">
                {{article_category}}
                {% if article_category and article_date %}
                <span class="bnews-time pull-right" datetime="{{article_date}}"></span>
                {% endif %}
                </p>
                </div>
                {% if article_summary %}
                <div class="col-md-12 col-sm-12 bnews-summary">{{article_summary}}</div>
                {% endif %}
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
    'show-summary': False,
    'site-url': '',
    'template-variable': False,
    'articles': None,
    'debug_processing': False
}

bnews_settings = copy.deepcopy(bnews_default_settings)


def boolean(value):
    """Conversion for yes/no True/False."""
    if isinstance(value, str):
        if value.lower() in ['yes', 'true', '1', u'yes', u'true', u'1']:
            return True

        else:
            return False

    elif isinstance(value, bool):
        return value

    else:
        return None


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
        if count < settings['count']:
            if settings['category']:
                if hasattr(article, 'category'):
                    category = article.category.name

                elif 'category' in article:
                    category = article['category']

                if category in settings['category']:
                    html += generate_item(
                        article=article,
                        settings=settings
                    ) + "\n"

                    count += 1

            else:
                html += generate_item(
                    article=article,
                    settings=settings
                ) + "\n"

                count += 1

        else:
            break

    html += "\n"

    if count:
        template = Template(settings['template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
        div_html = BeautifulSoup(template.render(
            news_list=html,
            header=settings['header'],
            site_url=settings['site-url'],
            header_link=settings['header-link'],
            panel_color=settings['panel-color']), "html.parser"
        )

        return div_html
    else:
        return ''


def generate_item(article, settings):
    if hasattr(article, 'date'):
        article_datetime = datetime.datetime(
            year=article.date.year,
            day=article.date.day,
            month=article.date.month,
            hour=article.date.hour,
            minute=article.date.minute
        )
    else:
        article_datetime = article['date']

    if settings['show-categories']:
        if hasattr(article, 'category'):
            label = article.category.name

        elif 'category' in article:
            label = article['category']

        if label.lower() in settings['category-label-css']:
            article_category = '<span class="'+settings['category-label-css'][label.lower()]['label-css']+'">'

        else:
            article_category = '<span class="label label-default">'

        if settings['shorten-category-label']:
            article_category += label[:1].upper()

        else:
            article_category += label

        article_category += '</span>'

    else:
        article_category = ''

    if settings['show-summary']:
        if hasattr(article, 'summary'):
            article_summary = article.summary

        elif 'summary' in article:
            article_summary = article['summary']

    else:
        article_summary = None

    if hasattr(article, 'url'):
        article_url = article.url

    elif 'url' in article:
        article_url = article['url']

    else:
        article_url = 'javascript:void(0)'

    if 'javascript' in article_url:
        article_url_target = '_self'

    elif 'http://' in article_url:
        article_url_target = '_blank'

    else:
        article_url = settings['site-url'] + '/' + article_url
        article_url_target = '_self'

    if hasattr(article, 'title'):
        article_title = article.title

    elif 'title' in article:
        article_title = article['title']

    else:
        article_title = None

    template = Template(settings['item-template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    html = BeautifulSoup(template.render(
        site_url=settings['site-url'],
        article_url=article_url,
        article_url_target=article_url_target,
        article_title=article_title,
        article_date=article_datetime,
        article_category=article_category,
        article_summary=article_summary
    ), "html.parser")

    return html.decode()


def load_micro_news(source):

    if source and os.path.isfile(source):
        try:
            with open(source, 'r') as field:
                micro_news_registry = yaml.load(field)

            if 'data' in micro_news_registry:
                micro_news_registry = micro_news_registry['data']

            # Sort based on date
            micro_news_registry = sorted(micro_news_registry, key=lambda d: d['date'], reverse=True)

            return micro_news_registry

        except ValueError:
            logger.warn('`pelican-bnews` failed to load file [' + str(source) + ']')
            return False

    else:
        logger.warn('`pelican-bnews` failed to load file [' + str(source) + ']')
        return False


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
    bnews_micro_divs = soup.find_all('div', class_='bnews-micro')

    if bnews_divs:
        if bnews_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='bnews',
                title=content.title,
                div_count=len(bnews_divs)
            ))

        # We have divs
        bnews_settings['show'] = True
        for bnews_div in bnews_divs:
            settings = copy.deepcopy(bnews_settings)
            settings['mode'] = get_attribute(bnews_div.attrs, 'mode', bnews_settings['mode'])
            settings['header'] = get_attribute(bnews_div.attrs, 'header', bnews_settings['header'])
            settings['header-link'] = get_attribute(bnews_div.attrs, 'header-link', bnews_settings['header-link'])
            settings['category'] = get_attribute(bnews_div.attrs, 'category', bnews_settings['category'])

            if settings['category']:
                settings['category'] = settings['category'].split(',')

            settings['shorten-category-label'] = boolean(
                get_attribute(bnews_div.attrs, 'shorten-category-label', bnews_settings['shorten-category-label'])
            )

            settings['count'] = get_attribute(bnews_div.attrs, 'count', bnews_settings['count'])
            if settings['count']:
                settings['count'] = int(settings['count'])

            settings['panel-color'] = get_attribute(bnews_div.attrs, 'panel-color', bnews_settings['panel-color'])
            settings['show-categories'] = get_attribute(bnews_div.attrs, 'show-categories', bnews_settings['show-categories']) == 'True'
            settings['show-summary'] = get_attribute(bnews_div.attrs, 'show-summary', bnews_settings['show-summary']) == 'True'

            div_html = generate_listing(settings=settings)
            bnews_div.replaceWith(div_html)

    if bnews_micro_divs:
        if bnews_settings['debug_processing']:
            logger.debug(msg='[{plugin_name}] title:[{title}] divs:[{div_count}]'.format(
                plugin_name='bnews-micro',
                title=content.title,
                div_count=len(bnews_micro_divs)
            ))

        # We have divs for micro news
        bnews_settings['show'] = True
        for bnews_micro_div in bnews_micro_divs:
            settings = copy.deepcopy(bnews_settings)
            settings['data_source'] = get_attribute(bnews_micro_div.attrs, 'source', None)
            settings['mode'] = get_attribute(bnews_micro_div.attrs, 'mode', bnews_settings['mode'])
            settings['header'] = get_attribute(bnews_micro_div.attrs, 'header', bnews_settings['header'])
            settings['header-link'] = get_attribute(bnews_micro_div.attrs, 'header-link', bnews_settings['header-link'])
            settings['category'] = get_attribute(bnews_micro_div.attrs, 'category', bnews_settings['category'])

            if settings['category']:
                settings['category'] = settings['category'].split(',')

            settings['shorten-category-label'] = boolean(
                get_attribute(bnews_micro_div.attrs, 'shorten-category-label', bnews_settings['shorten-category-label'])
            )

            settings['count'] = get_attribute(bnews_micro_div.attrs, 'count', bnews_settings['count'])
            if settings['count']:
                settings['count'] = int(settings['count'])

            settings['panel-color'] = get_attribute(bnews_micro_div.attrs, 'panel-color', bnews_settings['panel-color'])
            settings['show-categories'] = get_attribute(bnews_micro_div.attrs, 'show-categories', bnews_settings['show-categories']) == 'True'
            settings['show-summary'] = get_attribute(bnews_micro_div.attrs, 'show-summary', bnews_settings['show-summary']) == 'True'

            settings['articles'] = load_micro_news(settings['data_source'])

            div_html = generate_listing(settings=settings)
            bnews_micro_div.replaceWith(div_html)

    if bnews_settings['show']:

        if bnews_settings['minified']:
            html_elements = {
                'js_include': [
                    '<script type="text/javascript" src="' + bnews_settings['site-url'] + '/theme/js/timeago.min.js"></script>',
                    '<script type="text/javascript" src="' + bnews_settings['site-url'] + '/theme/js/bnews.min.js"></script>'
                ],
                'css_include': [
                    '<link rel="stylesheet" href="' + bnews_settings['site-url'] + '/theme/css/bnews.min.css">'
                ]
            }

        else:
            html_elements = {
                'js_include': [
                    '<script type="text/javascript" src="' + bnews_settings['site-url'] + '/theme/js/timeago.js"></script>',
                    '<script type="text/javascript" src="' + bnews_settings['site-url'] + '/theme/js/bnews.js"></script>',
                ],
                'css_include': [
                    '<link rel="stylesheet" href="' + bnews_settings['site-url'] + '/theme/css/bnews.css">'
                ]
            }

        if u'styles' not in content.metadata:
            content.metadata[u'styles'] = []

        for element in html_elements['js_include']:
            if element not in content.metadata[u'scripts']:
                content.metadata[u'scripts'].append(element)

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

    if u'bnews_show_summary' in metadata:
        bnews_settings['show-summary'] = metadata['bnews_show_summary']


def move_resources(gen):
    """
    Move files from css folders to output folder, use minified files.

    """

    plugin_paths = gen.settings['PLUGIN_PATHS']
    if bnews_settings['minified']:
        if bnews_settings['generate_minified']:
            minify_css_directory(gen=gen, source='css', target='css.min')
            minify_js_directory(gen=gen, source='js', target='js.min')

        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bnews.min.css')

        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        js_target_1 = os.path.join(gen.output_path, 'theme', 'js', 'timeago.min.js')
        js_target_2 = os.path.join(gen.output_path, 'theme', 'js', 'bnews.min.js')

        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'js')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'js'))

        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-bnews', 'css.min', 'bnews.min.css')
            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            js_source_1 = os.path.join(path, 'pelican-bnews', 'js.min', 'timeago.min.js')
            js_source_2 = os.path.join(path, 'pelican-bnews', 'js.min', 'bnews.min.js')

            if os.path.isfile(js_source_1):
                shutil.copyfile(js_source_1, js_target_1)

            if os.path.isfile(js_source_2):
                shutil.copyfile(js_source_2, js_target_2)

            if os.path.isfile(css_target) and os.path.isfile(js_target_1) and os.path.isfile(js_target_2):
                break
    else:
        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bnews.css')

        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        js_target_1 = os.path.join(gen.output_path, 'theme', 'js', 'timeago.js')
        js_target_2 = os.path.join(gen.output_path, 'theme', 'js', 'bnews.js')
        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-bnews', 'css', 'bnews.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            js_source_1 = os.path.join(path, 'pelican-bnews', 'js', 'timeago.js')
            js_source_2 = os.path.join(path, 'pelican-bnews', 'js', 'bnews.js')

            if os.path.isfile(js_source_1):
                shutil.copyfile(js_source_1, js_target_1)

            if os.path.isfile(js_source_2):
                shutil.copyfile(js_source_2, js_target_2)

            if os.path.isfile(css_target) and os.path.isfile(js_target_1) and os.path.isfile(js_target_2):
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


def minify_js_directory(gen, source, target):
    """
    Move JS resources from source directory to target directory and minify.

    """

    from jsmin import jsmin

    plugin_paths = gen.settings['PLUGIN_PATHS']
    for path in plugin_paths:
        source_ = os.path.join(path, 'pelican-bnews', source)
        target_ = os.path.join(path, 'pelican-bnews', target)

        if os.path.isdir(source_):
            if not os.path.exists(target_):
                os.makedirs(target_)

            for root, dirs, files in os.walk(source_):
                for current_file in files:
                    if current_file.endswith(".js"):
                        current_file_path = os.path.join(root, current_file)
                        with open(current_file_path) as js_file:
                            with open(os.path.join(target_, current_file.replace('.js', '.min.js')), "w") as minified_file:
                                minified_file.write(jsmin(js_file.read()))


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

    if 'BNEWS_HEADER_LINK' in pelican.settings:
        bnews_default_settings['header-link'] = pelican.settings['BNEWS_HEADER_LINK']

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

    if 'BNEWS_DEBUG_PROCESSING' in pelican.settings:
        bnews_default_settings['debug_processing'] = pelican.settings['BNEWS_DEBUG_PROCESSING']

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

