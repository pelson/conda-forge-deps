import os
import tornado.ioloop
import tornado.web


class ImgHandler(tornado.web.RequestHandler):
  def get(self, package):
    self.set_header("Content-Type", "image/svg+xml")
    import deps_plot
    svg_content = '\n'.join(deps_plot.svg_content(package))
    self.write(svg_content)


application = tornado.web.Application(
    [
      (r"/img/(.*)", ImgHandler),
    ],
    debug=True
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
