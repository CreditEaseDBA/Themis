# -*-coding:utf-8-*-

import os
import tornado.ioloop
import tornado.autoreload

from webui import view


def run_server(config, host=None, port=7000):
    handlers = [
        (r"/", view.SqlReRuleSetIndex),
        (r"/sqlreview/rule/simple/addition", view.RuleSimpleAdditoin),
        (r"/sqlreview/rule/complex/addition", view.RuleComplexAddition),
        (r"/sqlreview/rule/addition", view.RuleAddition),
        (r"/new/version/sql/review/rule/info/index", view.SqlReRuleSetInfoIndex),
        (r"/sqlreview/rule/upload", view.RuleUpload),
        (r"/sqlreview/rule/info", view.SqlReviewRuleInfo),
        (r"/new/version/sql/review/get/struct", view.SqlReviewGetStruct),
        (r"/new/version/sql/review/task/index", view.SqlReviewTaskIndex),
        (r"/new/version/sql/review/job/data", view.SqlReviewJobData),
        (r"/new/version/sql/review/task/rule/info", view.SqlReviewTaskRuleInfo),
        (r"/new/version/sql/review/task/rule/detail/info", view.SqlReviewTaskRuleDetailInfo),
        (r"/new/version/sql/review/task/rule/plan/info", view.SqlReviewTaskRulePlanInfo),
        (r"/new/version/sql/review/task/rule/text/info", view.SqlReviewTaskRuleTextInfo),
        # (r"/new/version/sql/review/prevent/object/index", view.SqlReviewPreventObjectIndex),
        # (r"/new/version/sql/review/prevent/object", view.SqlReviewPreventObject),
        (r"/new/version/sql/review/get/db/user/list", view.SqlReviewGetDbUserList),
        (r"/new/version/sql/review/get/db/port", view.SqlReviewGetDbPort),
        (r"/new/version/sql/review/task/publish", view.SqlReviewTaskPublish),
        (r"/new/version/sql/review/task/rule/export", view.SqlReviewRuleExport)
    ]
    application = tornado.web.Application(handlers,
                template_path=os.path.join(os.path.dirname(__file__), "template"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                debug=True,
                config=config
            )
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    application.listen(server_port)
    tornado.ioloop.IOLoop.instance().start()
