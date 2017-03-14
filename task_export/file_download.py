# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import os


"""
一个简单的文件下载服务器，用来下载生成的报告，默认监听9000端口
"""

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument("filename", None)
        if not filename:
            self.write("file name not empty")
            return
        filename = filename + ".tar.gz"
        if filename not in os.listdir('task_export/downloads'):
            self.write("file not find, please waiting for")
            return
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header(
            'Content-Disposition', 'attachment; filename=sqlreview.tar.gz')
        buf_size = 4096
        filename = "task_export/downloads/" + filename
        with open(filename, 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write(data)
        self.finish()

application = tornado.web.Application([
    (r"/download", MainHandler),
])

if __name__ == "__main__":
    application.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
