import asyncio
from flask import Flask, render_template
from playwright.async_api import async_playwright
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    link_url = db.Column(db.String(255), unique=True)
    link_title = db.Column(db.String(255))
    link_image_url = db.Column(db.String(255))

async def parse_telegram_group(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.set_default_timeout(60000)
        await page.goto(url)
        posts = await page.query_selector_all('.tgme_widget_message_bubble')
        parsed_posts = []
        for post_element in posts:
            link_preview = await post_element.query_selector('.tgme_widget_message_link_preview')
            if link_preview:
                link_url = await link_preview.get_attribute('href')
                if 'telegra.ph' in link_url and not Post.query.filter_by(link_url=link_url).first():
                    new_page = await browser.new_page()
                    await new_page.goto(link_url)
                    title_element = await new_page.query_selector('.tl_article_header h1')
                    title = await title_element.inner_text() if title_element else ''
                    image_element = await new_page.query_selector('.figure_wrapper img')
                    image_url = await image_element.get_attribute('src') if image_element else ''
                    text = await new_page.evaluate('(document.querySelector(".tl_article_content") || document.body).innerText')
                    truncated_text = text[:280] + '...' if len(text) > 280 else text
                    parsed_post = {
                        'text': truncated_text.strip(),
                        'link_url': link_url,
                        'link_title': title.strip(),
                        'link_image_url': image_url
                    }
                    parsed_posts.append(parsed_post)
                    db_post = Post(text=parsed_post['text'], link_url=parsed_post['link_url'], link_title=parsed_post['link_title'], link_image_url=parsed_post['link_image_url'])
                    db.session.add(db_post)
                    db.session.commit()
                    await new_page.close()
        await browser.close()
        return parsed_posts

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        asyncio.run(parse_telegram_group("https://t.me/s/drc_think_tank"))
    app.run(debug=True)
