Pelican-bnews - Automatic generation of most recent news article list for Pelican
===================================================================================

`pelican-bnews` is an open source Pelican plugin to produce list of most recent articles for content page. The plugin is developed to be used with Markdown content and Bootstrap 3 based template. 

**Author**

Toni Heittola (toni.heittola@gmail.com), [GitHub](https://github.com/toni-heittola), [Home page](http://www.cs.tut.fi/~heittolt/)

Installation instructions
=========================

## Requirements

**bs4** is required. To ensure that all external modules are installed, run:

    pip install -r requirements.txt

**bs4** (BeautifulSoup) for parsing HTML content

    pip install beautifulsoup4

In order to regenerate minified CSS and JS files you need also: 

**rcssmin** a CSS Minifier

    pip install rcssmin
    
**jsmin** a JS Minifier

    pip install jsmin

## Pelican installation

Make sure you include [Bootstrap](http://getbootstrap.com/) in your template.

Make sure the directory where the plugin was installed is set in `pelicanconf.py`. For example if you installed in `plugins/pelican-bnews`, add:

    PLUGIN_PATHS = ['plugins']

Enable `pelican-bnews` with:

    PLUGINS = ['pelican-bnews']

To allow plugin in include css file, one needs to add following to the `base.html` template, in the head :

    {% if article %}
        {% if article.styles %}
            {% for style in article.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}
    {% if page %}
        {% if page.styles %}
            {% for style in page.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}

Insert article listing in the page template:
 
    {% if page.bnews %}
        {{ page.bnews }}
    {% endif %}

Insert article listing in the article template:

    {% if article.bnews %}
        {{ article.bnews }}
    {% endif %}

Usage
=====

Article listing generation is triggered for the page either by setting BNEWS metadata for the content (page or article) or using `<div>` with class `bnews`. 

There is two layout modes available for both of these: `panel` and `list`. 

Optionally article entries can be replaced with micro news read from yaml-file (use `bnews-micro` divs and `data-source` parameter). Micro news is intended for minimal news where only summary is shown and usually associated url lead to external site.   

## Parameters

The parameters can be set in global, and content level. Globally set parameters are are first overwritten content meta data, and finally with div parameters.

### Global parameters

Parameters for the plugin can be set in `pelicanconf.py' with following parameters:

| Parameter                 | Type      | Default       | Description  |
|---------------------------|-----------|---------------|--------------|
| BNEWS_HEADER              | String    | Content       | Header text  |
| BNEWS_HEADER_LINK         | String    | news         | Header link  |
| BNEWS_TEMPLATE            | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BNEWS_ITEM_TEMPLATE       | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BNEWS_PANEL_COLOR         | String    | panel-primary |  CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BNEWS_CATEGORY_LABEL_CSS  | Dict      |               | Dict with category labels as keys, second level dict with key`label-css`. |
| BNEWS_MINIFIED           | Boolean   | True          | Do we use minified CSS file. Disable in case of debugging.  |
| BNEWS_GENERATE_MINIFIED  | Boolean   | False         | CSS file is minified each time, Enable in case of development.   |

### Content wise parameters

| Parameter                 | Example value | Description  |
|---------------------------|---------------|--------------|
| BNEWS                     | True          | Enable article listing for the page | 
| BNEWS_MODE                | panel         | Layout type, panel or list |
| BNEWS_PANEL_COLOR         | panel-info    | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BNEWS_HEADER              | News          | Header text  |
| BNEWS_HEADER_LINK         | /news         | Header link |
| BNEWS_COUNT               | 3             | Count of most recent articles shown |
| BNEWS_CATEGORY            | cat1, cat2    | Show only articles from specified categories (comma separated), if empty all categories shown |
| BNEWS_SHOW_CATEGORIES     | True          | Show category label |

Example:

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bnews: True
    bnews_header: Recent news
    bnews_category: cat1, cat2
    bnews_count: 5
    
Article listing is available in template in variable `page.bnews` or `article.bnews`
   
### Div wise parameters

| Parameter                 | Example value     | Description  |
|---------------------------|-------------|--------------|
| data-mode                 | panel       | Layout type, panel or list |
| data-header               | Dates       | Header text |
| data-header-link          | /news       | Header link |
| data-category             | cat1, cat2 | Show only articles from specified categories (comma separated), if empty all categories shown |
| data-count                | 2 | Count of most recent articles shown |
| data-show-categories      | True | Show category label |
| data-show-summary         | False | Show news summary, use summary meta label | 
| data-panel-color          | panel-info | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| data-source               | None | Source to the micro news data file in yaml format. Used only with `bnews-micro` divs |
| data-shorten-category-label | True | Shorten category label into single letter | 

Example listing:

    <div class="bnews" data-category="category1" data-mode="list" data-header="Recent News" data-show-summary="True"></div>

Example with meta fields:     

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bnews: True
    bnews_category: category1
    bnews_header: Recent News
    bnews_panel_color: panel-default   
    bnews_mode: panel    
    <div class="bnews"></div>
    
   
Example micro news listing:

    <div class="bnews-micro" source="content/data/micro_news.yaml" data-category="category1" data-mode="list" data-header="Recent News" data-show-summary="True"></div>
        
        
Source file:

    - title: Test title1
      date: 2016-03-03 12:00:00
      summary: Some text
      url: http://www.foo.bar.com
      category: category1
    
    - title: Test title2
      date: 2016-07-03 12:00:00
      summary: Some text
      url: http://www.foo.bar.com
      category: category1      
        
