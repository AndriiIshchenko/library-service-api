# library-service-api

docker run -d -p 6379:6379 redis
celery -A library_service worker --loglevel=INFO

celery -A library_service beat -l info --logfile=celery.beat.log --detach  
celery -A library_service worker -l info --logfile=celery.log --detach
pkill -f 'celery'