# -*- coding:utf-8 -*-

__all__ = [
    "generate",
]


def generate(input_path, output_path=None, in_memory=False):
    """Executes the Statik site generator using the given parameters.
    """
    return {
        "index.html": """<!DOCTYPE html>
<html>
<head>
<title>Welcome to the test blog</title>
</head>
<body>
<h1>Home page</h1>
<ul>
    <li><a href="/2016/06/15/my-first-post/">My first post</a></li>
</ul>
</body>
</html>""",
        "2016": {
            "06": {
                "15": {
                    "my-first-post": {
                        "index.html": """<!DOCTYPE html>
<html>
<head>
  <title>My first post</title>
</head>
<body>
  <h1>My first post</h1>
  <div class="meta">
    <div class="published">
      2016-06-15
    </div>
    <div class="author">
      <a href="/bios/michael/">By Michael</a>
    </div>
  </div>
  <div class="content">
    This is the <strong>Markdown</strong> content of the first post, which should appropriately
    be translated into the relevant <code>HTML</code> code.
  </div>
</body>
</html>
""",
                    }
                }
            }
        },
        "bios": {
            "michael": {
                "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Michael Anderson</title>
</head>
<body>
    <h1>Michael Anderson</h1>
    <div class="meta">
        <a href="mailto:manderson@somewhere.com">Contact Michael</a>
    </div>
    <div class="content">
        This is Michael's bio, in <strong>Markdown</strong> format.
    </div>
</body>
</html>
"""
            }
        }
    }
