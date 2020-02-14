import json


additionalHead = r'''
  <link rel="stylesheet" href="/assets/css/styles.css">
  <link rel="stylesheet" href="/assets/css/colorful.css">
  <link rel="stylesheet" href="/assets/css/colorbox.css">
  <link rel="stylesheet" href="/assets/css/button.css">
  <link rel="stylesheet" href="/assets/css/pseudocode.min.css">
  '''

config = {
    'ip' : '127.0.0.1',
    'port' : 8088,
    'base_dir' : '~/website_jekyll_folder/_site',
    'additional_head' : additionalHead
}


with open('_config.json', 'w') as outfile:
    json.dump(config, outfile, indent='  ')