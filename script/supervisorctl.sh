supervisord -c script/supervisord.conf
supervisorctl -u sqlreview -p sqlreview.themis reload
supervisorctl -u sqlreview -p sqlreview.themis